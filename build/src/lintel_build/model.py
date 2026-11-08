"""UMF Record/Key/Field resolution for the bounded production projection."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, cast

from lintel.ports.values import ElementRef, OperationRef
from lintel_build.errors import PreparationError

_NAME = re.compile(r"^(?!__)[_A-Za-z][_0-9A-Za-z]*$")
_SCALARS = {"string", "boolean", "decimal"}
_RESERVED = {"Node", "Query", "Mutation", "PageInfo", "Decimal", "ID", "String", "Boolean"}


@dataclass(frozen=True, slots=True)
class PreparedField:
    source: ElementRef
    name: str
    scalar: str
    nullable: bool


@dataclass(frozen=True, slots=True)
class PreparedRecord:
    source: ElementRef
    key_id: str
    key_fields: tuple[ElementRef, ...]
    type_name: str
    lookup: OperationRef
    fields: tuple[PreparedField, ...]


def _ref(value: object, keys: set[str], pointer: str) -> ElementRef:
    if not isinstance(value, dict):
        raise PreparationError("INVALID_EXPOSURE", pointer)
    typed = cast(dict[str, object], value)
    module, element = typed.get("module"), typed.get("element")
    if (
        set(typed) != keys
        or type(module) is not str
        or not module
        or type(element) is not str
        or not element
    ):
        raise PreparationError("INVALID_EXPOSURE", pointer)
    return ElementRef(module, element)


def _operation(
    value: object,
    pointer: str,
    capabilities: Mapping[str, str],
    source_record: ElementRef | None = None,
) -> OperationRef:
    if not isinstance(value, dict):
        raise PreparationError("INVALID_EXPOSURE", pointer)
    typed = cast(dict[str, object], value)
    if set(typed) != {"module", "id", "kind"} or typed.get("kind") not in {
        "table",
        "action",
        "record",
    }:
        raise PreparationError("INVALID_EXPOSURE", pointer)
    module, identifier, kind = typed.get("module"), typed.get("id"), typed.get("kind")
    if (
        type(module) is not str
        or not module
        or type(identifier) is not str
        or not identifier
        or type(kind) is not str
        or kind == "record"
        and (
            source_record is None
            or module != source_record.module
            or identifier != source_record.element
        )
        or kind in {"table", "action"}
        and source_record is not None
    ):
        raise PreparationError("INVALID_EXPOSURE", pointer)
    identity = "/".join(_pointer(item) for item in (module, identifier, kind))
    binding = capabilities.get(f"operation.binding/{identity}")
    if not binding or binding != capabilities.get("binding.profile"):
        raise PreparationError("UNSUPPORTED", pointer)
    return OperationRef(module, identifier, cast(Literal["table", "action", "record"], kind))


def _pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _prepare_record(
    index: int,
    item: dict[str, Any],
    model: dict[tuple[str, str], dict[str, Any]],
    capabilities: Mapping[str, str],
    types: set[str],
    source_seen: set[ElementRef],
    generated_record_root: bool = False,
) -> PreparedRecord:
    pointer = f"/records/{index}"
    record_ref, record = _record_declaration(item, model, pointer, source_seen)
    type_name = _type_name(item, pointer, types)
    key_id, key_fields = _record_key(
        item,
        record,
        model,
        pointer,
        allow_composite=generated_record_root,
        string_key_only=generated_record_root,
    )
    fields = _record_fields(item, record, model, pointer)
    if item["relationships"]:
        raise PreparationError("UNSUPPORTED", f"{pointer}/relationships")
    operation = _operation(
        item.get("lookup"),
        pointer + "/lookup",
        capabilities,
        record_ref if generated_record_root else None,
    )
    return PreparedRecord(record_ref, key_id, key_fields, type_name, operation, fields)


def _record_declaration(
    item: Mapping[str, Any],
    model: dict[tuple[str, str], dict[str, Any]],
    pointer: str,
    seen: set[ElementRef],
) -> tuple[ElementRef, dict[str, Any]]:
    record_ref = _ref(item.get("record"), {"module", "element"}, pointer + "/record")
    if record_ref in seen:
        raise PreparationError("AMBIGUOUS_IDENTITY", pointer + "/record")
    seen.add(record_ref)
    record = model.get((record_ref.module, record_ref.element))
    allowed = {"id", "name", "kind", "members", "keys", "extensions"}
    if (
        not record
        or record.get("kind") != "record"
        or record.get("extensions")
        or set(record) - allowed
    ):
        raise PreparationError("UNSUPPORTED", pointer + "/record")
    return record_ref, record


def _type_name(item: Mapping[str, Any], pointer: str, types: set[str]) -> str:
    value = item.get("typeName")
    if not isinstance(value, str) or not _NAME.fullmatch(value) or value in types:
        raise PreparationError("NAME_COLLISION", pointer + "/typeName")
    types.add(value)
    return value


def _record_key(
    item: Mapping[str, Any],
    record: Mapping[str, Any],
    model: dict[tuple[str, str], dict[str, Any]],
    pointer: str,
    *,
    allow_composite: bool = False,
    string_key_only: bool = False,
) -> tuple[str, tuple[ElementRef, ...]]:
    key_id = item.get("key")
    if not isinstance(key_id, str) or not key_id:
        raise PreparationError("INVALID_EXPOSURE", pointer + "/key")
    key_defs = record.get("keys", [])
    if not isinstance(key_defs, list):
        raise PreparationError("UNSUPPORTED", pointer + "/key")
    typed_keys: list[dict[str, Any]] = []
    for raw_key in cast(list[object], key_defs):
        if isinstance(raw_key, dict):
            typed_keys.append(cast(dict[str, Any], raw_key))
    key_def = next((key for key in typed_keys if key.get("id") == key_id), None)
    if key_def is None:
        raise PreparationError("UNSUPPORTED", pointer + "/key")
    key_values = key_def.get("fields")
    if not isinstance(key_values, list):
        raise PreparationError("UNSUPPORTED", pointer + "/key")
    typed_key_values = cast(list[object], key_values)
    if not typed_key_values or len(typed_key_values) > 1 and not allow_composite:
        raise PreparationError("UNSUPPORTED", pointer + "/key")
    key_fields = tuple(
        _ref(value, {"module", "element"}, pointer + "/key") for value in typed_key_values
    )
    if len(set(key_fields)) != len(key_fields):
        raise PreparationError("AMBIGUOUS_IDENTITY", pointer + "/key")
    for key_field in key_fields:
        _required_key_field(key_field, model, pointer, string_only=string_key_only)
    return key_id, key_fields


def _required_key_field(
    ref: ElementRef,
    model: dict[tuple[str, str], dict[str, Any]],
    pointer: str,
    *,
    string_only: bool = False,
) -> None:
    field = model.get((ref.module, ref.element))
    supported_members = {
        "id",
        "name",
        "kind",
        "scalarType",
        "cardinality",
        "nullability",
        "extensions",
        "facets",
    }
    if (
        not field
        or field.get("kind") != "field"
        or field.get("scalarType") not in ({"string"} if string_only else _SCALARS)
        or field.get("extensions")
        or set(field) - supported_members
        or field.get("cardinality") != "one"
        or field.get("nullability") != "required"
    ):
        raise PreparationError("UNSUPPORTED", pointer + "/key")


def _record_fields(
    item: Mapping[str, Any],
    record: Mapping[str, Any],
    model: dict[tuple[str, str], dict[str, Any]],
    pointer: str,
) -> tuple[PreparedField, ...]:
    raw_members = record.get("members", [])
    members_list = cast(list[dict[str, Any]], raw_members)
    members = {ElementRef(member["module"], member["element"]) for member in members_list}
    seen = {"id"}
    seen_sources: set[ElementRef] = set()
    fields = [
        _prepare_field(selection, index, members, model, pointer, seen, seen_sources)
        for index, selection in enumerate(item["fields"])
    ]
    if not fields:
        raise PreparationError("INVALID_EXPOSURE", pointer + "/fields")
    return tuple(sorted(fields, key=lambda field: field.name))


def _prepare_field(
    selection: Mapping[str, Any],
    index: int,
    members: set[ElementRef],
    model: dict[tuple[str, str], dict[str, Any]],
    pointer: str,
    names: set[str],
    seen_sources: set[ElementRef],
) -> PreparedField:
    field_pointer = f"{pointer}/fields/{index}"
    ref = _ref(selection.get("field"), {"module", "element"}, field_pointer + "/field")
    name = selection.get("name")
    if (
        ref not in members
        or ref in seen_sources
        or not isinstance(name, str)
        or not _NAME.fullmatch(name)
        or name in names
    ):
        raise PreparationError("NAME_COLLISION", field_pointer)
    names.add(name)
    seen_sources.add(ref)
    field = model.get((ref.module, ref.element))
    if not field or field.get("kind") != "field" or field.get("extensions"):
        raise PreparationError("UNSUPPORTED", field_pointer)
    scalar = field.get("scalarType")
    supported = {
        "id",
        "name",
        "kind",
        "scalarType",
        "cardinality",
        "nullability",
        "extensions",
        "facets",
    }
    if (
        scalar not in _SCALARS
        or field.get("cardinality") != "one"
        or field.get("nullability") != "required"
        or set(field) - supported
    ):
        raise PreparationError("UNSUPPORTED", field_pointer)
    facets = field.get("facets", {})
    if not isinstance(facets, dict):
        raise PreparationError("UNSUPPORTED", field_pointer)
    typed_facets = cast(dict[str, Any], facets)
    if typed_facets and (scalar != "decimal" or set(typed_facets) - {"precision", "scale"}):
        raise PreparationError("UNSUPPORTED", field_pointer)
    return PreparedField(ref, name, scalar, False)


def project_records(
    config: dict[str, Any],
    model: dict[tuple[str, str], dict[str, Any]],
    capabilities: Mapping[str, str],
    generated_record_roots: bool = False,
) -> tuple[PreparedRecord, ...]:
    types: set[str] = set(_RESERVED)
    source_seen: set[ElementRef] = set()
    records = [
        _prepare_record(
            index, item, model, capabilities, types, source_seen, generated_record_roots
        )
        for index, item in enumerate(config["records"])
    ]
    return tuple(sorted(records, key=lambda record: record.type_name))
