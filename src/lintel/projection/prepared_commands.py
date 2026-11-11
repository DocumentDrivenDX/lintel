"""Closed metadata and schema for the prepared table command profile."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, cast

from lintel.ports import OperationRef

Scalar = Literal["string", "boolean", "decimal"]
_SCALARS = {"string": "String", "boolean": "Boolean", "decimal": "Decimal"}
_NAME = re.compile(r"^(?!__)[_A-Za-z][_0-9A-Za-z]*$")
_CONTROLS = {"invocationKey", "confirmation"}


@dataclass(frozen=True, slots=True)
class TableCommandParameter:
    name: str
    scalar: Scalar
    required: bool


@dataclass(frozen=True, slots=True)
class PreparedTableCommand:
    name: str
    operation: OperationRef
    parameters: tuple[TableCommandParameter, ...]


def parse_command(value: object) -> PreparedTableCommand:
    row = _object(value, {"name", "operation", "parameters"})
    op = _object(row["operation"], {"module", "id", "kind"})
    module, operation = op["module"], op["id"]
    params = _array(row["parameters"], 32)
    if op["kind"] != "table" or type(module) is not str or not module:
        raise ValueError("API_MISMATCH")
    if type(operation) is not str or not operation:
        raise ValueError("API_MISMATCH")
    parameters = tuple(_parameter(item) for item in params)
    if len({item.name for item in parameters}) != len(parameters):
        raise ValueError("API_MISMATCH")
    return PreparedTableCommand(
        _name(row["name"]), OperationRef(module, operation, "table"), parameters
    )


def _object(value: object, keys: set[str]) -> dict[str, object]:
    if type(value) is not dict:
        raise ValueError("API_MISMATCH")
    row = cast(dict[str, object], value)
    if set(row) != keys:
        raise ValueError("API_MISMATCH")
    return row


def _array(value: object, limit: int) -> list[object]:
    if type(value) is not list:
        raise ValueError("API_MISMATCH")
    items = cast(list[object], value)
    if len(items) > limit:
        raise ValueError("API_MISMATCH")
    return items


def _name(value: object) -> str:
    if type(value) is not str or not _NAME.fullmatch(value):
        raise ValueError("API_MISMATCH")
    return value


def _parameter(value: object) -> TableCommandParameter:
    row = _object(value, {"name", "scalar", "required"})
    name = _name(row["name"])
    scalar, required = row["scalar"], row["required"]
    if name in _CONTROLS or type(scalar) is not str or scalar not in _SCALARS:
        raise ValueError("API_MISMATCH")
    if type(required) is not bool:
        raise ValueError("API_MISMATCH")
    return TableCommandParameter(name, cast(Scalar, scalar), required)


def admitted_commands(
    artifact: Mapping[str, object], exposure: Mapping[str, object], caps: Mapping[str, str]
) -> tuple[PreparedTableCommand, ...]:
    selected = exposure.get("mutations", [])
    rows = artifact.get("commands")
    if "commands" not in artifact and selected == []:
        return ()
    if (
        artifact.get("version") != "lintel.prepared-api/5"
        or type(selected) is not list
        or not all(
            caps.get(f"command.{feature}") == "1"
            and caps.get(f"command.{feature}.binding.profile") == caps.get("binding.profile")
            for feature in ("outcome", "observe")
        )
    ):
        raise ValueError("API_MISMATCH")
    commands = tuple(parse_command(row) for row in _array(rows, 64))
    if not commands:
        raise ValueError("API_MISMATCH")
    expected = [
        {"name": command.name, "operation": command.operation._asdict()} for command in commands
    ]
    if selected != expected or len({command.name for command in commands}) != len(commands):
        raise ValueError("API_MISMATCH")
    return commands


_OUTCOMES = """
enum CommandDurability { COMMITTED PENDING_CALLER_COMMIT UNKNOWN NONE }
enum AccessFailureCode {
  INVALID DENIED CONFLICT PRECONDITION_FAILED CONFIRMATION_REQUIRED
  UNSUPPORTED API_MISMATCH INVALID_CURSOR TOO_MANY_ROWS LIMIT_EXCEEDED
  BUSY NOT_YET_CURRENT
}
type CommandApplied {
  invocationKey: ID!
  durability: CommandDurability!
  receipt: String!
  affectedIds: [ID!]!
}
type CommandRecovered { invocationKey: ID!, durability: CommandDurability!, receipt: String! }
type CommandNotObserved { invocationKey: ID! }
type CommandUnknown { invocationKey: ID! }
type CommandRejected { invocationKey: ID!, code: AccessFailureCode!, confirmation: String }
union CommandOutcome = CommandApplied | CommandRecovered | CommandUnknown | CommandRejected
union CommandObservation = CommandRecovered | CommandNotObserved | CommandRejected
"""


def command_sdl(sdl: str, commands: tuple[PreparedTableCommand, ...], *, has_decimal: bool) -> str:
    if not commands:
        return sdl
    if not has_decimal and any(p.scalar == "decimal" for c in commands for p in c.parameters):
        sdl += "\nscalar Decimal\n"
    mutations = " ".join(
        f"{c.name}(input: {c.name[0].upper() + c.name[1:]}Input!): CommandOutcome!"
        for c in commands
    )
    return (
        sdl
        + f"\ntype Mutation {{ {mutations} }}\n"
        + _OUTCOMES
        + "\n".join(_command_definitions(command) for command in commands)
    )


def _command_definitions(command: PreparedTableCommand) -> str:
    upper_name = command.name[0].upper() + command.name[1:]
    args = " ".join(
        f"{p.name}: {_SCALARS[p.scalar]}{'!' if p.required else ''}" for p in command.parameters
    )
    return (
        f"input {upper_name}Input {{ {args} invocationKey: ID! confirmation: String }}\n"
        f"input Observe{upper_name}Input {{ {args} invocationKey: ID! }}\n"
        f"extend type Query {{ observe{upper_name}(input: Observe{upper_name}Input!):"
        " CommandObservation! }\n"
    )
