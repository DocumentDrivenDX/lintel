import asyncio
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager

import pytest

from lintel import (
    Arguments,
    CommandResult,
    ConnectionPage,
    Edge,
    ElementRef,
    ExecutionError,
    ExecutionPort,
    NodeCodec,
    NodeKey,
    NodeValue,
    OperationRef,
    RequestScope,
    RequestSession,
)


class FabricatedSession:
    def __init__(self) -> None:
        self.task_ref = ElementRef("board", "Task")
        self.title_ref = ElementRef("board", "title")
        self.key = NodeKey(self.task_ref, "taskKey", ({"string": "t-1"},))
        self.node = NodeValue(self.key, {self.title_ref: {"string": "Fabricated"}})
        self.applied = CommandResult(
            "applied", "invoke-1", "committed", (self.key,), "receipt-1", None, None
        )

    async def get_many(
        self, operation: OperationRef, keys: tuple[NodeKey, ...], fields: tuple[ElementRef, ...]
    ) -> tuple[NodeValue | None, ...]:
        if operation.kind != "table" or fields != (self.title_ref,):
            raise ExecutionError("UNSUPPORTED", "board.Task")
        return tuple(self.node if key == self.key else None for key in keys)

    async def connection(
        self,
        operation: OperationRef,
        arguments: Arguments,
        first: int,
        after: str | None,
        fields: tuple[ElementRef, ...],
    ) -> ConnectionPage:
        if operation.kind != "table" or first != 1 or after is not None:
            raise ExecutionError("INVALID_CURSOR", "board.tasks")
        return ConnectionPage((Edge("cursor-1", self.node),), False, False)

    async def related_many(
        self,
        operation: OperationRef,
        parents: tuple[NodeKey, ...],
        target: ElementRef,
        fields: tuple[ElementRef, ...],
    ) -> tuple[NodeValue | None, ...]:
        if operation.kind != "table" or target != self.task_ref:
            raise ExecutionError("UNSUPPORTED", "board.assignedTasks")
        return tuple(self.node if parent == self.key else None for parent in parents)

    async def invoke(
        self,
        operation: OperationRef,
        arguments: Arguments,
        invocation_key: str,
        confirmation: str | None,
    ) -> CommandResult:
        if operation.kind != "action" or invocation_key != "invoke-1":
            raise ExecutionError("INVALID", "board.completeTask")
        return self.applied

    async def observe(
        self, operation: OperationRef, arguments: Arguments, invocation_key: str
    ) -> CommandResult:
        if operation.kind != "action" or invocation_key != "invoke-1":
            raise ExecutionError("INVALID", "board.completeTask")
        return self.applied._replace(status="recovered")


class FabricatedPort:
    def __init__(self) -> None:
        self.data = FabricatedSession()

    def capabilities(self) -> Mapping[str, str]:
        return {"lintel.execution": "1", "node.refetch": "1"}

    @asynccontextmanager
    async def session(self, scope: RequestScope) -> AsyncGenerator[RequestSession, None]:
        if not scope.application or not scope.request_id or scope.authority is None:
            raise ExecutionError("DENIED")
        yield self.data


class FabricatedCodec:
    def profile(self) -> str:
        return "fabricated-node/1"

    def encode(self, namespace: str, key: NodeKey) -> str:
        return namespace + ":" + key.record.module + ":" + key.record.element + ":" + key.key_id

    def decode(self, namespace: str, value: str) -> NodeKey:
        parts = value.split(":")
        if len(parts) != 4 or parts[0] != namespace:
            raise ExecutionError("INVALID")
        return NodeKey(ElementRef(parts[1], parts[2]), parts[3], ({"string": "t-1"},))


def test_public_port_shapes_execute_against_an_independent_fabricated_provider() -> None:
    asyncio.run(_exercise_public_port_shapes())


async def _exercise_public_port_shapes() -> None:
    port: ExecutionPort = FabricatedPort()
    codec: NodeCodec = FabricatedCodec()
    scope = RequestScope("task-board", "a" * 64, "query", object(), "req-1", 100.0)
    task_lookup = OperationRef("board", "lookupTask", "table")
    task_list = OperationRef("board", "tasks", "table")
    complete = OperationRef("board", "completeTask", "action")
    field = ElementRef("board", "title")

    assert port.capabilities()["lintel.execution"] == "1"
    async with port.session(scope) as session:
        nodes = await session.get_many(task_lookup, (port.data.key, port.data.key), (field,))
        assert nodes == (port.data.node, port.data.node)
        page = await session.connection(task_list, {}, 1, None, (field,))
        assert page == ConnectionPage((Edge("cursor-1", port.data.node),), False, False)
        related = await session.related_many(
            task_lookup,
            (port.data.key, NodeKey(ElementRef("board", "Person"), "personKey", ())),
            port.data.task_ref,
            (field,),
        )
        assert related == (port.data.node, None)
        assert await session.invoke(complete, {}, "invoke-1", None) == port.data.applied
        assert await session.observe(complete, {}, "invoke-1") == port.data.applied._replace(
            status="recovered"
        )
        nullable: Arguments = {"title": None}
        assert nullable["title"] is None

    opaque = codec.encode("task-board", port.data.key)
    assert codec.decode("task-board", opaque) == port.data.key
    with pytest.raises(AttributeError):
        setattr(port.data.key, "key" + "_id", "other")
    with pytest.raises(ExecutionError, match="INVALID_CURSOR"):
        async with port.session(scope) as session:
            await session.connection(task_list, {}, 1, "foreign", (field,))
