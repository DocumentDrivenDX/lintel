"""GraphQL resolver bindings for the prepared keyed-refetch subset."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Callable, Mapping
from typing import Any, cast

from graphql import (
    GraphQLError,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLResolveInfo,
    GraphQLSchema,
)
from graphql.execution.collect_fields import FieldDetails, FragmentDetails, collect_subfields
from graphql.execution.values import VariableValues
from graphql.language import FieldNode

from lintel.graphql.commands import CommandBinding, CommandParameter, install_command_resolvers
from lintel.graphql.relationships import install_relationships
from lintel.ports.protocols import NodeCodec, PlannedRequestSession, RequestSession
from lintel.ports.values import ConnectionIntent, ConnectionPage, ElementRef, NodeKey, NodeValue
from lintel.projection.prepared import AdmittedPreparedApi, PreparedField, PreparedRecord
from lintel.projection.prepared_v3 import PreparedConnection

Context = dict[str, object]
ResolveInfo = GraphQLResolveInfo[Context]


def install_resolvers(
    schema: GraphQLSchema,
    prepared: AdmittedPreparedApi,
    records: Mapping[ElementRef, PreparedRecord],
    fields: Mapping[str, Mapping[str, PreparedField]],
    codec: NodeCodec,
) -> None:
    query = cast(GraphQLObjectType, schema.get_type("Query"))
    get_one, get_many = _node_query_resolvers(prepared, records, codec)
    query.fields["node"].resolve = get_one
    query.fields["nodes"].resolve = get_many
    _install_record_resolvers(schema, prepared, records, fields, codec)
    _install_commands(schema, prepared, codec)
    if prepared.version == "lintel.prepared-api/5" and prepared.relationships:
        install_relationships(
            schema, prepared, records, _selected_fields, limit(prepared, "relationshipBatch")
        )
    if prepared.version in {
        "lintel.prepared-api/3",
        "lintel.prepared-api/4",
        "lintel.prepared-api/5",
    }:
        records_by_lookup = {record.lookup: record for record in records.values()}
        for route in prepared.generated_connections:
            record = records_by_lookup.get(route.lookup)
            if record is None or route.name not in query.fields:
                raise ValueError("API_MISMATCH")
            query.fields[route.name].resolve = _connection_resolver(prepared, route, record)


def _install_commands(
    schema: GraphQLSchema, prepared: AdmittedPreparedApi, codec: NodeCodec
) -> None:
    if prepared.version != "lintel.prepared-api/5":
        return
    for command in prepared.commands:
        install_command_resolvers(
            schema,
            CommandBinding(
                command.name,
                command.operation,
                tuple(CommandParameter(param.name, param.scalar) for param in command.parameters),
            ),
            lambda _value: None,
            lambda key: encode_node_key(codec, prepared, key),
        )


def _connection_resolver(
    prepared: AdmittedPreparedApi, route: PreparedConnection, record: PreparedRecord
) -> Callable[..., Any]:
    async def resolve(
        _root: object, info: ResolveInfo, first: int, after: str | None = None
    ) -> object:
        response_key = str(info.path.key)
        staged = cast(Mapping[str, ConnectionIntent], info.context.get("connection_intents", {}))
        intent = staged.get(response_key)
        consumed = cast(set[str], info.context.get("consumed_connection_intents", set[str]()))
        if (
            intent is None
            or response_key in consumed
            or intent.field_name != route.name
            or intent.lookup != route.lookup
            or intent.first != first
            or intent.after != after
            or intent.arguments
        ):
            raise GraphQLError("API_MISMATCH", extensions={"code": "API_MISMATCH"})
        consumed.add(response_key)
        session = _session(info)
        if not hasattr(session, "planned_connection"):
            raise GraphQLError("API_MISMATCH", extensions={"code": "API_MISMATCH"})
        page = await cast(PlannedRequestSession, session).planned_connection(intent)
        if (
            type(page) is not ConnectionPage
            or type(page.has_next_page) is not bool
            or type(page.has_previous_page) is not bool
            or len(page.edges) > first
            or first == 0
            and page.edges
        ):
            raise GraphQLError("UNSUPPORTED", extensions={"code": "UNSUPPORTED"})
        edges: list[dict[str, object]] = []
        seen_cursors: set[str] = set()
        for edge in page.edges:
            try:
                cursor_bytes = edge.cursor.encode("utf-8", errors="strict")
            except (AttributeError, UnicodeEncodeError) as error:
                raise GraphQLError("UNSUPPORTED", extensions={"code": "UNSUPPORTED"}) from error
            if (
                not cursor_bytes
                or len(cursor_bytes) > limit(prepared, "cursorBytes")
                or edge.cursor in seen_cursors
                or type(edge.node) is not NodeValue
                or edge.node.key.record != record.source
                or edge.node.key.key_id != record.key_id
                or len(edge.node.key.components) != len(record.key_fields)
                or not _valid_key_shape(edge.node.key)
                or not _valid_node(edge.node, edge.node.key, intent.fields)
            ):
                raise GraphQLError("UNSUPPORTED", extensions={"code": "UNSUPPORTED"})
            seen_cursors.add(edge.cursor)
            edges.append({"cursor": edge.cursor, "node": edge.node})
        return {
            "edges": edges,
            "pageInfo": {
                "hasNextPage": page.has_next_page,
                "hasPreviousPage": page.has_previous_page,
                "startCursor": page.edges[0].cursor if page.edges else None,
                "endCursor": page.edges[-1].cursor if page.edges else None,
            },
        }

    return resolve


def _node_query_resolvers(
    prepared: AdmittedPreparedApi,
    records: Mapping[ElementRef, PreparedRecord],
    codec: NodeCodec,
) -> tuple[Callable[..., Any], Callable[..., Any]]:
    resolver = _NodeQueryResolvers(prepared, records, codec)
    return resolver.get_one, resolver.get_many


class _NodeQueryResolvers:
    def __init__(
        self,
        prepared: AdmittedPreparedApi,
        records: Mapping[ElementRef, PreparedRecord],
        codec: NodeCodec,
    ) -> None:
        self.prepared = prepared
        self.records = records
        self.codec = codec

    async def get_one(self, _root: object, info: ResolveInfo, id: str) -> NodeValue | None:
        prepared, records, codec = self.prepared, self.records, self.codec
        key = decode_node_key(codec, prepared, id, records)
        if key is None:
            return None
        record = records[key.record]
        selected = _selected_fields(info, record)
        semaphore = cast(asyncio.Semaphore, info.context["dispatch_semaphore"])
        async with semaphore:
            nodes = await _session(info).get_many(record.lookup, (key,), selected)
        if len(nodes) != 1 or nodes[0] is not None and not _valid_node(nodes[0], key, selected):
            raise GraphQLError("UNSUPPORTED", extensions={"code": "UNSUPPORTED"})
        return nodes[0]

    async def get_many(
        self, _root: object, info: ResolveInfo, ids: list[str]
    ) -> list[NodeValue | None]:
        prepared, records, codec = self.prepared, self.records, self.codec
        if len(ids) > int(limit(prepared, "maxLookup")):
            raise GraphQLError("LIMIT_EXCEEDED", extensions={"code": "LIMIT_EXCEEDED"})
        grouped: dict[ElementRef, list[tuple[int, NodeKey]]] = {}
        result: list[NodeValue | None] = [None] * len(ids)
        for index, opaque in enumerate(ids):
            key = decode_node_key(codec, prepared, opaque, records)
            if key is not None:
                grouped.setdefault(key.record, []).append((index, key))
        for record_ref, entries in grouped.items():
            record = records[record_ref]
            keys = tuple(key for _, key in entries)
            selected = _selected_fields(info, record)
            semaphore = cast(asyncio.Semaphore, info.context["dispatch_semaphore"])
            async with semaphore:
                values = await _session(info).get_many(record.lookup, keys, selected)
            if len(values) != len(keys) or any(
                value is not None and not _valid_node(value, key, selected)
                for value, key in zip(values, keys, strict=True)
            ):
                raise GraphQLError("UNSUPPORTED", extensions={"code": "UNSUPPORTED"})
            for (index, _), value in zip(entries, values, strict=True):
                result[index] = value
        return result


def _install_record_resolvers(
    schema: GraphQLSchema,
    prepared: AdmittedPreparedApi,
    records: Mapping[ElementRef, PreparedRecord],
    fields: Mapping[str, Mapping[str, PreparedField]],
    codec: NodeCodec,
) -> None:
    node = cast(GraphQLInterfaceType, schema.get_type("Node"))
    node.resolve_type = _type_resolver(records)
    for type_name, mapping in fields.items():
        gql_type = cast(GraphQLObjectType, schema.get_type(type_name))
        gql_type.fields["id"].resolve = _resolve_id(prepared, codec)
        for field_name, definition in mapping.items():
            gql_type.fields[field_name].resolve = _resolve_projected_field(
                definition.source, definition.scalar
            )


def _type_resolver(records: Mapping[ElementRef, PreparedRecord]) -> Callable[..., str | None]:
    def resolve(value: Any, _info: Any, _abstract: Any) -> str | None:
        return resolve_record_type(value, records)

    return resolve


def _resolve_id(prepared: AdmittedPreparedApi, codec: NodeCodec) -> Callable[..., str]:
    def resolve(value: object, _info: ResolveInfo) -> str:
        if type(value) is not NodeValue:
            raise GraphQLError("UNSUPPORTED", extensions={"code": "UNSUPPORTED"})
        return encode_node_key(codec, prepared, value.key)

    return resolve


def _resolve_projected_field(source: ElementRef, scalar: str) -> Callable[..., object]:
    def resolve(value: object, _info: ResolveInfo) -> object:
        return scalar_value(value, source, scalar)

    return resolve


def _selected_fields(info: ResolveInfo, record: PreparedRecord) -> tuple[ElementRef, ...]:
    fragments = {
        name: FragmentDetails(definition=fragment) for name, fragment in info.fragments.items()
    }
    gql_type = info.schema.get_type(record.type_name)
    if gql_type is None or not hasattr(gql_type, "fields"):
        raise GraphQLError("API_MISMATCH", extensions={"code": "API_MISMATCH"})
    collected = collect_subfields(
        info.schema,
        fragments,
        cast(VariableValues, info.context["variables"]),
        info.operation,
        cast(GraphQLObjectType, gql_type),
        [FieldDetails(node, None) for node in info.field_nodes],
    )
    names = {
        detail.node.name.value
        for details in collected.grouped_field_set.values()
        for detail in details
        if detail.node.name.value != "__typename"
    }
    selected = tuple(f.source for f in record.fields if f.name in names)
    return selected


def resolve_record_type(value: object, records: Mapping[ElementRef, PreparedRecord]) -> str | None:
    return (
        records[value.key.record].type_name
        if type(value) is NodeValue and value.key.record in records
        else None
    )


def scalar_value(value: object, source: ElementRef, scalar: str) -> object:
    if type(value) is not NodeValue:
        return None
    literal = value.fields.get(source)
    wrapper = "decimalToken" if scalar == "decimal" else scalar
    if not isinstance(literal, Mapping) or set(literal) != {wrapper}:
        raise GraphQLError("UNSUPPORTED", extensions={"code": "UNSUPPORTED"})
    scalar_value = literal[wrapper]
    if scalar == "string" and isinstance(scalar_value, str):
        return scalar_value
    if scalar == "boolean" and isinstance(scalar_value, bool):
        return scalar_value
    if (
        scalar == "decimal"
        and isinstance(scalar_value, str)
        and re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", scalar_value)
    ):
        return scalar_value
    raise GraphQLError("UNSUPPORTED", extensions={"code": "UNSUPPORTED"})


def decode_node_key(
    codec: NodeCodec,
    prepared: AdmittedPreparedApi,
    opaque: str,
    records: Mapping[ElementRef, PreparedRecord],
) -> NodeKey | None:
    try:
        encoded = opaque.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        return None
    if len(encoded) > limit(prepared, "nodeIdBytes"):
        return None
    try:
        key = codec.decode(prepared.identity_namespace, opaque)
    except Exception:
        return None
    if not _valid_key_shape(key):
        return None
    record = records.get(key.record)
    if (
        record is None
        or key.key_id != record.key_id
        or len(key.components) != len(record.key_fields)
    ):
        return None
    return key


def _valid_node(value: NodeValue, key: NodeKey, fields: tuple[ElementRef, ...]) -> bool:
    return value.key == key and set(value.fields) == set(fields)


def encode_node_key(codec: NodeCodec, prepared: AdmittedPreparedApi, key: NodeKey) -> str:
    if not _valid_key_shape(key):
        raise GraphQLError("UNSUPPORTED", extensions={"code": "UNSUPPORTED"})
    try:
        value = codec.encode(prepared.identity_namespace, key)
        if type(value) is not str:
            raise TypeError("codec returned a non-string ID")
        encoded = value.encode("utf-8", errors="strict")
    except Exception as error:
        raise GraphQLError("UNSUPPORTED", extensions={"code": "UNSUPPORTED"}) from error
    if type(value) is not str or not encoded or len(encoded) > limit(prepared, "nodeIdBytes"):
        raise GraphQLError("LIMIT_EXCEEDED", extensions={"code": "LIMIT_EXCEEDED"})
    return value


def uses_introspection(document: Any) -> bool:
    for definition in document.definitions:
        selection_set = getattr(definition, "selection_set", None)
        stack = [selection_set] if selection_set is not None else []
        while stack:
            current = stack.pop()
            for selection in current.selections:
                if isinstance(selection, FieldNode) and selection.name.value in {
                    "__schema",
                    "__type",
                }:
                    return True
                if getattr(selection, "selection_set", None) is not None:
                    stack.append(selection.selection_set)
    return False


def _session(info: Any) -> RequestSession:
    return cast(RequestSession, info.context["session"])


def mount(prepared: AdmittedPreparedApi) -> str:
    return cast(str, prepared.host_profile["mount"])


def limit(prepared: AdmittedPreparedApi, name: str) -> int:
    limits = cast(Mapping[str, str], prepared.host_profile["limits"])
    value = limits.get(name)
    if value is None or not value.isdecimal():
        raise ValueError("API_MISMATCH")
    return int(value)


def integer_limits(prepared: AdmittedPreparedApi) -> dict[str, int]:
    limits = cast(Mapping[str, str], prepared.host_profile["limits"])
    return {name: limit(prepared, name) for name in limits}


def _valid_key_shape(key: object) -> bool:
    if not isinstance(key, NodeKey) or type(key) is not NodeKey:
        return False
    if type(key.record) is not ElementRef or not key.record.module or not key.record.element:
        return False
    if type(key.key_id) is not str or not key.key_id or type(key.components) is not tuple:
        return False
    return all(_valid_key_literal(value) for value in key.components)


def _valid_key_literal(value: object) -> bool:
    if not isinstance(value, Mapping):
        return False
    typed = cast(Mapping[str, object], value)
    if len(typed) != 1:
        return False
    tag, literal = next(iter(typed.items()))
    validators: dict[str, Callable[[object], bool]] = {
        "string": _valid_text,
        "boolean": _valid_boolean,
        "integer": _valid_integer,
        "decimal": _valid_decimal,
        "uuid": _valid_uuid,
        "date": _valid_nonempty_text,
        "timestamp": _valid_nonempty_text,
    }
    validator = validators.get(tag)
    return validator(literal) if validator is not None else False


def _valid_text(value: object) -> bool:
    return type(value) is str


def _valid_boolean(value: object) -> bool:
    return isinstance(value, bool)


def _valid_nonempty_text(value: object) -> bool:
    return type(value) is str and bool(value)


def _valid_integer(value: object) -> bool:
    return type(value) is str and re.fullmatch(r"-?(?:0|[1-9][0-9]*)", value) is not None


def _valid_decimal(value: object) -> bool:
    return (
        type(value) is str
        and re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", value) is not None
    )


def _valid_uuid(value: object) -> bool:
    return (
        type(value) is str
        and re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", value)
        is not None
    )
