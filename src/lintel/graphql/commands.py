"""Bind declared commands and read-only outcome observation to the execution port."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Literal, cast

from graphql import GraphQLError, GraphQLObjectType, GraphQLResolveInfo, GraphQLSchema

from lintel.ports import (
    CommandResult,
    ElementRef,
    ExecutionError,
    ExecutionErrorCode,
    NodeKey,
    OperationRef,
    RequestSession,
)


@dataclass(frozen=True, slots=True)
class CommandParameter:
    name: str
    scalar: Literal["string", "boolean", "decimal", "key"]
    key_record: ElementRef | None = None


@dataclass(frozen=True, slots=True)
class CommandBinding:
    name: str
    operation: OperationRef
    parameters: tuple[CommandParameter, ...]

    @property
    def observation_name(self) -> str:
        return "observe" + self.name[0].upper() + self.name[1:]


Outcome = dict[str, object]
ResolveInfo = GraphQLResolveInfo[dict[str, object]]
DecodeKey = Callable[[str], NodeKey | None]
EncodeKey = Callable[[NodeKey], str]


def install_command_resolvers(
    schema: GraphQLSchema,
    command: CommandBinding,
    decode_key: DecodeKey,
    encode_key: EncodeKey,
) -> None:
    """Bind one command after artifact admission has verified its schema and metadata."""
    mutation, query = schema.mutation_type, schema.query_type
    if not isinstance(mutation, GraphQLObjectType) or not isinstance(query, GraphQLObjectType):
        raise ValueError("API_MISMATCH")
    if command.name not in mutation.fields or command.observation_name not in query.fields:
        raise ValueError("API_MISMATCH")
    mutation.fields[command.name].resolve = _resolver(command, decode_key, encode_key, False)
    query.fields[command.observation_name].resolve = _resolver(
        command, decode_key, encode_key, True
    )


def _resolver(
    command: CommandBinding,
    decode_key: DecodeKey,
    encode_key: EncodeKey,
    observe: bool,
) -> Callable[[object, ResolveInfo, Mapping[str, object]], Awaitable[Outcome]]:
    async def resolve(_root: object, info: ResolveInfo, input: Mapping[str, object]) -> Outcome:
        invocation_key = cast(str, input["invocationKey"])
        try:
            check_control(invocation_key, 128)
            confirmation = cast(str | None, input.get("confirmation"))
            if confirmation is not None:
                check_control(confirmation, 2048)
            arguments = {
                param.name: command_argument(param, input[param.name], decode_key)
                for param in command.parameters
                if param.name in input
            }
            session = cast(RequestSession, info.context["session"])
            semaphore = cast(asyncio.Semaphore, info.context["dispatch_semaphore"])
            async with semaphore:
                result = (
                    await session.observe(command.operation, arguments, invocation_key)
                    if observe
                    else await session.invoke(
                        command.operation, arguments, invocation_key, confirmation
                    )
                )
        except ExecutionError as error:
            return rejected_command(invocation_key, error)
        try:
            return command_outcome(result, invocation_key, encode_key, observe)
        except ExecutionError:
            return _unavailable(invocation_key, observe)

    return resolve


def check_control(value: str, max_bytes: int) -> None:
    try:
        size = len(value.encode("utf-8"))
    except UnicodeEncodeError as error:
        raise ExecutionError("INVALID") from error
    if not 0 < size <= max_bytes or "\x00" in value:
        raise ExecutionError("INVALID")


def command_argument(
    parameter: CommandParameter, value: object, decode_key: DecodeKey
) -> Mapping[str, object] | NodeKey | None:
    if value is None:
        return None
    if parameter.scalar == "key" and type(value) is str:
        key = decode_key(value)
        if key is not None and key.record == parameter.key_record:
            return key
    if parameter.scalar == "string" and type(value) is str:
        return {"string": value}
    if parameter.scalar == "boolean" and type(value) is bool:
        return {"boolean": value}
    if (
        parameter.scalar == "decimal"
        and type(value) is str
        and re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", value)
    ):
        return {"decimalToken": value}
    raise ExecutionError("INVALID")


def rejected_command(invocation_key: str, error: ExecutionError) -> Outcome:
    return {
        "__typename": "CommandRejected",
        "invocationKey": invocation_key,
        "code": error.code,
        "confirmation": (error.safe_reference if error.code == "CONFIRMATION_REQUIRED" else None),
    }


def command_outcome(
    result: CommandResult, invocation_key: str, encode_key: EncodeKey, observe: bool
) -> Outcome:
    if type(result) is not CommandResult or result.invocation_key != invocation_key:
        return _unavailable(invocation_key, observe)
    if result.status == "rejected":
        return _rejection_result(result, observe)
    if result.status == "not-observed" and observe and result.durability == "none":
        return {"__typename": "CommandNotObserved", "invocationKey": invocation_key}
    if (
        result.status in {"applied", "recovered"}
        and (not observe or result.status == "recovered")
        and result.durability in {"committed", "pending-caller-commit"}
        and result.receipt
    ):
        return _confirmed_result(result, encode_key)
    return _unavailable(invocation_key, observe)


def _confirmed_result(result: CommandResult, encode_key: EncodeKey) -> Outcome:
    outcome: Outcome = {
        "__typename": "CommandApplied" if result.status == "applied" else "CommandRecovered",
        "invocationKey": result.invocation_key,
        "durability": result.durability.replace("-", "_").upper(),
        "receipt": result.receipt,
    }
    if result.status == "applied":
        outcome["affectedIds"] = [encode_key(key) for key in result.affected]
    return outcome


def _rejection_result(result: CommandResult, observe: bool) -> Outcome:
    if result.durability != "none" or result.affected or result.receipt:
        return _unavailable(result.invocation_key, observe)
    try:
        error = ExecutionError(cast(ExecutionErrorCode, result.code), result.confirmation)
    except ValueError:
        return _unavailable(result.invocation_key, observe)
    return rejected_command(result.invocation_key, error)


def _unavailable(invocation_key: str, observe: bool) -> Outcome:
    if observe:
        raise GraphQLError("BUSY", extensions={"code": "BUSY"})
    return {"__typename": "CommandUnknown", "invocationKey": invocation_key}
