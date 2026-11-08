"""Production projection admission for the explicitly supported read subset.

This module consumes UMF documents directly. It intentionally does not import or
reuse the experimental probe schema.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any, cast

from graphql import build_schema, lexicographic_sort_schema, print_schema
from umf import read_document, validate_document  # pyright: ignore[reportUnknownVariableType]

from lintel_build.errors import PreparationError
from lintel_build.model import PreparedRecord, project_records

_NAME = re.compile(r"^(?!__)[_A-Za-z][_0-9A-Za-z]*$")
NAME_PATTERN = _NAME
_SCALARS = {"string": "String", "boolean": "Boolean", "decimal": "Decimal"}
_RESERVED = {"Node", "Query", "Mutation", "PageInfo", "Decimal", "ID", "String", "Boolean"}
_HOST_LIMITS = {
    "defaultPage": (0, 25),
    "maxPage": (1, 100),
    "maxLookup": (1, 100),
    "relationshipBatch": (1, 100),
    "maxRelationshipHops": (1, 1),
    "maxDepth": (1, 8),
    "maxFieldOccurrences": (1, 256),
    "maxAliases": (1, 32),
    "maxCost": (1, 10000),
    "maxMutationFields": (1, 4),
    "maxConcurrentDispatch": (1, 8),
    "requestBytes": (1, 1048576),
    "responseBytes": (1, 8388608),
    "documentBytes": (1, 262144),
    "deadlineMs": (1, 30000),
    "nodeIdBytes": (1, 2048),
    "cursorBytes": (1, 4096),
    "invocationKeyBytes": (1, 128),
}
_REQUIRED = {"lintel.execution": "1", "node.refetch": "1", "read.consistency": "request-snapshot-1"}
_V2_OPAQUE_EXTENSION_PATHS = {
    "/vocabularies/umf.tables",
    "/vocabularies/umf.access",
}


def prepare_api(
    umf_source: bytes,
    dependencies: Sequence[tuple[str, bytes]],
    exposure: bytes,
    capabilities: Mapping[str, str],
    host_profile: Mapping[str, object],
    scalar_codec_profile: str,
) -> bytes:
    """Compile exact UMF/source bytes and explicit exposure to canonical inventory bytes."""
    source_bytes = bytes(umf_source)
    exposure_bytes = bytes(exposure)
    config = json_object(exposure_bytes, "INVALID_EXPOSURE")
    check_exposure_shape(config)
    profile = check_host(host_profile)
    caps = check_capabilities(
        capabilities, bool(config["connections"]), bool(config["mutations"]), host_profile
    )
    profile["binding"] = dict(caps)["binding.profile"]
    if not scalar_codec_profile or dict(caps).get("scalar.codec.profile") != scalar_codec_profile:
        raise PreparationError("UNSUPPORTED", "scalar.codec.profile")
    if config["connections"] or config["mutations"]:
        raise PreparationError("UNSUPPORTED", "selected operation binding profile")
    identity, model = read_umf(source_bytes)
    source_rows = [(identity, source_bytes)]
    for dependency_identity, dependency_bytes in dependencies:
        checked_identity, checked_model = read_umf(bytes(dependency_bytes))
        if dependency_identity != checked_identity or dependency_identity == identity:
            raise PreparationError("API_MISMATCH", "source dependency identity")
        source_rows.append((dependency_identity, bytes(dependency_bytes)))
        for key, value in checked_model.items():
            if key in model:
                raise PreparationError("AMBIGUOUS_IDENTITY", f"{key[0]}.{key[1]}")
            model[key] = value
    source_entries = tuple(
        sorted((name, hashlib.sha256(raw).hexdigest()) for name, raw in source_rows)
    )
    if len({name for name, _ in source_entries}) != len(source_entries):
        raise PreparationError("AMBIGUOUS_IDENTITY", "source dependency")
    records = project_records(config, model, dict(caps))
    sdl = render_sdl(records)
    schema = lexicographic_sort_schema(build_schema(sdl))
    sdl = print_schema(schema).rstrip() + "\n"
    schema_digest = hashlib.sha256(sdl.encode("utf-8")).hexdigest()
    scalar_profile = scalar_codec_profile
    api_digest = _api_digest(exposure_bytes, source_entries, caps, profile, scalar_profile, sdl)
    base: dict[str, object] = {
        "version": "lintel.prepared-api/1",
        "artifactId": api_digest,
        "application": config["application"],
        "identityNamespace": config["identityNamespace"],
        "exposureBase64": base64.b64encode(exposure_bytes).decode("ascii"),
        "exposureSha256": hashlib.sha256(exposure_bytes).hexdigest(),
        "sources": [{"identity": name, "sha256": digest} for name, digest in source_entries],
        "capabilities": [list(pair) for pair in caps],
        "hostProfile": {
            "mount": profile["mount"],
            "introspection": profile["introspection"],
            "limits": [list(pair) for pair in cast(Sequence[tuple[str, str]], profile["limits"])],
        },
        "bindingProfile": profile["binding"],
        "scalarCodecProfile": scalar_profile,
        "records": [record_json(record) for record in records],
        "sdl": sdl,
        "schemaDigest": schema_digest,
        "apiDigest": api_digest,
    }
    artifact_digest = hashlib.sha256(canonical_json(base)).hexdigest()
    base["artifactDigest"] = artifact_digest
    return canonical_json(base)


def _frame(value: bytes) -> bytes:
    return len(value).to_bytes(8, "big") + value


def canonical_json(value: Mapping[str, object]) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def record_json(record: PreparedRecord) -> dict[str, object]:
    return {
        "source": {"module": record.source.module, "element": record.source.element},
        "keyId": record.key_id,
        "keyFields": [
            {"module": field.module, "element": field.element} for field in record.key_fields
        ],
        "typeName": record.type_name,
        "lookup": {
            "module": record.lookup.module,
            "id": record.lookup.id,
            "kind": record.lookup.kind,
        },
        "fields": [
            {
                "source": {"module": field.source.module, "element": field.source.element},
                "name": field.name,
                "scalar": field.scalar,
                "nullable": field.nullable,
            }
            for field in record.fields
        ],
    }


def _api_digest(
    exposure: bytes,
    sources: Sequence[tuple[str, str]],
    capabilities: Sequence[tuple[str, str]],
    host_profile: Mapping[str, object],
    scalar_profile: str,
    sdl: str,
) -> str:
    limits = cast(Sequence[tuple[str, str]], host_profile["limits"])
    profile = tuple(
        sorted((*capabilities, *((f"host.limit.{key}", value) for key, value in limits)))
    )
    frames = [b"lintel.api/1", exposure]
    for identity, digest in sources:
        frames.extend((identity.encode("utf-8"), digest.encode("ascii")))
    frames.extend(
        (
            json.dumps(
                [list(pair) for pair in profile], ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8"),
            scalar_profile.encode("utf-8"),
            sdl.encode("utf-8"),
        )
    )
    return hashlib.sha256(b"".join(_frame(frame) for frame in frames)).hexdigest()


def json_object(raw: bytes, code: str) -> dict[str, Any]:
    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result

    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=object_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise PreparationError(code, "") from error
    if not isinstance(value, dict):
        raise PreparationError(code, "")
    return cast(dict[str, Any], value)


def check_exposure_shape(
    config: dict[str, Any],
    expected_format: str = "lintel.exposure/1",
    record_roots: bool = False,
    root_connections: bool = False,
) -> None:
    expected = {
        "format",
        "application",
        "identityNamespace",
        "records",
        "connections",
        "mutations",
    }
    if set(config) != expected:
        raise PreparationError("INVALID_EXPOSURE", "")
    if (
        config["format"] != expected_format
        or type(config["application"]) is not str
        or not config["application"]
        or len(config["application"]) > 128
        or type(config["identityNamespace"]) is not str
        or not config["identityNamespace"]
        or len(config["identityNamespace"]) > 128
    ):
        raise PreparationError("INVALID_EXPOSURE", "")
    for section in ("records", "connections", "mutations"):
        if not isinstance(config[section], list) or len(config[section]) > 64:
            raise PreparationError("INVALID_EXPOSURE", f"/{section}")
    if not config["records"]:
        raise PreparationError("INVALID_EXPOSURE", "/records")
    _check_exposure_items(config, record_roots, root_connections)


def _check_exposure_items(
    config: Mapping[str, Any], record_roots: bool = False, root_connections: bool = False
) -> None:
    for raw_record in cast(list[object], config["records"]):
        _check_record_exposure(raw_record, record_roots)
    _check_unsupported_sections(config, root_connections)


def _check_record_exposure(raw_record: object, record_roots: bool = False) -> None:
    record = _closed_object(
        raw_record,
        {"record", "key", "typeName", "lookup", "fields", "relationships"},
        "/records",
    )
    _check_ref_shape(record["record"], "/records/record")
    if type(record["key"]) is not str or not record["key"]:
        raise PreparationError("INVALID_EXPOSURE", "/records/key")
    type_name = record["typeName"]
    if not isinstance(type_name, str) or not _NAME.fullmatch(type_name):
        raise PreparationError("INVALID_EXPOSURE", "/records/typeName")
    _check_operation_shape(
        record["lookup"],
        "/records/lookup",
        ("record",) if record_roots else ("table", "action"),
    )
    fields = _bounded_array(record["fields"], 256, "/records/fields")
    relationships = _bounded_array(record["relationships"], 32, "/records/relationships")
    for raw_field in fields:
        selected = _closed_object(raw_field, {"field", "name"}, "/records/fields")
        _check_ref_shape(selected["field"], "/records/fields/field")
        if not isinstance(selected["name"], str) or not _NAME.fullmatch(selected["name"]):
            raise PreparationError("INVALID_EXPOSURE", "/records/fields/name")
    if relationships:
        raise PreparationError("UNSUPPORTED", "/records/relationships")


def _check_unsupported_sections(config: Mapping[str, Any], root_connections: bool = False) -> None:
    connection_keys = {"name", "record", "operation"}
    mutation_keys = {"name", "operation"}
    if root_connections:
        for raw_item in cast(list[object], config["connections"]):
            item = _closed_object(raw_item, {"name", "record"}, "/connections")
            if not isinstance(item["name"], str) or not _NAME.fullmatch(item["name"]):
                raise PreparationError("INVALID_EXPOSURE", "/connections/name")
            _check_ref_shape(item["record"], "/connections/record")
    else:
        for raw_item in cast(list[object], config["connections"]):
            item = _closed_object(raw_item, connection_keys, "/connections")
            _check_ref_shape(item["record"], "/connections/record")
            _check_operation_shape(item["operation"], "/connections/operation")
    for raw_item in cast(list[object], config["mutations"]):
        item = _closed_object(raw_item, mutation_keys, "/mutations")
        _check_operation_shape(item["operation"], "/mutations/operation")
    if config["mutations"] or config["connections"] and not root_connections:
        raise PreparationError("UNSUPPORTED", "selected operation binding profile")
    if root_connections and not config["connections"]:
        raise PreparationError("INVALID_EXPOSURE", "/connections")


def _bounded_array(value: object, maximum: int, pointer: str) -> list[object]:
    if not isinstance(value, list):
        raise PreparationError("INVALID_EXPOSURE", pointer)
    result = cast(list[object], value)
    if len(result) > maximum:
        raise PreparationError("INVALID_EXPOSURE", pointer)
    return result


def _closed_object(value: object, keys: set[str], pointer: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise PreparationError("INVALID_EXPOSURE", pointer)
    result = cast(dict[str, object], value)
    if set(result) != keys:
        raise PreparationError("INVALID_EXPOSURE", pointer)
    return result


def _check_ref_shape(value: object, pointer: str) -> None:
    ref = _closed_object(value, {"module", "element"}, pointer)
    if any(type(ref[name]) is not str or not ref[name] for name in ("module", "element")):
        raise PreparationError("INVALID_EXPOSURE", pointer)


def _check_operation_shape(
    value: object, pointer: str, allowed_kinds: tuple[str, ...] = ("table", "action")
) -> None:
    operation = _closed_object(value, {"module", "id", "kind"}, pointer)
    if (
        any(type(operation[name]) is not str or not operation[name] for name in ("module", "id"))
        or operation["kind"] not in allowed_kinds
    ):
        raise PreparationError("INVALID_EXPOSURE", pointer)


def check_host(value: Mapping[str, object]) -> dict[str, object]:
    if set(value) != {"format", "mount", "introspection", "limits"}:
        raise PreparationError("INVALID", "host profile")
    mount = value.get("mount")
    if (
        value.get("format") != "lintel.host/1"
        or not isinstance(mount, str)
        or not re.fullmatch(r"/(?:[A-Za-z0-9_-]+/)*graphql", mount)
    ):
        raise PreparationError("INVALID", "host profile")
    if not isinstance(value.get("introspection"), bool):
        raise PreparationError("INVALID", "host profile")
    limits = value.get("limits")
    if not isinstance(limits, Mapping):
        raise PreparationError("INVALID", "host limits")
    typed_limits = cast(Mapping[str, object], limits)
    if set(typed_limits) != set(_HOST_LIMITS):
        raise PreparationError("INVALID", "host limits")
    vals_raw: dict[str, object] = dict(typed_limits)
    if any(not isinstance(v, int) or isinstance(v, bool) for v in vals_raw.values()):
        raise PreparationError("INVALID", "host limits")
    vals = cast(dict[str, int], vals_raw)
    for name, (minimum, maximum) in _HOST_LIMITS.items():
        if not minimum <= vals[name] <= maximum:
            raise PreparationError("INVALID", f"host limits/{name}")
    if vals["defaultPage"] > vals["maxPage"] or vals["relationshipBatch"] > vals["maxLookup"]:
        raise PreparationError("INVALID", "host limit combination")
    return {
        "mount": mount,
        "introspection": value["introspection"],
        "limits": tuple(sorted((key, str(val)) for key, val in vals.items())),
    }


def check_capabilities(
    value: Mapping[str, str],
    needs_connection: bool,
    needs_command: bool,
    host_profile: Mapping[str, object],
) -> tuple[tuple[str, str], ...]:
    caps = dict(value)
    if not all(key and version for key, version in caps.items()):
        raise PreparationError("UNSUPPORTED", "capability snapshot")
    for key, expected in _REQUIRED.items():
        if caps.get(key) != expected:
            raise PreparationError("UNSUPPORTED", key)
    codec = caps.get("identity.codec", "")
    binding = caps.get("binding.profile", "")
    if not codec or not binding:
        raise PreparationError("UNSUPPORTED", "binding.profile")
    selected = _selected_capabilities(caps, needs_connection, needs_command)
    _require_binding_profiles(caps, selected, binding)
    _require_profile_limits(caps, host_profile, binding)
    return tuple(sorted(caps.items()))


def _selected_capabilities(
    caps: Mapping[str, str], needs_connection: bool, needs_command: bool
) -> list[str]:
    selected = [
        "lintel.execution",
        "node.refetch",
        "read.consistency",
        "identity.codec",
        "scalar.codec.profile",
    ]
    if needs_connection:
        if caps.get("connection.forward") != "edge-cursor-1":
            raise PreparationError("UNSUPPORTED", "connection.forward")
        selected.append("connection.forward")
    if needs_command:
        for key, version in (("command.outcome", "1"), ("command.observe", "1")):
            if caps.get(key) != version:
                raise PreparationError("UNSUPPORTED", key)
            selected.append(key)
    return selected


def _require_binding_profiles(caps: Mapping[str, str], selected: list[str], binding: str) -> None:
    for key in selected:
        if caps.get(f"{key}.binding.profile") != binding:
            raise PreparationError("UNSUPPORTED", f"{key}.binding.profile")


def _require_profile_limits(
    caps: Mapping[str, str], host_profile: Mapping[str, object], binding: str
) -> None:
    limits = cast(Mapping[str, object], host_profile["limits"])
    for profile_key, expected in limits.items():
        key = f"limit.{profile_key}"
        if key not in caps or not caps[key].isdigit() or int(caps[key]) != expected:
            raise PreparationError("UNSUPPORTED", key)
        if caps.get(f"{key}.binding.profile") != binding:
            raise PreparationError("UNSUPPORTED", f"{key}.binding.profile")


def read_umf(
    source: bytes, *, allow_unknown_extensions: bool = False
) -> tuple[str, dict[tuple[str, str], dict[str, Any]]]:
    try:
        doc = cast(Any, read_document(source.decode("utf-8")))
        result = cast(Any, validate_document(doc))
        unknown_extension_warnings = all(
            diagnostic.code == "UNKNOWN_EXTENSION"
            and diagnostic.severity == "warning"
            and diagnostic.path in _V2_OPAQUE_EXTENSION_PATHS
            for diagnostic in result.diagnostics
        )
        if (
            not result.valid
            or not result.complete
            and not (allow_unknown_extensions and result.diagnostics and unknown_extension_warnings)
        ):
            raise PreparationError("UNSUPPORTED", "UMF validation")
        raw = cast(dict[str, Any], doc.to_dict())
    except Exception as error:
        if isinstance(error, PreparationError):
            raise
        raise PreparationError("INVALID", "UMF source") from error
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for module in raw["modules"]:
        for element in module["elements"]:
            key = (module["id"], element["id"])
            if key in index:
                raise PreparationError("AMBIGUOUS_IDENTITY", f"{key[0]}.{key[1]}")
            index[key] = element
    identity = raw.get("id")
    if not isinstance(identity, str) or not identity:
        raise PreparationError("INVALID", "UMF identity")
    return identity, index


def render_sdl(records: tuple[PreparedRecord, ...]) -> str:
    defs = ["interface Node { id: ID! }"]
    for record in records:
        fields = ["id: ID!"]
        fields.extend(
            f"{field.name}: {_SCALARS[field.scalar]}{'' if field.nullable else '!'}"
            for field in record.fields
        )
        defs.append(f"type {record.type_name} implements Node {{ " + " ".join(fields) + " }")
    defs.extend(["type Query { node(id: ID!): Node nodes(ids: [ID!]!): [Node]! }"])
    if any(field.scalar == "decimal" for record in records for field in record.fields):
        defs.append("scalar Decimal")
    return "\n".join(defs) + "\n"
