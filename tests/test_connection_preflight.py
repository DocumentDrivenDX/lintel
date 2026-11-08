from __future__ import annotations

from collections.abc import AsyncGenerator, Mapping
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from time import monotonic
from typing import Protocol, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from graphql import OperationDefinitionNode, build_schema, parse
from graphql.execution.values import VariableValues, get_variable_values
from httpx import Response as HttpxResponse

from lintel.graphql import create_router
from lintel.graphql import router as router_module
from lintel.graphql.preflight import BudgetFailure, collect_connection_intents, preflight
from lintel.ports.protocols import ExecutionPort, NodeCodec, RequestSession
from lintel.ports.values import (
    ConnectionIntent,
    ConnectionPage,
    Edge,
    ElementRef,
    NodeKey,
    NodeValue,
    OperationRef,
    RequestScope,
)
from lintel.projection.prepared import AdmittedPreparedApi, PreparedField, PreparedRecord
from lintel.projection.prepared_v3 import PreparedConnection


class _Client(Protocol):
    def post(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: Mapping[str, object],
    ) -> HttpxResponse: ...


class _Codec:
    def profile(self) -> str:
        return "test"

    def encode(self, namespace: str, key: NodeKey) -> str:
        return f"{namespace}:note-1"

    def decode(self, namespace: str, value: str) -> NodeKey:
        raise ValueError(value)


class _PlannedPort:
    def __init__(self) -> None:
        self.staged: tuple[ConnectionIntent, ...] = ()
        self.entered = False
        self.dispatched: list[ConnectionIntent] = []
        self.pages: dict[str, ConnectionPage] = {}

    def capabilities(self) -> Mapping[str, str]:
        return {}

    def session(self, scope: RequestScope) -> AbstractAsyncContextManager[RequestSession]:
        del scope
        raise AssertionError("API3 connection request must use planned session")

    def session_planned(
        self, _scope: RequestScope, intents: tuple[ConnectionIntent, ...]
    ) -> AbstractAsyncContextManager[RequestSession]:
        self.staged = intents
        return self._session()

    @asynccontextmanager
    async def _session(self) -> AsyncGenerator[RequestSession, None]:
        self.entered = True
        yield cast(RequestSession, self)

    async def planned_connection(self, intent: ConnectionIntent) -> ConnectionPage:
        assert self.entered
        self.dispatched.append(intent)
        return self.pages.get(intent.response_key, ConnectionPage((), False, False))


def _run(query: str, max_dispatch: int, max_occurrences: int = 256) -> None:
    schema = build_schema(
        """
        type Query { notes(first: Int = 25): NotesConnection!, node(id: ID!): Node }
        type NotesConnection { edges: [NotesEdge!]!, pageInfo: PageInfo! }
        type NotesEdge { cursor: String!, node: Note! }
        type PageInfo { hasNextPage: Boolean!, hasPreviousPage: Boolean! }
        interface Node { id: ID! }
        type Note implements Node { id: ID!, title: String }
        """
    )
    document = parse(query)
    operation = cast(
        OperationDefinitionNode,
        next(item for item in document.definitions if item.kind == "operation_definition"),
    )
    variables = VariableValues({}, {})
    preflight(
        schema,
        document,
        operation,
        variables,
        {
            "maxConcurrentDispatch": max_dispatch,
            "maxDepth": 8,
            "maxFieldOccurrences": max_occurrences,
            "maxAliases": 32,
            "maxCost": 10000,
            "defaultPage": 25,
            "maxPage": 100,
            "maxLookup": 100,
        },
        frozenset({"notes"}),
    )


def test_dispatch_budget_counts_merged_root_alias_once() -> None:
    _run(
        "query { a: notes { ...Fields } ...More } "
        "fragment More on Query { a: notes { ...Fields } } "
        "fragment Fields on NotesConnection { edges { node { id } } }",
        1,
    )


def test_merged_alias_still_counts_source_occurrences() -> None:
    with pytest.raises(BudgetFailure, match="LIMIT_EXCEEDED"):
        _run(
            "query { a: notes { edges { node { id } } } ...More } "
            "fragment More on Query { a: notes { edges { node { id } } } }",
            1,
            max_occurrences=1,
        )


def test_dispatch_budget_counts_distinct_connection_aliases() -> None:
    with pytest.raises(BudgetFailure, match="LIMIT_EXCEEDED"):
        _run("query { a: notes { edges { node { id } } } b: notes { edges { node { id } } } }", 1)


def test_connection_intents_use_coerced_defaults_and_active_merged_fields() -> None:
    schema = build_schema(
        """
        type Query { notes(first: Int = 25, after: String): NotesConnection! }
        type NotesConnection { edges: [NotesEdge!]!, pageInfo: PageInfo! }
        type NotesEdge { cursor: String!, node: Note! }
        type PageInfo { hasNextPage: Boolean!, hasPreviousPage: Boolean! }
        type Note { id: ID!, title: String, owner: String }
        """
    )
    document = parse(
        "query($skipOwner: Boolean! = true) { a: notes { edges { node { ...Public } } } } "
        "fragment Public on Note { id title owner @skip(if: $skipOwner) }"
    )
    operation = cast(
        OperationDefinitionNode,
        next(item for item in document.definitions if item.kind == "operation_definition"),
    )
    variables = get_variable_values(schema, operation.variable_definitions or (), {})
    assert not isinstance(variables, list)
    key = ElementRef("demo", "id")
    title = ElementRef("demo", "title")
    owner = ElementRef("demo", "owner")
    lookup = OperationRef("demo", "Note", "record")
    record = PreparedRecord(
        ElementRef("demo", "Note"),
        "primary",
        (key,),
        "Note",
        lookup,
        (
            PreparedField(title, "title", "string", True),
            PreparedField(owner, "owner", "string", True),
        ),
    )
    route = PreparedConnection(
        lookup,
        "notes",
        (title, owner),
        key,
        "0" * 64,
        {},
    )
    prepared = object.__new__(AdmittedPreparedApi)
    object.__setattr__(prepared, "_version", "lintel.prepared-api/3")
    object.__setattr__(prepared, "_generated_connections", (route,))
    object.__setattr__(prepared, "_records", (record,))
    object.__setattr__(
        prepared,
        "_host_profile",
        {"limits": {"defaultPage": "25", "maxPage": "100", "cursorBytes": "4096"}},
    )

    intents = collect_connection_intents(schema, document, operation, variables, prepared)
    assert len(intents) == 1
    intent = intents[0]
    assert intent.response_key == "a"
    assert intent.field_name == "notes"
    assert intent.lookup == lookup
    assert intent.arguments == {}
    assert intent.first == 25
    assert intent.after is None
    assert intent.fields == (title,)


def test_router_stages_all_aliases_before_entering_planned_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = ElementRef("demo", "Note")
    key_field = ElementRef("demo", "id")
    title = ElementRef("demo", "title")
    lookup = OperationRef("demo", "Note", "record")
    record = PreparedRecord(
        source,
        "primary",
        (key_field,),
        "Note",
        lookup,
        (PreparedField(title, "title", "string", True),),
    )
    route = PreparedConnection(lookup, "notes", (title,), key_field, "0" * 64, {})
    prepared = object.__new__(AdmittedPreparedApi)
    object.__setattr__(prepared, "_version", "lintel.prepared-api/3")
    object.__setattr__(prepared, "_application", "fixture")
    object.__setattr__(prepared, "_api_digest", "a" * 64)
    object.__setattr__(prepared, "_identity_namespace", "fixture.v1")
    object.__setattr__(prepared, "_records", (record,))
    object.__setattr__(prepared, "_generated_connections", (route,))
    object.__setattr__(
        prepared,
        "_sdl",
        """
        interface Node { id: ID! }
        type Note implements Node { id: ID!, title: String }
        type NoteEdge { cursor: String!, node: Note! }
        type NoteConnection { edges: [NoteEdge!]!, pageInfo: PageInfo! }
        type PageInfo {
          hasNextPage: Boolean!
          hasPreviousPage: Boolean!
          startCursor: String
          endCursor: String
        }
        type Query {
          node(id: ID!): Node
          nodes(ids: [ID!]!): [Node]!
          notes(first: Int = 25, after: String): NoteConnection!
        }
        """,
    )
    object.__setattr__(
        prepared,
        "_host_profile",
        {
            "mount": "/graphql",
            "introspection": False,
            "limits": {
                "requestBytes": "1048576",
                "documentBytes": "262144",
                "responseBytes": "8388608",
                "deadlineMs": "30000",
                "nodeIdBytes": "2048",
                "cursorBytes": "4096",
                "defaultPage": "25",
                "maxPage": "100",
                "maxLookup": "100",
                "maxDepth": "8",
                "maxFieldOccurrences": "256",
                "maxAliases": "32",
                "maxCost": "10000",
                "maxConcurrentDispatch": "2",
            },
        },
    )

    def ignore_profiles(
        _prepared: AdmittedPreparedApi, _executor: ExecutionPort, _codec: NodeCodec
    ) -> None:
        return None

    monkeypatch.setattr(router_module, "_check_runtime_profiles", ignore_profiles)
    port = _PlannedPort()
    key = NodeKey(source, "primary", ({"string": "note-1"},))
    port.pages["a"] = ConnectionPage(
        (Edge("opaque-token", NodeValue(key, {title: {"string": "hello"}})),),
        True,
        False,
    )

    async def resolve_context(_request: object, digest: str) -> RequestScope:
        return RequestScope("fixture", digest, "query", object(), "req", monotonic() + 60)

    app = FastAPI()
    app.include_router(create_router(prepared, port, _Codec(), resolve_context))
    response = cast(_Client, TestClient(app)).post(
        "/graphql",
        headers={"x-lintel-api": "a" * 64, "content-type": "application/json"},
        json={
            "query": (
                "query { a: notes(first: 2) { edges { cursor node { id title } } "
                "pageInfo { hasNextPage hasPreviousPage startCursor endCursor } } "
                "b: notes(first: 0) { edges { cursor } } }"
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "a": {
                "edges": [
                    {
                        "cursor": "opaque-token",
                        "node": {"id": "fixture.v1:note-1", "title": "hello"},
                    }
                ],
                "pageInfo": {
                    "hasNextPage": True,
                    "hasPreviousPage": False,
                    "startCursor": "opaque-token",
                    "endCursor": "opaque-token",
                },
            },
            "b": {"edges": []},
        }
    }
    assert port.entered
    assert tuple(intent.response_key for intent in port.staged) == ("a", "b")
    assert tuple(intent.first for intent in port.staged) == (2, 0)
    assert tuple(intent for intent in port.staged) == tuple(port.dispatched)
