"""Build-only extraction of profile-pinned connection field descriptors."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import cast

from lintel.ports.values import ElementRef
from lintel_build.errors import PreparationError
from lintel_build.generated_roots import (
    CONNECTION_PROFILE,
    GeneratedManifestValue,
    GeneratedNativeTable,
    admit_generated,
    algebra_roots,
    check_manifest_source,
    element_ref,
    native_records,
    root_fields,
    root_for,
    verified_algebra,
    verify_bindings,
)
from lintel_build.model import PreparedRecord


def verify_generated_connection_profiles(
    manifest: object,
    files: object,
    trusted: object,
    target: object,
    source_identity: str,
    source_sha256: str,
    binding_profile: str,
    scalar_codec_profile: str,
    max_page: int,
    records: Sequence[PreparedRecord],
    selected_records: Sequence[ElementRef],
    *,
    expected_profile: str = CONNECTION_PROFILE,
) -> tuple[dict[str, object], ...]:
    """Join selected Record connections to exact-profile verifier descriptors."""
    executor = admit_generated(manifest, files, trusted, target)
    try:
        read_profile = executor.read_profile
        native = cast(GeneratedNativeTable, executor.native_table)
        executor_target = executor.target
    except Exception as error:
        raise PreparationError("API_MISMATCH", "generated connection profile") from error
    if read_profile != expected_profile:
        raise PreparationError("UNSUPPORTED", "generated connection read profile")
    _trusted_ref, _target_binding, inventory = verify_bindings(
        trusted, files, target, executor_target, native, source_sha256, binding_profile
    )
    algebra = verified_algebra(executor, files, inventory)
    manifest_value = cast(GeneratedManifestValue, manifest).value
    check_manifest_source(manifest_value, source_identity, source_sha256, records)
    roots = algebra_roots(algebra, expected_profile)
    native_rows = native_records(native.native_source, source_sha256)
    record_map = {(item.source.module, item.source.element): item for item in records}
    return tuple(
        _connection_row(
            ref, record_map, roots, native_rows, scalar_codec_profile, max_page, expected_profile
        )
        for ref in selected_records
    )


def _connection_row(
    ref: ElementRef,
    record_map: Mapping[tuple[str, str], PreparedRecord],
    roots: Mapping[str, object],
    native_rows: Mapping[tuple[str, str], frozenset[ElementRef]],
    scalar_codec_profile: str,
    max_page: int,
    read_profile: str,
) -> dict[str, object]:
    identity = (ref.module, ref.element)
    record = record_map.get(identity)
    if record is None:
        raise PreparationError("API_MISMATCH", "connection Record exposure")
    root = root_for(roots, identity, record)
    if identity not in native_rows:
        raise PreparationError("UNSUPPORTED", "native connection Record")
    key_field, key_field_id = _single_string_key(record, root)
    connection = _eligible_connection(root, key_field_id, max_page)
    outputs = _connection_outputs(connection)
    issued_fields = root_fields(root, record)
    allowed_fields = sorted({key_field, *(field.source for field in record.fields)})
    if not set(allowed_fields) <= native_rows[identity]:
        raise PreparationError("UNSUPPORTED", "native connection Fields")
    descriptors = [
        _connection_descriptor(source_field, record, key_field, issued_fields, outputs)
        for source_field in allowed_fields
    ]
    descriptors.sort(key=lambda item: cast(str, item["fieldId"]))
    body = {
        "version": "umf.allowed-connection-fields/1",
        "scalarCodecProfile": scalar_codec_profile,
        "fields": descriptors,
    }
    body_bytes = json.dumps(
        body, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return {
        "lookup": {"module": identity[0], "id": identity[1], "kind": "record"},
        "fieldRefs": [
            {"module": field.source.module, "element": field.source.element}
            for field in sorted(record.fields, key=lambda item: item.source)
        ],
        "primaryKeyField": {"module": key_field.module, "element": key_field.element},
        "profile": {
            "connectionProfile": "connection.forward=edge-cursor-1",
            "readProfile": read_profile,
            "allowedFieldProfile": {
                "version": "umf.allowed-connection-fields/1",
                "digest": hashlib.sha256(body_bytes).hexdigest(),
                "body": body,
            },
        },
    }


def _eligible_connection(
    root: Mapping[str, object], key_field_id: str, max_page: int
) -> Mapping[str, object]:
    raw = root.get("forwardConnection")
    support_value = root.get("forwardConnectionSupport")
    support = (
        cast(Mapping[str, object], support_value) if isinstance(support_value, Mapping) else None
    )
    if (
        not isinstance(raw, Mapping)
        or support is None
        or support.get("status") != "eligible"
        or support.get("profile") != "weft.generated-forward-connection/1"
    ):
        raise PreparationError("UNSUPPORTED", "generated forward connection")
    typed_support = support
    raw_connection = cast(Mapping[str, object], raw)
    connection = cast(Mapping[str, object], raw)
    key_order = (
        cast(Mapping[str, object], connection["key"])
        if isinstance(connection.get("key"), Mapping)
        else None
    )
    if (
        typed_support.get("profile") != "weft.generated-forward-connection/1"
        or raw_connection.get("profile") != "weft.generated-forward-connection/1"
        or not isinstance(connection.get("forward"), Mapping)
        or type(connection.get("maxFirst")) is not int
        or cast(int, connection["maxFirst"]) < max_page
        or not isinstance(key_order, Mapping)
        or key_order.get("fieldId") != key_field_id
        or key_order.get("direction") != "asc"
        or key_order.get("collation") != 'pg_catalog."C"'
    ):
        raise PreparationError("UNSUPPORTED", "generated forward connection profile")
    return connection


def _connection_outputs(connection: Mapping[str, object]) -> Mapping[str, Mapping[str, object]]:
    outputs = connection.get("fieldOutputs")
    if not isinstance(outputs, list):
        raise PreparationError("API_MISMATCH", "generated connection fields")
    result: dict[str, Mapping[str, object]] = {}
    for raw_item in cast(list[object], outputs):
        if not isinstance(raw_item, Mapping):
            continue
        item = cast(Mapping[str, object], raw_item)
        field_id = item.get("fieldId")
        if type(field_id) is str:
            result[field_id] = item
    return result


def _connection_descriptor(
    field: ElementRef,
    record: PreparedRecord,
    key_field: ElementRef,
    issued_fields: Mapping[str, object],
    outputs: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    field_id, output = _issued_field_output(field, issued_fields, outputs)
    carrier, nullable = output.get("carrier"), output.get("nullable")
    if (
        carrier != _source_scalar(field, record, key_field)
        or type(nullable) is not bool
        or type(output.get("name")) is not str
        or not cast(str, output.get("name"))
        or type(output.get("oid")) is not int
        or not isinstance(output.get("nativeType"), Mapping)
    ):
        raise PreparationError("UNSUPPORTED", "generated connection scalar profile")
    return {
        "fieldId": field_id,
        "sourceField": {"module": field.module, "element": field.element},
        "output": dict(output),
        "scalar": carrier,
        "nullable": nullable,
    }


def _single_string_key(
    record: PreparedRecord, root: Mapping[str, object]
) -> tuple[ElementRef, str]:
    if len(record.key_fields) != 1:
        raise PreparationError("UNSUPPORTED", "connection primary Key")
    field = record.key_fields[0]
    fields = root_fields(root, record)
    raw_connection = root.get("forwardConnection")
    outputs = (
        cast(Mapping[str, object], raw_connection).get("fieldOutputs")
        if isinstance(raw_connection, Mapping)
        else None
    )
    matches: list[tuple[str, Mapping[str, object]]] = []
    for raw_row in cast(Sequence[object], outputs or ()):
        if not isinstance(raw_row, Mapping):
            continue
        row = cast(Mapping[str, object], raw_row)
        field_id = row.get("fieldId")
        if type(field_id) is not str or field_id not in fields:
            continue
        field_value = fields[field_id]
        output_value = row.get("output")
        if (
            isinstance(field_value, Mapping)
            and element_ref(cast(Mapping[str, object], field_value).get("sourceField")) == field
            and isinstance(output_value, Mapping)
        ):
            matches.append((field_id, cast(Mapping[str, object], output_value)))
    if len(matches) != 1:
        raise PreparationError("UNSUPPORTED", "connection string primary Key")
    field_id, output = matches[0]
    if output.get("carrier") != "string" or output.get("nullable") is not False:
        raise PreparationError("UNSUPPORTED", "connection string primary Key")
    return field, field_id


def _issued_field_output(
    source_field: ElementRef,
    fields: Mapping[str, object],
    outputs: Mapping[str, Mapping[str, object]],
) -> tuple[str, Mapping[str, object]]:
    matches = [
        field_id
        for field_id, raw in fields.items()
        if isinstance(raw, Mapping)
        and element_ref(cast(Mapping[str, object], raw).get("sourceField")) == source_field
    ]
    if len(matches) != 1:
        raise PreparationError("UNSUPPORTED", "generated connection Field")
    field_id = matches[0]
    output_row = outputs.get(field_id)
    if not isinstance(output_row, Mapping):
        raise PreparationError("UNSUPPORTED", "generated connection Field output")
    output = output_row.get("output")
    if not isinstance(output, Mapping) or set(cast(Mapping[str, object], output)) != {
        "carrier",
        "name",
        "nativeType",
        "nullable",
        "oid",
    }:
        raise PreparationError("API_MISMATCH", "generated connection Field output")
    return field_id, cast(Mapping[str, object], output)


def _source_scalar(field: ElementRef, record: PreparedRecord, key_field: ElementRef) -> str:
    if field == key_field:
        return "string"
    selected = next((item for item in record.fields if item.source == field), None)
    if selected is None:
        raise PreparationError("API_MISMATCH", "generated connection Field")
    return selected.scalar


eligible_connection = _eligible_connection
