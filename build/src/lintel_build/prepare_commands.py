"""Derive selected scalar table commands from their exact source declarations."""

from collections.abc import Mapping
from typing import Any, cast

from lintel.projection.prepared_commands import parse_command
from lintel_build.errors import PreparationError
from lintel_build.prepare import json_object


def prepare_table_commands(
    source: bytes, selected: object, fields: Mapping[tuple[str, str], Mapping[str, Any]]
) -> tuple[dict[str, object], ...]:
    if type(selected) is not list:
        raise PreparationError("INVALID_EXPOSURE", "/mutations")
    items = cast(list[object], selected)
    if not 0 < len(items) <= 64:
        raise PreparationError("INVALID_EXPOSURE", "/mutations")
    document = json_object(source, "INVALID_EXPOSURE")
    rows = tuple(_command(document, item, fields) for item in items)
    if len({row["name"] for row in rows}) != len(rows):
        raise PreparationError("INVALID_EXPOSURE", "/mutations/name")
    return rows


def _command(
    document: Mapping[str, Any],
    value: object,
    fields: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, object]:
    if type(value) is not dict:
        raise PreparationError("INVALID_EXPOSURE", "/mutations")
    selected = cast(dict[str, Any], value)
    if set(selected) != {"name", "operation"}:
        raise PreparationError("INVALID_EXPOSURE", "/mutations")
    raw_operation = selected["operation"]
    if type(raw_operation) is not dict:
        raise PreparationError("INVALID_EXPOSURE", "/mutations/operation")
    operation = cast(dict[str, Any], raw_operation)
    if set(operation) != {"module", "id", "kind"} or operation["kind"] != "table":
        raise PreparationError("INVALID_EXPOSURE", "/mutations/operation")
    declared = _find_declaration(document, operation)
    parameters = [_parameter(param, fields) for param in declared["parameters"]]
    row: dict[str, object] = {**selected, "parameters": parameters}
    try:
        parse_command(row)
    except ValueError as error:
        raise PreparationError("INVALID_EXPOSURE", "/mutations") from error
    return row


def _find_declaration(
    document: Mapping[str, Any], operation: Mapping[str, Any]
) -> Mapping[str, Any]:
    matches = [
        command
        for module in document["modules"]
        if module["id"] == operation["module"]
        for command in module.get("extensions", {}).get("umf.tables", {}).get("commands", [])
        if command["id"] == operation["id"]
    ]
    if len(matches) != 1:
        raise PreparationError("UNSUPPORTED", "/mutations/operation")
    command = cast(Mapping[str, Any], matches[0])
    if (
        command.get("version") != "umf.table-operation/0.1"
        or command.get("replay") != "caller-key-required"
        or command.get("consistency") != "transaction"
        or command.get("batch") is not None
        or command["body"].get("maxRows") != 1
        or command["body"]["kind"] not in {"insert", "update", "delete", "upsert"}
    ):
        raise PreparationError("UNSUPPORTED", "recoverable single-row command profile")
    return command


def _parameter(
    param: Mapping[str, Any], fields: Mapping[tuple[str, str], Mapping[str, Any]]
) -> dict[str, object]:
    ref = param["field"]
    field = fields.get((ref["module"], ref["element"]))
    if (
        field is None
        or field.get("kind") != "field"
        or field.get("cardinality") != "one"
        or field.get("scalarType") not in {"string", "boolean", "decimal"}
        or field.get("nullability") not in {"required", "absent-allowed"}
    ):
        raise PreparationError("UNSUPPORTED", "/mutations/parameters")
    return {
        "name": param["id"],
        "scalar": field["scalarType"],
        "required": field["nullability"] == "required",
    }
