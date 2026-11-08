"""Immutable value shapes for the CONTRACT-002 host boundary."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, NamedTuple

CoreLiteral = Mapping[str, object] | None


class ElementRef(NamedTuple):
    module: str
    element: str


class OperationRef(NamedTuple):
    module: str
    id: str
    kind: Literal["table", "action", "record"]


class NodeKey(NamedTuple):
    record: ElementRef
    key_id: str
    components: tuple[CoreLiteral, ...]


Arguments = Mapping[str, CoreLiteral | NodeKey]


@dataclass(frozen=True, slots=True)
class ConnectionIntent:
    """One immutable, caller-coerced root connection staged before session entry."""

    response_key: str
    field_name: str
    lookup: OperationRef
    arguments: Arguments
    first: int
    after: str | None
    fields: tuple[ElementRef, ...]


class NodeValue(NamedTuple):
    key: NodeKey
    fields: Mapping[ElementRef, CoreLiteral]


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
    kind: Literal["query", "mutation"]
    authority: object
    request_id: str
    deadline_monotonic: float


class CommandResult(NamedTuple):
    status: Literal["applied", "recovered", "not-observed", "unknown", "rejected"]
    invocation_key: str
    durability: Literal["committed", "pending-caller-commit", "unknown", "none"]
    affected: tuple[NodeKey, ...]
    receipt: str | None
    code: str | None
    confirmation: str | None
