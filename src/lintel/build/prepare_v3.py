"""Strict generated Record-root connection API issuer for Weft read algebra `/5`."""

from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import cast

from graphql import build_schema, lexicographic_sort_schema, print_schema

from lintel.build.errors import PreparationError
from lintel.build.generated_connections import verify_generated_connection_profiles
from lintel.build.generated_roots import CONNECTION_PROFILE, verify_generated_roots
from lintel.build.model import PreparedRecord, project_records
from lintel.build.prepare import (
    NAME_PATTERN,
    canonical_json,
    check_capabilities,
    check_exposure_shape,
    check_host,
    json_object,
    read_umf,
    record_json,
)
from lintel.build.prepare_v2 import check_generated_bindings
from lintel.node_id import PROFILE as NODE_ID_PROFILE
from lintel.ports.values import OperationRef
from lintel.projection.prepared_v2 import PreparedGeneratedRoot, generated_roots_json


def prepare_api_v3(
    umf_source: bytes,
    dependencies: Sequence[tuple[str, bytes]],
    exposure: bytes,
    capabilities: Mapping[str, str],
    host_profile: Mapping[str, object],
    scalar_codec_profile: str,
    generated_manifest: object,
    generated_files: object,
    generated_trust: object,
    generated_target: object,
) -> bytes:
    """Issue a `/3` API only from strict `/5` verifier-issued connection roots."""
    source_bytes, exposure_bytes = bytes(umf_source), bytes(exposure)
    config = json_object(exposure_bytes, "INVALID_EXPOSURE")
    check_exposure_shape(config, "lintel.exposure/3", record_roots=True, root_connections=True)
    profile = check_host(host_profile)
    caps = check_capabilities(capabilities, True, False, host_profile)
    cap_map = dict(caps)
    if cap_map.get("identity.codec") != NODE_ID_PROFILE:
        raise PreparationError("UNSUPPORTED", "identity.codec")
    profile["binding"] = cap_map["binding.profile"]
    if not scalar_codec_profile or cap_map.get("scalar.codec.profile") != scalar_codec_profile:
        raise PreparationError("UNSUPPORTED", "scalar.codec.profile")
    identity, model = read_umf(source_bytes, allow_unknown_extensions=True)
    source_rows = [(identity, source_bytes)]
    for dependency_identity, dependency_bytes in dependencies:
        checked_identity, checked_model = read_umf(
            bytes(dependency_bytes), allow_unknown_extensions=True
        )
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
    if len({name for name, _digest in source_entries}) != len(source_entries):
        raise PreparationError("AMBIGUOUS_IDENTITY", "source dependency")
    records = project_records(config, model, cap_map, generated_record_roots=True)
    selected = _connection_declarations(config, records)
    source_digest = hashlib.sha256(source_bytes).hexdigest()
    limit_profile = cast(Mapping[str, int], host_profile["limits"])
    roots = verify_generated_roots(
        generated_manifest,
        generated_files,
        generated_trust,
        generated_target,
        identity,
        source_digest,
        cap_map["binding.profile"],
        records,
        expected_profile=CONNECTION_PROFILE,
    )
    connection_rows = tuple(
        sorted(
            verify_generated_connection_profiles(
                generated_manifest,
                generated_files,
                generated_trust,
                generated_target,
                identity,
                source_digest,
                cap_map["binding.profile"],
                scalar_codec_profile,
                limit_profile["maxPage"],
                records,
                tuple(record.source for _name, record in selected),
            ),
            key=lambda row: (
                cast(Mapping[str, str], row["lookup"])["module"],
                cast(Mapping[str, str], row["lookup"])["id"],
            ),
        )
    )
    check_generated_bindings(roots, cap_map, profile["binding"])
    _check_connection_names(selected, records)
    sdl = _render_sdl(records, selected, limit_profile["defaultPage"])
    sdl = print_schema(lexicographic_sort_schema(build_schema(sdl))).rstrip() + "\n"
    api_digest = _api_digest_v3(
        exposure_bytes,
        source_entries,
        caps,
        profile,
        scalar_codec_profile,
        roots,
        connection_rows,
        sdl,
    )
    schema_digest = hashlib.sha256(sdl.encode("utf-8")).hexdigest()
    base: dict[str, object] = {
        "version": "lintel.prepared-api/3",
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
        "scalarCodecProfile": scalar_codec_profile,
        "records": [record_json(record) for record in records],
        "generatedRoots": list(roots),
        "generatedConnections": list(connection_rows),
        "sdl": sdl,
        "schemaDigest": schema_digest,
        "apiDigest": api_digest,
    }
    base["artifactDigest"] = hashlib.sha256(canonical_json(base)).hexdigest()
    return canonical_json(base)


def _connection_declarations(
    config: Mapping[str, object], records: Sequence[PreparedRecord]
) -> tuple[tuple[str, PreparedRecord], ...]:
    record_map = {(item.source.module, item.source.element): item for item in records}
    result: list[tuple[str, PreparedRecord]] = []
    for raw in cast(list[object], config["connections"]):
        if not isinstance(raw, dict):
            raise PreparationError("INVALID_EXPOSURE", "/connections")
        item = cast(dict[str, object], raw)
        ref = item.get("record")
        if not isinstance(ref, Mapping):
            raise PreparationError("INVALID_EXPOSURE", "/connections/record")
        typed = cast(Mapping[str, object], ref)
        module, element = typed.get("module"), typed.get("element")
        record = (
            record_map.get((module, element))
            if type(module) is str and type(element) is str
            else None
        )
        name = item.get("name")
        if record is None or type(name) is not str or not NAME_PATTERN.fullmatch(name):
            raise PreparationError("INVALID_EXPOSURE", "/connections")
        result.append((name, record))
    result.sort(key=lambda item: (item[1].source.module, item[1].source.element))
    if len({record.source for _name, record in result}) != len(result):
        raise PreparationError("AMBIGUOUS_IDENTITY", "connection Record")
    return tuple(result)


def _check_connection_names(
    selected: Sequence[tuple[str, PreparedRecord]], records: Sequence[PreparedRecord]
) -> None:
    query_fields = {"node", "nodes"}
    type_names = {"Node", "Query", "PageInfo", "Mutation", "String", "Boolean", "ID", "Decimal"}
    field_names: set[str] = set()
    for name, record in selected:
        edge, connection = record.type_name + "Edge", record.type_name + "Connection"
        if name in query_fields or name in field_names:
            raise PreparationError("NAME_COLLISION", "connection root field")
        if edge in type_names or connection in type_names or edge == connection:
            raise PreparationError("NAME_COLLISION", "connection type")
        field_names.add(name)
        type_names.update((edge, connection))
    record_type_names = {record.type_name for record in records}
    if type_names & record_type_names:
        raise PreparationError("NAME_COLLISION", "connection type")


def _render_sdl(
    records: Sequence[PreparedRecord],
    selected: Sequence[tuple[str, PreparedRecord]],
    default_page: int,
) -> str:
    defs = ["interface Node { id: ID! }"]
    scalar_names = {
        "string": "String",
        "boolean": "Boolean",
        "integer": "BigInt",
        "decimal": "Decimal",
        "uuid": "UUID",
        "date": "Date",
        "timestamp": "ExactTimestamp",
    }
    for record in records:
        fields = ["id: ID!"]
        fields.extend(
            f"{field.name}: {scalar_names[field.scalar]}{'' if field.nullable else '!'}"
            for field in record.fields
        )
        defs.append(f"type {record.type_name} implements Node {{ " + " ".join(fields) + " }")
    for _name, record in selected:
        defs.append(f"type {record.type_name}Edge {{ cursor: String! node: {record.type_name}! }}")
        defs.append(
            f"type {record.type_name}Connection {{ edges: [{record.type_name}Edge!]! "
            "pageInfo: PageInfo! }"
        )
    defs.append(
        "type PageInfo { hasNextPage: Boolean! hasPreviousPage: Boolean! "
        "startCursor: String endCursor: String }"
    )
    query = ["node(id: ID!): Node", "nodes(ids: [ID!]!): [Node]!"]
    query.extend(
        f"{name}(first: Int = {default_page}, after: String): {record.type_name}Connection!"
        for name, record in selected
    )
    defs.append("type Query { " + " ".join(query) + " }")
    custom_scalars = {
        "integer": "BigInt",
        "decimal": "Decimal",
        "uuid": "UUID",
        "date": "Date",
        "timestamp": "ExactTimestamp",
    }
    used = {field.scalar for record in records for field in record.fields}
    defs.extend(f"scalar {name}" for scalar, name in custom_scalars.items() if scalar in used)
    return "\n".join(defs) + "\n"


def _api_digest_v3(
    exposure: bytes,
    sources: Sequence[tuple[str, str]],
    capabilities: Sequence[tuple[str, str]],
    host_profile: Mapping[str, object],
    scalar_profile: str,
    roots: Sequence[Mapping[str, object]],
    connections: Sequence[Mapping[str, object]],
    sdl: str,
) -> str:
    limits = cast(Sequence[tuple[str, str]], host_profile["limits"])
    profile = tuple(
        sorted((*capabilities, *((f"host.limit.{key}", value) for key, value in limits)))
    )
    frames = [b"lintel.api/3", exposure]
    for identity, digest in sources:
        frames.extend((identity.encode("utf-8"), digest.encode("ascii")))
    frames.extend(
        (
            json.dumps(
                [list(pair) for pair in profile], ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8"),
            scalar_profile.encode("utf-8"),
            generated_roots_json(_root_values(roots)),
            _connections_bytes(connections),
            sdl.encode("utf-8"),
        )
    )
    return hashlib.sha256(
        b"".join(len(value).to_bytes(8, "big") + value for value in frames)
    ).hexdigest()


def _root_values(roots: Sequence[Mapping[str, object]]) -> tuple[PreparedGeneratedRoot, ...]:
    return tuple(
        PreparedGeneratedRoot(
            OperationRef(
                cast(str, cast(Mapping[str, object], root["lookup"])["module"]),
                cast(str, cast(Mapping[str, object], root["lookup"])["id"]),
                "record",
            ),
            cast(str, root["sourceDigest"]),
            cast(str, root["artifactDigest"]),
            cast(str, root["receiptDigest"]),
            cast(str, root["bindingDigest"]),
            cast(str, root["algebraSha256"]),
            cast(str, root["primaryKeyId"]),
        )
        for root in roots
    )


def _connections_bytes(connections: Sequence[Mapping[str, object]]) -> bytes:
    return json.dumps(
        list(connections),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
