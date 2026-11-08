"""Closed generated root-connection metadata for prepared API version three."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from lintel.ports.values import ElementRef, OperationRef
from lintel.projection.prepared_v2 import PreparedGeneratedRoot

if TYPE_CHECKING:
    from lintel.projection.prepared import PreparedRecord

CONNECTION_PROFILE = "connection.forward=edge-cursor-1"
READ_PROFILE = "weft.generated-read-algebra/5"
READ_PROFILE_V4 = "weft.generated-read-algebra/7"
ALLOWED_PROFILE = "umf.allowed-connection-fields/1"


@dataclass(frozen=True, slots=True)
class PreparedConnection:
    lookup: OperationRef
    name: str
    field_refs: tuple[ElementRef, ...]
    primary_key_field: ElementRef
    profile_digest: str
    profile_body: Mapping[str, object]
    read_profile: str = READ_PROFILE


def generated_connections_json(connections: Sequence[PreparedConnection]) -> bytes:
    return _canonical_json([_connection_json(item) for item in connections])


def allowed_field_profile_to_dict(connection: PreparedConnection) -> dict[str, object]:
    """Return a fresh JSON-compatible copy for native profile constructors."""
    body = _json_value(connection.profile_body)
    if not isinstance(body, dict):
        raise ValueError("API_MISMATCH")
    return cast(dict[str, object], body)


def generated_connections_from_json(
    value: object, *, expected_read_profile: str = READ_PROFILE
) -> tuple[PreparedConnection, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError("API_MISMATCH")
    parsed = tuple(_connection(item, expected_read_profile) for item in cast(list[object], value))
    identities = tuple((item.lookup.module, item.lookup.id) for item in parsed)
    if identities != tuple(sorted(identities)) or len(set(identities)) != len(identities):
        raise ValueError("API_MISMATCH")
    return parsed


def join_generated_connections(
    records: Sequence[PreparedRecord],
    roots: Sequence[PreparedGeneratedRoot],
    connections: Sequence[PreparedConnection],
    sources: Sequence[tuple[str, str]],
    scalar_codec_profile: str,
    *,
    expected_read_profile: str = READ_PROFILE,
) -> None:
    record_map = {(item.source.module, item.source.element): item for item in records}
    root_map = {(item.lookup.module, item.lookup.id): item for item in roots}
    connection_map = {(item.lookup.module, item.lookup.id): item for item in connections}
    if (
        not connection_map
        or not set(connection_map) <= set(record_map)
        or not set(connection_map) <= set(root_map)
    ):
        raise ValueError("API_MISMATCH")
    source_hashes = {digest for _identity, digest in sources}
    for identity, connection in connection_map.items():
        _join_one_connection(
            identity,
            connection,
            record_map[identity],
            root_map[identity],
            source_hashes,
            scalar_codec_profile,
            expected_read_profile,
        )


def _join_one_connection(
    identity: tuple[str, str],
    connection: PreparedConnection,
    record: PreparedRecord,
    root: PreparedGeneratedRoot,
    source_hashes: set[str],
    scalar_codec_profile: str,
    expected_read_profile: str,
) -> None:
    body = connection.profile_body
    fields = body.get("fields")
    if (
        connection.lookup != record.lookup
        or connection.lookup != root.lookup
        or connection.lookup.kind != "record"
        or connection.read_profile != expected_read_profile
        or root.source_digest not in source_hashes
        or body.get("version") != ALLOWED_PROFILE
        or body.get("scalarCodecProfile") != scalar_codec_profile
        or not isinstance(fields, (list, tuple))
    ):
        raise ValueError("API_MISMATCH")
    refs = tuple(_descriptor_ref(value) for value in cast(Sequence[object], fields))
    required = (*connection.field_refs, connection.primary_key_field)
    if len(set(refs)) != len(refs) or set(refs) != set(required):
        raise ValueError("API_MISMATCH")
    if (
        not set(connection.field_refs) <= {field.source for field in record.fields}
        or record.key_fields != (connection.primary_key_field,)
        or hashlib.sha256(_canonical_json(_json_value(body))).hexdigest()
        != connection.profile_digest
    ):
        raise ValueError("API_MISMATCH")
    _check_native_descriptors(record, connection, cast(Sequence[object], fields))


def _check_native_descriptors(
    record: PreparedRecord, connection: PreparedConnection, descriptors: Sequence[object]
) -> None:
    by_ref = {_descriptor_ref(value): cast(Mapping[str, object], value) for value in descriptors}
    for field_ref in connection.field_refs:
        selected = next((item for item in record.fields if item.source == field_ref), None)
        if selected is None or not _descriptor_matches(
            by_ref.get(field_ref), selected.scalar, selected.nullable
        ):
            raise ValueError("API_MISMATCH")
    if not _descriptor_matches(by_ref.get(connection.primary_key_field), "string", False):
        raise ValueError("API_MISMATCH")


def _descriptor_matches(
    descriptor: Mapping[str, object] | None, carrier: str, nullable: bool
) -> bool:
    if descriptor is None:
        return False
    output = descriptor.get("output")
    if not isinstance(output, Mapping):
        return False
    typed_output = cast(Mapping[str, object], output)
    return (
        descriptor.get("scalar") == carrier
        and descriptor.get("nullable") is nullable
        and typed_output.get("carrier") == carrier
        and typed_output.get("nullable") is nullable
    )


def _connection_json(item: PreparedConnection) -> dict[str, object]:
    return {
        "lookup": {"module": item.lookup.module, "id": item.lookup.id, "kind": item.lookup.kind},
        "fieldRefs": [_ref_json(value) for value in item.field_refs],
        "primaryKeyField": _ref_json(item.primary_key_field),
        "profile": {
            "connectionProfile": CONNECTION_PROFILE,
            "readProfile": item.read_profile,
            "allowedFieldProfile": {
                "version": ALLOWED_PROFILE,
                "digest": item.profile_digest,
                "body": _json_value(item.profile_body),
            },
        },
    }


def _connection(value: object, expected_read_profile: str = READ_PROFILE) -> PreparedConnection:
    if not isinstance(value, dict) or set(cast(dict[str, object], value)) != {
        "lookup",
        "fieldRefs",
        "primaryKeyField",
        "profile",
    }:
        raise ValueError("API_MISMATCH")
    typed = cast(dict[str, object], value)
    lookup = _lookup(typed["lookup"])
    fields = typed["fieldRefs"]
    if not isinstance(fields, list):
        raise ValueError("API_MISMATCH")
    digest, body = _profile(typed["profile"], expected_read_profile)
    refs = tuple(_ref(item) for item in cast(list[object], fields))
    if not refs or refs != tuple(sorted(set(refs))):
        raise ValueError("API_MISMATCH")
    return PreparedConnection(
        lookup,
        "",
        refs,
        _ref(typed["primaryKeyField"]),
        digest,
        cast(Mapping[str, object], _freeze(body)),
        expected_read_profile,
    )


def _lookup(value: object) -> OperationRef:
    if not isinstance(value, dict) or set(cast(dict[str, object], value)) != {
        "module",
        "id",
        "kind",
    }:
        raise ValueError("API_MISMATCH")
    typed = cast(dict[str, object], value)
    if typed.get("kind") != "record":
        raise ValueError("API_MISMATCH")
    return _operation(cast(dict[str, object], value))


def _profile(
    value: object, expected_read_profile: str = READ_PROFILE
) -> tuple[str, dict[str, object]]:
    if not isinstance(value, dict) or set(cast(dict[str, object], value)) != {
        "connectionProfile",
        "readProfile",
        "allowedFieldProfile",
    }:
        raise ValueError("API_MISMATCH")
    profile = cast(dict[str, object], value)
    if (
        profile.get("connectionProfile") != CONNECTION_PROFILE
        or profile.get("readProfile") != expected_read_profile
    ):
        raise ValueError("API_MISMATCH")
    allowed = profile.get("allowedFieldProfile")
    if not isinstance(allowed, dict) or set(cast(dict[str, object], allowed)) != {
        "version",
        "digest",
        "body",
    }:
        raise ValueError("API_MISMATCH")
    typed_allowed = cast(dict[str, object], allowed)
    digest, body = typed_allowed.get("digest"), typed_allowed.get("body")
    if (
        typed_allowed.get("version") != ALLOWED_PROFILE
        or not isinstance(body, dict)
        or set(cast(dict[str, object], body)) != {"version", "scalarCodecProfile", "fields"}
        or cast(dict[str, object], body).get("version") != ALLOWED_PROFILE
        or type(cast(dict[str, object], body).get("scalarCodecProfile")) is not str
        or not cast(dict[str, object], body).get("scalarCodecProfile")
        or type(digest) is not str
        or re.fullmatch(r"[0-9a-f]{64}", digest) is None
    ):
        raise ValueError("API_MISMATCH")
    typed_body = cast(dict[str, object], body)
    typed_digest = digest
    _validate_profile_body(typed_body, typed_digest)
    return typed_digest, typed_body


def _validate_profile_body(body: Mapping[str, object], digest: str) -> None:
    descriptors = body.get("fields")
    if not isinstance(descriptors, list) or not descriptors:
        raise ValueError("API_MISMATCH")
    ids: list[str] = []
    for descriptor in cast(list[object], descriptors):
        _validate_descriptor(descriptor)
        field_id = cast(dict[str, object], descriptor)["fieldId"]
        if type(field_id) is not str:
            raise ValueError("API_MISMATCH")
        ids.append(field_id)
    if ids != sorted(set(ids)) or hashlib.sha256(_canonical_json(body)).hexdigest() != digest:
        raise ValueError("API_MISMATCH")


def _validate_descriptor(value: object) -> None:
    if not isinstance(value, dict) or set(cast(dict[str, object], value)) != {
        "fieldId",
        "sourceField",
        "output",
        "scalar",
        "nullable",
    }:
        raise ValueError("API_MISMATCH")
    item = cast(dict[str, object], value)
    source, output = item.get("sourceField"), item.get("output")
    typed_source = cast(dict[str, object], source) if isinstance(source, dict) else {}
    typed_output = cast(dict[str, object], output) if isinstance(output, dict) else {}
    if (
        type(item.get("fieldId")) is not str
        or not item["fieldId"]
        or not isinstance(source, dict)
        or set(typed_source) != {"module", "element"}
        or not isinstance(output, dict)
        or set(typed_output) != {"carrier", "name", "nativeType", "nullable", "oid"}
        or type(typed_output.get("carrier")) is not str
        or not typed_output["carrier"]
        or type(typed_output.get("name")) is not str
        or not typed_output["name"]
        or not isinstance(typed_output.get("nativeType"), dict)
        or type(typed_output.get("nullable")) is not bool
        or type(typed_output.get("oid")) is not int
        or item.get("scalar") != typed_output.get("carrier")
        or item.get("nullable") != typed_output.get("nullable")
    ):
        raise ValueError("API_MISMATCH")
    _ref(typed_source)


def _descriptor_ref(value: object) -> ElementRef:
    if not isinstance(value, Mapping):
        raise ValueError("API_MISMATCH")
    return _ref(cast(Mapping[str, object], value).get("sourceField"))


def _ref(value: object) -> ElementRef:
    if not isinstance(value, Mapping) or set(cast(Mapping[str, object], value)) != {
        "module",
        "element",
    }:
        raise ValueError("API_MISMATCH")
    typed = cast(Mapping[str, object], value)
    module, element = typed.get("module"), typed.get("element")
    if type(module) is not str or not module or type(element) is not str or not element:
        raise ValueError("API_MISMATCH")
    return ElementRef(module, element)


def _operation(value: object) -> OperationRef:
    if not isinstance(value, dict):
        raise ValueError("API_MISMATCH")
    typed = cast(dict[str, object], value)
    if type(typed.get("module")) is not str or type(typed.get("id")) is not str:
        raise ValueError("API_MISMATCH")
    return OperationRef(cast(str, typed["module"]), cast(str, typed["id"]), "record")


def _ref_json(value: ElementRef) -> dict[str, str]:
    return {"module": value.module, "element": value.element}


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _json_value(value: object) -> object:
    if isinstance(value, Mapping):
        typed = cast(Mapping[str, object], value)
        return {key: _json_value(item) for key, item in typed.items()}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in cast(Sequence[object], value)]
    return value


def _freeze(value: object) -> object:
    if isinstance(value, dict):
        from types import MappingProxyType

        typed = cast(dict[str, object], value)
        return MappingProxyType({key: _freeze(item) for key, item in typed.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in cast(list[object], value))
    return value


def connection_names(exposure: bytes, records: Sequence[PreparedRecord]) -> dict[OperationRef, str]:
    value = json.loads(exposure.decode("utf-8", errors="strict"))
    if not isinstance(value, dict) or not isinstance(
        cast(dict[str, object], value).get("connections"), list
    ):
        raise ValueError("API_MISMATCH")
    by_source = {record.source: record for record in records}
    result: dict[OperationRef, str] = {}
    names: set[str] = set()
    for raw in cast(list[object], value["connections"]):
        if not isinstance(raw, dict) or set(cast(dict[str, object], raw)) != {"name", "record"}:
            raise ValueError("API_MISMATCH")
        item = cast(dict[str, object], raw)
        ref = item.get("record")
        if not isinstance(ref, dict) or set(cast(dict[str, object], ref)) != {"module", "element"}:
            raise ValueError("API_MISMATCH")
        source = _ref(cast(dict[str, object], ref))
        record = by_source.get(source)
        name = item.get("name")
        if (
            record is None
            or type(name) is not str
            or not re.fullmatch(r"^(?!__)[_A-Za-z][_0-9A-Za-z]*$", name)
            or name in {"node", "nodes"}
            or name in names
            or record.lookup in result
        ):
            raise ValueError("API_MISMATCH")
        names.add(name)
        result[record.lookup] = name
    return result


def connection_with_name(connection: PreparedConnection, name: str) -> PreparedConnection:
    return PreparedConnection(
        connection.lookup,
        name,
        connection.field_refs,
        connection.primary_key_field,
        connection.profile_digest,
        connection.profile_body,
        connection.read_profile,
    )


def sdl_v3(
    records: Sequence[PreparedRecord],
    connections: Sequence[PreparedConnection],
    host: Mapping[str, object],
) -> str:
    scalar_names = {
        "string": "String",
        "boolean": "Boolean",
        "integer": "BigInt",
        "decimal": "Decimal",
        "uuid": "UUID",
        "date": "Date",
        "timestamp": "ExactTimestamp",
    }
    definitions = ["interface Node { id: ID! }"]
    for record in records:
        fields = ["id: ID!"]
        fields.extend(
            f"{field.name}: {scalar_names[field.scalar]}{'!' if not field.nullable else ''}"
            for field in record.fields
        )
        definitions.append(f"type {record.type_name} implements Node {{ " + " ".join(fields) + " }")
    record_by_lookup = {record.lookup: record for record in records}
    for connection in connections:
        record = record_by_lookup.get(connection.lookup)
        if record is None:
            raise ValueError("API_MISMATCH")
        definitions.extend(
            (
                f"type {record.type_name}Edge {{ cursor: String! node: {record.type_name}! }}",
                f"type {record.type_name}Connection {{ edges: [{record.type_name}Edge!]! "
                "pageInfo: PageInfo! }",
            )
        )
    definitions.append(
        "type PageInfo { hasNextPage: Boolean! hasPreviousPage: Boolean! "
        "startCursor: String endCursor: String }"
    )
    query_fields = ["node(id: ID!): Node", "nodes(ids: [ID!]!): [Node]!"]
    limits = cast(Mapping[str, str], host["limits"])
    for connection in connections:
        record = record_by_lookup[connection.lookup]
        query_fields.append(
            f"{connection.name}(first: Int = {int(limits['defaultPage'])}, after: String): "
            f"{record.type_name}Connection!"
        )
    definitions.append("type Query { " + " ".join(query_fields) + " }")
    custom_scalars = {
        "integer": "BigInt",
        "decimal": "Decimal",
        "uuid": "UUID",
        "date": "Date",
        "timestamp": "ExactTimestamp",
    }
    used = {field.scalar for record in records for field in record.fields}
    definitions.extend(
        f"scalar {name}" for scalar, name in custom_scalars.items() if scalar in used
    )
    return "\n".join(definitions) + "\n"


def sdl_legacy(records: Sequence[PreparedRecord]) -> str:
    scalar_names = {
        "string": "String",
        "boolean": "Boolean",
        "decimal": "Decimal",
        "integer": "BigInt",
        "uuid": "UUID",
        "date": "Date",
        "timestamp": "ExactTimestamp",
    }
    definitions = ["interface Node { id: ID! }"]
    for record in records:
        fields = ["id: ID!"]
        fields.extend(
            f"{field.name}: {scalar_names[field.scalar]}{'!' if not field.nullable else ''}"
            for field in record.fields
        )
        definitions.append(f"type {record.type_name} implements Node {{ " + " ".join(fields) + " }")
    definitions.append("type Query { node(id: ID!): Node nodes(ids: [ID!]!): [Node]! }")
    scalars = sorted(
        {
            field.scalar
            for record in records
            for field in record.fields
            if field.scalar not in {"string", "boolean"}
        }
    )
    definitions.extend(f"scalar {scalar_names[name]}" for name in scalars)
    return "\n".join(definitions) + "\n"
