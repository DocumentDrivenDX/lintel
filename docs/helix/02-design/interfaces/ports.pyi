"""Target neutral boundary for CONTRACT-002; specification, not installed code."""
from collections.abc import Callable, Mapping
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import Literal, NamedTuple, Protocol

CoreLiteral = Mapping[str, object] | None  # Existing UMF exact tagged literal; upstream validated.

class ElementRef(NamedTuple):
    module: str
    element: str

class OperationRef(NamedTuple):
    module: str
    id: str
    kind: Literal['table', 'action', 'record']

class NodeKey(NamedTuple):
    record: ElementRef
    key_id: str
    components: tuple[CoreLiteral, ...]

Arguments = Mapping[str, CoreLiteral | NodeKey]  # Declared scalar or key input; omission stays absent.

@dataclass(frozen=True, slots=True)
class ConnectionIntent:
    response_key: str
    field_name: str
    lookup: OperationRef
    arguments: Arguments
    first: int
    after: str | None
    fields: tuple[ElementRef, ...]

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

class PlannedExecutionPort(Protocol):
    def capabilities(self) -> Mapping[str, str]: ...
    def session_planned(self, scope: RequestScope, intents: tuple[ConnectionIntent, ...]) -> AbstractAsyncContextManager[RequestSession]: ...

class PlannedRequestSession(Protocol):
    async def planned_connection(self, intent: ConnectionIntent) -> ConnectionPage: ...

class NodeCodec(Protocol):
    def profile(self) -> str: ...
    def encode(self, namespace: str, key: NodeKey) -> str: ...
    def decode(self, namespace: str, value: str) -> NodeKey: ...

class StringKeyNodeCodec:
    """Portable routing-only codec for required string Key components."""
    def __init__(self) -> None: ...
    def profile(self) -> str: ...
    def encode(self, namespace: str, key: NodeKey) -> str: ...
    def decode(self, namespace: str, value: str) -> NodeKey: ...
    @classmethod
    def for_prepared_api(
        cls,
        prepared: PreparedApiRootPins,
        validators: Mapping[
            tuple[ElementRef, str],
            Callable[[str, str, str, tuple[object, ...]], tuple[object, ...]],
        ],
    ) -> StringKeyNodeCodec: ...
    def registry_matches(self, prepared: PreparedApiRootPins) -> bool: ...

class PreparedApiRootPins(Protocol):
    @property
    def version(self) -> str: ...
    @property
    def generated_roots(self) -> tuple[PreparedGeneratedRootInfo, ...]: ...

class PreparedGeneratedRootInfo(Protocol):
    @property
    def lookup(self) -> OperationRef: ...
    @property
    def source_digest(self) -> str: ...
    @property
    def artifact_digest(self) -> str: ...
    @property
    def receipt_digest(self) -> str: ...
    @property
    def binding_digest(self) -> str: ...
    @property
    def algebra_sha256(self) -> str: ...
    @property
    def primary_key_id(self) -> str: ...
