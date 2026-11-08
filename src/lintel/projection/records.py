"""Closed prepared record projection decoding helpers."""

from __future__ import annotations

from typing import Literal, cast

from lintel.ports.values import ElementRef, OperationRef
from lintel.projection.prepared import (
    PreparedField,
    PreparedRecord,
    name_pattern,
)
from lintel.projection.prepared_wire import bool_value, string_value


def records_from_json(
    value: object, allowed_operation_kinds: tuple[str, ...] = ("table", "action")
) -> tuple[PreparedRecord, ...]:
    if not isinstance(value, list):
        raise ValueError("API_MISMATCH")
    records = tuple(_record(raw, allowed_operation_kinds) for raw in cast(list[object], value))
    if tuple(sorted(records, key=lambda record: record.type_name)) != records:
        raise ValueError("API_MISMATCH")
    if len({record.source for record in records}) != len(records):
        raise ValueError("API_MISMATCH")
    if len({record.type_name for record in records}) != len(records):
        raise ValueError("API_MISMATCH")
    if not records or any(not _valid_record(record) for record in records):
        raise ValueError("API_MISMATCH")
    return records


def _record(raw: object, allowed_operation_kinds: tuple[str, ...]) -> PreparedRecord:
    expected = {"source", "keyId", "keyFields", "typeName", "lookup", "fields"}
    if not isinstance(raw, dict):
        raise ValueError("API_MISMATCH")
    typed: dict[str, object] = dict(cast(dict[str, object], raw))
    if set(typed) != expected:
        raise ValueError("API_MISMATCH")
    raw_keys, raw_fields = typed["keyFields"], typed["fields"]
    if not isinstance(raw_keys, list) or not isinstance(raw_fields, list):
        raise ValueError("API_MISMATCH")
    return PreparedRecord(
        _ref(typed["source"]),
        string_value(typed, "keyId"),
        tuple(_ref(item) for item in cast(list[object], raw_keys)),
        string_value(typed, "typeName"),
        _operation(typed["lookup"], allowed_operation_kinds),
        tuple(_field(item) for item in cast(list[object], raw_fields)),
    )


def _field(value: object) -> PreparedField:
    expected = {"source", "name", "scalar", "nullable"}
    if not isinstance(value, dict):
        raise ValueError("API_MISMATCH")
    typed: dict[str, object] = dict(cast(dict[str, object], value))
    if set(typed) != expected:
        raise ValueError("API_MISMATCH")
    return PreparedField(
        _ref(typed["source"]),
        string_value(typed, "name"),
        string_value(typed, "scalar"),
        bool_value(typed, "nullable"),
    )


def _valid_record(record: PreparedRecord) -> bool:
    reserved = {"Node", "Query", "Mutation", "PageInfo", "Decimal"}
    if not name_pattern.fullmatch(record.type_name) or record.type_name in reserved:
        return False
    if not record.key_fields or len(set(record.key_fields)) != len(record.key_fields):
        return False
    if len({field.source for field in record.fields}) != len(record.fields):
        return False
    if len({field.name for field in record.fields}) != len(record.fields):
        return False
    return all(
        name_pattern.fullmatch(field.name)
        and field.name != "id"
        and field.scalar in {"string", "boolean", "decimal"}
        for field in record.fields
    )


def _ref(value: object) -> ElementRef:
    if not isinstance(value, dict):
        raise ValueError("API_MISMATCH")
    typed: dict[str, object] = dict(cast(dict[str, object], value))
    if set(typed) != {"module", "element"}:
        raise ValueError("API_MISMATCH")
    return ElementRef(string_value(typed, "module"), string_value(typed, "element"))


def _operation(value: object, allowed_kinds: tuple[str, ...]) -> OperationRef:
    if not isinstance(value, dict):
        raise ValueError("API_MISMATCH")
    typed: dict[str, object] = dict(cast(dict[str, object], value))
    if set(typed) != {"module", "id", "kind"}:
        raise ValueError("API_MISMATCH")
    kind = string_value(typed, "kind")
    if kind not in allowed_kinds:
        raise ValueError("API_MISMATCH")
    return OperationRef(
        string_value(typed, "module"),
        string_value(typed, "id"),
        cast(Literal["table", "action", "record"], kind),
    )
