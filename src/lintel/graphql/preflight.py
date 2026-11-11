"""GraphQL-core field collection and bounded read-cost preflight."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Protocol, cast

from graphql import (
    GraphQLEnumType,
    GraphQLField,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLNamedType,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLScalarType,
    GraphQLSchema,
    GraphQLUnionType,
    get_named_type,
)
from graphql.execution.collect_fields import (
    FieldDetails,
    FragmentDetails,
    collect_fields,
    collect_subfields,
)
from graphql.execution.values import VariableValues, get_argument_values
from graphql.language import (
    DocumentNode,
    FieldNode,
    FragmentDefinitionNode,
    OperationDefinitionNode,
)

from lintel.ports.values import ConnectionIntent
from lintel.projection.prepared import AdmittedPreparedApi, PreparedRecord
from lintel.projection.prepared_v3 import PreparedConnection


class _WrappedGraphQLType(Protocol):
    of_type: object


class BudgetFailure(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def preflight(
    schema: GraphQLSchema,
    document: DocumentNode,
    operation: OperationDefinitionNode,
    variables: VariableValues,
    limits: Mapping[str, int],
    connection_fields: frozenset[str] = frozenset(),
) -> None:
    root = schema.query_type if operation.operation.value == "query" else schema.mutation_type
    if root is None:
        raise BudgetFailure("INVALID")
    fragments = {
        name: FragmentDetails(definition=fragment)
        for name, fragment in schema_fragments(document).items()
    }
    collected = collect_fields(schema, fragments, variables, root, operation)
    dispatches = sum(
        any(detail.node.name.value in {"node", "nodes"} | connection_fields for detail in details)
        for details in collected.grouped_field_set.values()
    )
    if dispatches > limits["maxConcurrentDispatch"]:
        raise BudgetFailure("LIMIT_EXCEEDED")
    budget = _Budget(schema, fragments, variables, operation, limits, connection_fields)
    budget.walk(root, collected.grouped_field_set, 0)


def collect_connection_intents(
    schema: GraphQLSchema,
    document: DocumentNode,
    operation: OperationDefinitionNode,
    variables: VariableValues,
    prepared: AdmittedPreparedApi,
) -> tuple[ConnectionIntent, ...]:
    """Freeze active root connection calls after GraphQL coercion and validation."""
    if (
        prepared.version
        not in {"lintel.prepared-api/3", "lintel.prepared-api/4", "lintel.prepared-api/5"}
        or operation.operation.value != "query"
    ):
        return ()
    root = schema.query_type
    if root is None:
        raise BudgetFailure("INVALID")
    fragments = {
        name: FragmentDetails(definition=fragment)
        for name, fragment in schema_fragments(document).items()
    }
    collected = collect_fields(schema, fragments, variables, root, operation)
    routes = {route.name: route for route in prepared.generated_connections}
    records = {record.lookup: record for record in prepared.records}
    return tuple(
        _root_connection_intent(
            schema,
            fragments,
            variables,
            operation,
            root,
            response_key,
            details,
            routes,
            records,
            prepared,
        )
        for response_key, details in collected.grouped_field_set.items()
        if any(detail.node.name.value in routes for detail in details)
    )


def _root_connection_intent(
    schema: GraphQLSchema,
    fragments: dict[str, FragmentDetails],
    variables: VariableValues,
    operation: OperationDefinitionNode,
    root: GraphQLObjectType,
    response_key: str,
    details: list[FieldDetails],
    routes: Mapping[str, PreparedConnection],
    records: Mapping[object, PreparedRecord],
    prepared: AdmittedPreparedApi,
) -> ConnectionIntent:
    names = {detail.node.name.value for detail in details}
    if len(names) != 1:
        raise BudgetFailure("INVALID")
    field_name = next(iter(names))
    route = routes.get(field_name)
    record = records.get(route.lookup) if route is not None else None
    field = root.fields.get(field_name)
    if route is None or record is None or field is None:
        raise BudgetFailure("API_MISMATCH")
    args = get_argument_values(field, details[0].node, variables)
    if any(get_argument_values(field, item.node, variables) != args for item in details[1:]):
        raise BudgetFailure("INVALID")
    first, after = _page_arguments(prepared, args)
    selected_names = _connection_selected_field_names(
        schema, fragments, variables, operation, details
    )
    if prepared.version == "lintel.prepared-api/5":
        selected_names -= {
            route.name for route in prepared.relationships if route.source == record.source
        }
    names_by_field = {item.name: item.source for item in record.fields}
    if not selected_names <= set(names_by_field):
        raise BudgetFailure("API_MISMATCH")
    allowed = set(route.field_refs)
    selected_refs = tuple(
        sorted(names_by_field[name] for name in selected_names if names_by_field[name] in allowed)
    )
    if len(selected_refs) != len(selected_names):
        raise BudgetFailure("API_MISMATCH")
    return ConnectionIntent(
        response_key, field_name, route.lookup, MappingProxyType({}), first, after, selected_refs
    )


def _page_arguments(
    prepared: AdmittedPreparedApi, args: Mapping[str, object]
) -> tuple[int, str | None]:
    first = args.get("first", int(limit_value(prepared, "defaultPage")))
    after = args.get("after")
    if type(first) is not int:
        raise BudgetFailure("INVALID")
    if first < 0:
        raise BudgetFailure("INVALID")
    if first > int(limit_value(prepared, "maxPage")):
        raise BudgetFailure("LIMIT_EXCEEDED")
    if after is not None:
        if type(after) is not str:
            raise BudgetFailure("INVALID")
        try:
            encoded = after.encode("utf-8", errors="strict")
        except UnicodeEncodeError as error:
            raise BudgetFailure("INVALID_CURSOR") from error
        if not encoded:
            raise BudgetFailure("INVALID_CURSOR")
        if len(encoded) > int(limit_value(prepared, "cursorBytes")):
            raise BudgetFailure("LIMIT_EXCEEDED")
    return first, after


def _connection_selected_field_names(
    schema: GraphQLSchema,
    fragments: dict[str, FragmentDetails],
    variables: VariableValues,
    operation: OperationDefinitionNode,
    root_details: list[FieldDetails],
) -> set[str]:
    root_field_name = root_details[0].node.name.value
    query = schema.query_type
    if query is None:
        raise BudgetFailure("API_MISMATCH")
    connection_type = cast(GraphQLNamedType, get_named_type(query.fields[root_field_name].type))
    if not isinstance(connection_type, GraphQLObjectType):
        raise BudgetFailure("API_MISMATCH")
    grouped = collect_subfields(
        schema, fragments, variables, operation, connection_type, root_details
    ).grouped_field_set
    edges = [
        detail
        for details in grouped.values()
        for detail in details
        if detail.node.name.value == "edges"
    ]
    if not edges:
        return set()
    edge_type = cast(GraphQLNamedType, get_named_type(connection_type.fields["edges"].type))
    if not isinstance(edge_type, GraphQLObjectType):
        raise BudgetFailure("API_MISMATCH")
    edge_fields = collect_subfields(
        schema, fragments, variables, operation, edge_type, edges
    ).grouped_field_set
    nodes = [
        detail
        for details in edge_fields.values()
        for detail in details
        if detail.node.name.value == "node"
    ]
    if not nodes:
        return set()
    record_type = cast(GraphQLNamedType, get_named_type(edge_type.fields["node"].type))
    if not isinstance(record_type, GraphQLObjectType):
        raise BudgetFailure("API_MISMATCH")
    selected = collect_subfields(
        schema, fragments, variables, operation, record_type, nodes
    ).grouped_field_set
    return {
        detail.node.name.value
        for details in selected.values()
        for detail in details
        if detail.node.name.value not in {"id", "__typename"}
    }


def limit_value(prepared: AdmittedPreparedApi, name: str) -> str:
    limits = cast(Mapping[str, str], prepared.host_profile["limits"])
    return limits[name]


def schema_fragments(document: DocumentNode) -> dict[str, FragmentDefinitionNode]:
    return {
        definition.name.value: definition
        for definition in document.definitions
        if isinstance(definition, FragmentDefinitionNode)
    }


class _Budget:
    def __init__(
        self,
        schema: GraphQLSchema,
        fragments: dict[str, FragmentDetails],
        variables: VariableValues,
        operation: OperationDefinitionNode,
        limits: Mapping[str, int],
        connection_fields: frozenset[str] = frozenset(),
    ) -> None:
        self.schema = schema
        self.fragments = fragments
        self.variables = variables
        self.operation = operation
        self.limits = limits
        self.connection_fields = connection_fields
        self.occurrences = 0
        self.aliases = 0

    def walk(
        self,
        parent: GraphQLObjectType,
        grouped: Mapping[str, list[FieldDetails]],
        parent_depth: int,
    ) -> int:
        total = 0
        for details in grouped.values():
            nodes = [detail.node for detail in details]
            self.occurrences += len(nodes)
            self.aliases += sum(node.alias is not None for node in nodes)
            depth = parent_depth + 1
            if depth > self.limits["maxDepth"]:
                raise BudgetFailure("LIMIT_EXCEEDED")
            for node in nodes:
                field = parent.fields.get(node.name.value)
                if field is None:
                    continue
                children = self._child_cost(cast(object, field.type), details, depth)
                multiplier = self._multiplier(parent, node.name.value, field, node)
                total += 1 + multiplier * children
        self._check_count("maxFieldOccurrences", self.occurrences)
        self._check_count("maxAliases", self.aliases)
        self._check_count("maxCost", total)
        return total

    def _child_cost(self, output_type: object, details: list[FieldDetails], depth: int) -> int:
        if isinstance(output_type, GraphQLNonNull):
            wrapped = cast(_WrappedGraphQLType, output_type).of_type
            return self._child_cost(wrapped, details, depth)
        if isinstance(output_type, GraphQLList):
            wrapped = cast(_WrappedGraphQLType, output_type).of_type
            return self._child_cost(wrapped, details, depth)
        if isinstance(output_type, GraphQLObjectType):
            types = (output_type,)
        elif isinstance(output_type, (GraphQLInterfaceType, GraphQLUnionType)):
            types = tuple(self.schema.get_possible_types(output_type))
        elif isinstance(output_type, (GraphQLScalarType, GraphQLEnumType)):
            return 0
        else:
            return 0
        return max(
            (
                self.walk(
                    concrete,
                    collect_subfields(
                        self.schema,
                        self.fragments,
                        self.variables,
                        self.operation,
                        concrete,
                        details,
                    ).grouped_field_set,
                    depth,
                )
                for concrete in types
            ),
            default=0,
        )

    def _multiplier(
        self, parent: GraphQLObjectType, name: str, field: GraphQLField, node: FieldNode
    ) -> int:
        if parent.name == "Query" and name in self.connection_fields:
            args = get_argument_values(field, node, self.variables)
            first = args.get("first", self.limits["defaultPage"])
            return max(1, first) if type(first) is int else 1
        if parent.name != "Query" or name != "nodes":
            return 1
        args = get_argument_values(field, node, self.variables)
        ids = args.get("ids")
        if not isinstance(ids, list):
            return 1
        typed_ids = cast(list[object], ids)
        if len(typed_ids) > self.limits["maxLookup"]:
            raise BudgetFailure("LIMIT_EXCEEDED")
        return max(1, len(typed_ids))

    def _check_count(self, key: str, value: int) -> None:
        if value > self.limits[key]:
            raise BudgetFailure("LIMIT_EXCEEDED")
