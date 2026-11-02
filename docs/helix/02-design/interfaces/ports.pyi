"""Target neutral boundary for CONTRACT-002; specification, not installed code."""
from collections.abc import Mapping
from contextlib import AbstractAsyncContextManager
from typing import Literal, NamedTuple, Protocol

CoreLiteral = Mapping[str, object]  # Existing UMF exact tagged literal; upstream validated.

class ElementRef(NamedTuple):
    module: str
    element: str

class OperationRef(NamedTuple):
    module: str
    id: str
    kind: Literal['table', 'action']

class NodeKey(NamedTuple):
    record: ElementRef
    key_id: str
    components: tuple[CoreLiteral, ...]

Arguments = Mapping[str, CoreLiteral | NodeKey]  # Declared scalar or key input; omission stays absent.

class NodeValue(NamedTuple):
    key: NodeKey
    fields: Mapping[ElementRef, CoreLiteral]  # Qualified Field identities.

class Edge(NamedTuple):
    cursor: str
    node: NodeValue

class ConnectionPage(NamedTuple):
    edges: tuple[Edge, ...]
    has_next_page: bool
    has_previous_page: bool

class RequestScope(NamedTuple):
    application: str
    api_digest: str
    kind: Literal['query', 'mutation']
    authority: object  # Trusted host-owned capability handle; never reconstructed from body.
    request_id: str
    deadline_monotonic: float

class CommandResult(NamedTuple):
    status: Literal['applied', 'recovered', 'not-observed', 'unknown', 'rejected']
    invocation_key: str
    durability: Literal['committed', 'pending-caller-commit', 'unknown', 'none']
    affected: tuple[NodeKey, ...]
    receipt: str | None
    code: str | None
    confirmation: str | None  # Opaque host challenge only; not proof of approval.

class ExecutionError(Exception):
    code: str
    safe_reference: str | None

class RequestSession(Protocol):
    async def get_many(self, operation: OperationRef, keys: tuple[NodeKey, ...], fields: tuple[ElementRef, ...]) -> tuple[NodeValue | None, ...]: ...
    async def connection(self, operation: OperationRef, arguments: Arguments, first: int, after: str | None, fields: tuple[ElementRef, ...]) -> ConnectionPage: ...
    async def related_many(self, operation: OperationRef, parents: tuple[NodeKey, ...], target: ElementRef, fields: tuple[ElementRef, ...]) -> tuple[NodeValue | None, ...]: ...
    async def invoke(self, operation: OperationRef, arguments: Arguments, invocation_key: str, confirmation: str | None) -> CommandResult: ...
    async def observe(self, operation: OperationRef, arguments: Arguments, invocation_key: str) -> CommandResult: ...

class ExecutionPort(Protocol):
    def capabilities(self) -> Mapping[str, str]: ...
    def session(self, scope: RequestScope) -> AbstractAsyncContextManager[RequestSession]: ...

class NodeCodec(Protocol):
    def profile(self) -> str: ...
    def encode(self, namespace: str, key: NodeKey) -> str: ...
    def decode(self, namespace: str, value: str) -> NodeKey: ...
