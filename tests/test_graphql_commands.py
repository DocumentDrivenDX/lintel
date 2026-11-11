"""Exercise GraphQL command and observation fields through the neutral port."""

import asyncio
from pathlib import Path
from typing import Protocol, cast

import graphql
from graphql import ExecutionResult, GraphQLSchema, build_schema

from lintel.graphql.commands import CommandBinding, CommandParameter, install_command_resolvers
from lintel.ports import Arguments, CommandResult, ElementRef, ExecutionError, NodeKey, OperationRef

_GRAPHQL_FUNCTION = "graphql"
TASK = ElementRef("board", "Task")
KEY = NodeKey(TASK, "primary", ({"string": "t-001"},))
COMMAND = OperationRef("board", "completeTask", "table")


class ExecuteGraphQL(Protocol):
    async def __call__(
        self,
        schema: GraphQLSchema,
        source: str,
        *,
        context_value: dict[str, object],
        variable_values: dict[str, object],
    ) -> ExecutionResult: ...


class CommandSession:
    def __init__(self) -> None:
        self.effects: dict[str, Arguments] = {}
        self.dispatches = 0

    async def invoke(
        self,
        operation: OperationRef,
        arguments: Arguments,
        invocation_key: str,
        confirmation: str | None,
    ) -> CommandResult:
        assert operation == COMMAND
        if confirmation != "approved":
            raise ExecutionError("CONFIRMATION_REQUIRED", "challenge")
        self.dispatches += 1
        self.effects[invocation_key] = arguments
        return CommandResult("unknown", invocation_key, "unknown", (), None, None, None)

    async def observe(
        self,
        operation: OperationRef,
        arguments: Arguments,
        invocation_key: str,
    ) -> CommandResult:
        assert operation == COMMAND
        if self.effects.get(invocation_key) != arguments:
            return CommandResult("not-observed", invocation_key, "none", (), None, None, None)
        return CommandResult("recovered", invocation_key, "committed", (), "receipt", None, None)


def test_command_observation_uses_original_presence_and_never_dispatches() -> None:
    async def run() -> None:
        source = (
            Path(__file__).resolve().parents[1] / "docs/helix/02-design/examples/task-board.graphql"
        )
        schema = build_schema(source.read_text())
        install_command_resolvers(
            schema,
            CommandBinding(
                "completeTask",
                COMMAND,
                (CommandParameter("task", "key", TASK), CommandParameter("note", "string")),
            ),
            lambda value: KEY if value == "task-id" else None,
            lambda _key: "task-id",
        )
        session = CommandSession()
        context: dict[str, object] = {
            "session": session,
            "dispatch_semaphore": asyncio.Semaphore(1),
        }
        invoke = """
        mutation Complete($input: CompleteTaskInput!) {
          completeTask(input: $input) {
            __typename
            ... on CommandRejected { code confirmation }
            ... on CommandUnknown { invocationKey }
          }
        }
        """
        observe = """
        query Observe($input: ObserveCompleteTaskInput!) {
          observeCompleteTask(input: $input) {
            __typename
            ... on CommandRecovered { invocationKey durability receipt }
          }
        }
        """

        async def execute(document: str, **fields: str | None) -> dict[str, object]:
            run_graphql = cast(ExecuteGraphQL, getattr(graphql, _GRAPHQL_FUNCTION))
            result = await run_graphql(
                schema,
                document,
                context_value=context,
                variable_values={
                    "input": {"task": "task-id", "invocationKey": "request-1", **fields}
                },
            )
            assert not result.errors
            assert result.data is not None
            return result.data

        assert await execute(invoke) == {
            "completeTask": {
                "__typename": "CommandRejected",
                "code": "CONFIRMATION_REQUIRED",
                "confirmation": "challenge",
            }
        }
        assert await execute(invoke, confirmation="approved") == {
            "completeTask": {"__typename": "CommandUnknown", "invocationKey": "request-1"}
        }
        assert await execute(observe, note=None) == {
            "observeCompleteTask": {"__typename": "CommandNotObserved"}
        }
        assert await execute(observe) == {
            "observeCompleteTask": {
                "__typename": "CommandRecovered",
                "invocationKey": "request-1",
                "durability": "COMMITTED",
                "receipt": "receipt",
            }
        }
        assert session.effects == {"request-1": {"task": KEY}}
        assert session.dispatches == 1

    asyncio.run(run())
