"""Transport-neutral asynchronous execution and Node codec protocols."""

from collections.abc import Mapping
from contextlib import AbstractAsyncContextManager
from typing import Protocol

from lintel.ports.values import (
    Arguments,
    CommandResult,
    ConnectionIntent,
    ConnectionPage,
    ElementRef,
    NodeKey,
    NodeValue,
    OperationRef,
    RequestScope,
)


class RequestSession(Protocol):
    async def get_many(
        self,
        operation: OperationRef,
        keys: tuple[NodeKey, ...],
        fields: tuple[ElementRef, ...],
    ) -> tuple[NodeValue | None, ...]: ...

    async def connection(
        self,
        operation: OperationRef,
        arguments: Arguments,
        first: int,
        after: str | None,
        fields: tuple[ElementRef, ...],
    ) -> ConnectionPage: ...

    async def related_many(
        self,
        operation: OperationRef,
        parents: tuple[NodeKey, ...],
        target: ElementRef,
        fields: tuple[ElementRef, ...],
    ) -> tuple[NodeValue | None, ...]: ...

    async def invoke(
        self,
        operation: OperationRef,
        arguments: Arguments,
        invocation_key: str,
        confirmation: str | None,
    ) -> CommandResult: ...

    async def observe(
        self,
        operation: OperationRef,
        arguments: Arguments,
        invocation_key: str,
    ) -> CommandResult: ...


class ExecutionPort(Protocol):
    def capabilities(self) -> Mapping[str, str]: ...

    def session(self, scope: RequestScope) -> AbstractAsyncContextManager[RequestSession]: ...


class PlannedExecutionPort(Protocol):
    """Optional operation-wide preflight seam for selected root connections."""

    def capabilities(self) -> Mapping[str, str]: ...

    def session_planned(
        self, scope: RequestScope, intents: tuple[ConnectionIntent, ...]
    ) -> AbstractAsyncContextManager[RequestSession]: ...


class PlannedRequestSession(Protocol):
    """API3 connection dispatch that preserves its exact staged intent identity."""

    async def planned_connection(self, intent: ConnectionIntent) -> ConnectionPage: ...


class NodeCodec(Protocol):
    def profile(self) -> str: ...

    def encode(self, namespace: str, key: NodeKey) -> str: ...

    def decode(self, namespace: str, value: str) -> NodeKey: ...
