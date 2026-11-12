"""Project HTTP and named operation contracts from a trusted prepared inventory."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol, cast

from lintel.http import operation_name
from lintel.projection.prepared import (
    AdmittedPreparedApi,
    PreparedField,
    PreparedRecord,
)
from lintel.projection.prepared_commands import PreparedTableCommand
from lintel.projection.prepared_v3 import PreparedConnection
from lintel.projection.relationships import PreparedRelationship

Json = dict[str, object]
JSON_API = "application/vnd.api+json"
DECIMAL = r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$"


@dataclass(frozen=True, slots=True)
class Operation:
    name: str
    description: str
    input_schema: Json
    output_schema: Json

    def tool_schema(self) -> Json:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "outputSchema": self.output_schema,
        }


def _object(properties: Mapping[str, object], required: Iterable[str]) -> Json:
    return {
        "type": "object",
        "properties": dict(properties),
        "required": list(required),
        "additionalProperties": False,
    }


def _scalar(scalar: str, nullable: bool) -> Json:
    schemas: dict[str, Json] = {
        "string": {"type": "string"},
        "boolean": {"type": "boolean"},
        "decimal": {"type": "string", "pattern": DECIMAL},
    }
    schema = schemas[scalar]
    return {"anyOf": [schema, {"type": "null"}]} if nullable else schema


def _resource(record: PreparedRecord, fields: tuple[PreparedField, ...]) -> Json:
    attributes = {field.name: _scalar(field.scalar, field.nullable) for field in fields}
    if {"type", "id", "lid"} & attributes.keys():
        raise ValueError("selected field conflicts with JSON:API resource identity")
    return _object(
        {
            "type": {"type": "string", "const": record.type_name},
            "id": {"type": "string", "minLength": 1},
            "attributes": _object(attributes, attributes),
        },
        ("type", "id", "attributes"),
    )


def _get(record: PreparedRecord) -> Operation:
    return Operation(
        "get_" + operation_name(record.type_name),
        f"Refetch an authorized {record.type_name} by opaque identifier.",
        _object({"id": {"type": "string", "minLength": 1}}, ("id",)),
        _object({"data": _resource(record, record.fields)}, ("data",)),
    )


def _list(record: PreparedRecord, connection: PreparedConnection, max_page: int) -> Operation:
    fields = tuple(field for field in record.fields if field.source in connection.field_refs)
    return Operation(
        "list_" + operation_name(connection.name),
        f"Read one forward page of authorized {record.type_name} resources.",
        _object(
            {
                "page[size]": {"type": "integer", "minimum": 1, "maximum": max_page},
                "page[after]": {"type": "string", "minLength": 1},
            },
            ("page[size]",),
        ),
        _object(
            {
                "data": {"type": "array", "items": _resource(record, fields)},
                "links": _object({"next": {"type": ["string", "null"]}}, ("next",)),
            },
            ("data", "links"),
        ),
    )


def _with_relationships(
    operation: Operation,
    record: PreparedRecord,
    records: tuple[PreparedRecord, ...],
    relationships: tuple[PreparedRelationship, ...],
) -> Operation:
    routes = tuple(route for route in relationships if route.source == record.source)
    if not routes:
        return operation
    source = cast(Json, operation.output_schema["properties"])
    data = cast(Json, source["data"])
    item = cast(Json, data.get("items", data))
    properties = cast(Json, item["properties"])
    required = cast(list[str], item["required"])
    targets = {r.source: r for r in records}
    linkage = _object({"type": {"type": "string"}, "id": {"type": "string"}}, ("type", "id"))
    properties["relationships"] = _object(
        {
            route.name: _object({"data": {"anyOf": [linkage, {"type": "null"}]}}, ("data",))
            for route in routes
        },
        (),
    )
    required.append("relationships")
    included = [
        _resource(targets[ref], targets[ref].fields)
        for ref in dict.fromkeys(r.target for r in routes)
    ]
    source["included"] = {"type": "array", "items": {"anyOf": included}}
    inputs = cast(Json, operation.input_schema["properties"])
    inputs["include"] = {"type": "string", "enum": [route.name for route in routes]}
    return operation


def _command(command: PreparedTableCommand, *, observe: bool) -> Operation:
    fields: Json = {
        param.name: _scalar(param.scalar, not param.required) for param in command.parameters
    }
    fields["invocationKey"] = {"type": "string", "minLength": 1}
    if not observe:
        fields["confirmation"] = {"type": ["string", "null"]}
    required = ["invocationKey", *(p.name for p in command.parameters if p.required)]
    label = "Observe the original outcome of" if observe else "Invoke the declared command"
    return Operation(
        ("observe_" if observe else "") + operation_name(command.name),
        f"{label} {command.name}.",
        _object(fields, required),
        _outcome(observe=observe),
    )


def _outcome(*, observe: bool) -> Json:
    status = (
        ("recovered", "not-observed", "rejected")
        if observe
        else ("applied", "recovered", "unknown", "rejected")
    )
    properties = {
        "status": {"type": "string", "enum": list(status)},
        "invocationKey": {"type": "string"},
        "durability": {
            "type": "string",
            "enum": ["committed", "pending-caller-commit", "unknown", "none"],
        },
        "receipt": {"type": ["string", "null"]},
        "affectedIds": {"type": "array", "items": {"type": "string"}},
        "code": {"type": ["string", "null"]},
        "confirmation": {"type": ["string", "null"]},
    }
    return _object(properties, properties)


def _http(
    operation: Operation, *, method: str, media: str, parameter_location: str = "query"
) -> Json:
    spec: Json = {
        "operationId": operation.name,
        "description": operation.description,
        "responses": {
            "200": {
                "description": "Authorized result",
                "content": {media: {"schema": operation.output_schema}},
            },
        },
    }
    header = {
        "name": "x-lintel-api",
        "in": "header",
        "required": True,
        "schema": {"type": "string"},
    }
    spec["parameters"] = [header]
    if method == "post":
        spec["requestBody"] = {
            "required": True,
            "content": {"application/json": {"schema": operation.input_schema}},
        }
    else:
        properties = cast(Mapping[str, object], operation.input_schema["properties"])
        required = cast(list[str], operation.input_schema["required"])
        spec["parameters"] = [
            header,
            *[
                {
                    "name": key,
                    "in": "query" if key == "include" else parameter_location,
                    "required": key in required,
                    "schema": schema,
                }
                for key, schema in properties.items()
            ],
        ]
    return {method: spec}


class _Inventory(Protocol):
    @property
    def version(self) -> str: ...
    @property
    def records(self) -> tuple[PreparedRecord, ...]: ...
    @property
    def generated_connections(self) -> tuple[PreparedConnection, ...]: ...
    @property
    def relationships(self) -> tuple[PreparedRelationship, ...]: ...
    @property
    def commands(self) -> tuple[PreparedTableCommand, ...]: ...
    @property
    def host_profile(self) -> Mapping[str, object]: ...
    @property
    def api_digest(self) -> str: ...


def project_http(prepared: AdmittedPreparedApi) -> tuple[Json, tuple[Json, ...]]:
    """Generate interface descriptions. Runtime dispatch requires a separate host binding."""
    if type(prepared) is not AdmittedPreparedApi:
        raise ValueError("HTTP projection requires an admitted prepared API /5")
    inventory = cast(_Inventory, prepared)
    if inventory.version != "lintel.prepared-api/5":
        raise ValueError("HTTP projection requires an admitted prepared API /5")
    limits = cast(Mapping[str, str], inventory.host_profile["limits"])
    return _project(
        inventory.records,
        inventory.generated_connections,
        inventory.commands,
        int(limits["maxPage"]),
        inventory.api_digest,
        inventory.relationships,
    )


def _project(
    records: tuple[PreparedRecord, ...],
    connections: tuple[PreparedConnection, ...],
    commands: tuple[PreparedTableCommand, ...],
    max_page: int,
    api_digest: str,
    relationships: tuple[PreparedRelationship, ...] = (),
) -> tuple[Json, tuple[Json, ...]]:
    paths: dict[str, Json] = {}
    operations: dict[str, Operation] = {}
    by_lookup = {record.lookup: record for record in records}

    def add(
        path: str, method: str, operation: Operation, parameter_location: str = "query"
    ) -> None:
        if operation.name in operations or path in paths:
            raise ValueError("ambiguous projected HTTP operation")
        operations[operation.name] = operation
        media = JSON_API if method == "get" else "application/json"
        paths[path] = _http(
            operation, method=method, media=media, parameter_location=parameter_location
        )

    def read(operation: Operation, record: PreparedRecord) -> Operation:
        return _with_relationships(operation, record, records, relationships)

    for record in records:
        add(f"/records/{record.type_name}/{{id}}", "get", read(_get(record), record), "path")
    for connection in connections:
        add(
            f"/collections/{connection.name}",
            "get",
            read(
                _list(by_lookup[connection.lookup], connection, max_page),
                by_lookup[connection.lookup],
            ),
        )
    for command in commands:
        for observe in (False, True):
            operation = _command(command, observe=observe)
            add("/operations/" + operation.name, "post", operation)

    return {
        "openapi": "3.1.0",
        "info": {"title": "Lintel prepared HTTP API", "version": api_digest},
        "paths": paths,
    }, tuple(operation.tool_schema() for operation in operations.values())
