"""Runtime admission of canonical build-issued prepared API artifacts."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final, cast

from lintel.node_id import PROFILE as NODE_ID_PROFILE
from lintel.ports.values import ElementRef, OperationRef
from lintel.projection.prepared_commands import admitted_commands, command_sdl
from lintel.projection.prepared_digest import api_digest as _api_digest
from lintel.projection.prepared_host import freeze_host as _freeze_host
from lintel.projection.prepared_host import host_profile as _host_profile
from lintel.projection.prepared_v2 import PreparedGeneratedRoot
from lintel.projection.prepared_v2 import generated_roots_from_json as _generated_roots_from_json
from lintel.projection.prepared_v2 import generated_roots_json as _generated_roots_json
from lintel.projection.prepared_v2 import join_generated_roots as _join_generated_roots
from lintel.projection.prepared_v2 import strict_object as _strict_object
from lintel.projection.prepared_v3 import READ_PROFILE as _CONNECTION_READ_PROFILE_V3
from lintel.projection.prepared_v3 import PreparedConnection
from lintel.projection.prepared_v3 import connection_names as _connection_names
from lintel.projection.prepared_v3 import connection_with_name as _connection_with_name
from lintel.projection.prepared_v3 import (
    generated_connections_from_json as _generated_connections_from_json,
)
from lintel.projection.prepared_v3 import generated_connections_json as _generated_connections_json
from lintel.projection.prepared_v3 import join_generated_connections as _join_generated_connections
from lintel.projection.prepared_v3 import sdl_legacy as _sdl
from lintel.projection.prepared_v3 import sdl_v3 as _sdl_v3
from lintel.projection.prepared_v4 import READ_PROFILE as _CONNECTION_READ_PROFILE_V4
from lintel.projection.prepared_v4 import (
    generated_connections_from_json as _generated_connections_from_json_v4,
)
from lintel.projection.prepared_v4 import (
    join_generated_connections as _join_generated_connections_v4,
)
from lintel.projection.prepared_v5 import READ_PROFILE as _CONNECTION_READ_PROFILE_V5
from lintel.projection.prepared_v5 import (
    generated_connections_from_json as _generated_connections_from_json_v5,
)
from lintel.projection.prepared_v5 import (
    join_generated_connections as _join_generated_connections_v5,
)
from lintel.projection.prepared_wire import canonical_json as _canonical_json
from lintel.projection.prepared_wire import canonical_sdl as _canonical_sdl
from lintel.projection.prepared_wire import decode_exposure as _decode_exposure
from lintel.projection.prepared_wire import digest as _digest
from lintel.projection.prepared_wire import nonempty as _nonempty
from lintel.projection.prepared_wire import pairs as _pairs
from lintel.projection.prepared_wire import source_pairs as _source_pairs
from lintel.projection.prepared_wire import string_value
from lintel.projection.relationships import relationship_sdl, relationships

_TOKEN: Final = object()
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
name_pattern = re.compile(r"^(?!__)[_A-Za-z][_0-9A-Za-z]*$")
_SCALARS = {
    "string": "String",
    "boolean": "Boolean",
    "integer": "BigInt",
    "decimal": "Decimal",
    "uuid": "UUID",
    "date": "Date",
    "timestamp": "ExactTimestamp",
}
_FIELDS = {
    "version",
    "artifactId",
    "artifactDigest",
    "application",
    "identityNamespace",
    "exposureBase64",
    "exposureSha256",
    "sources",
    "capabilities",
    "hostProfile",
    "bindingProfile",
    "scalarCodecProfile",
    "records",
    "sdl",
    "schemaDigest",
    "apiDigest",
}


def _connection_read_profile(version: object) -> str:
    return {
        "lintel.prepared-api/3": _CONNECTION_READ_PROFILE_V3,
        "lintel.prepared-api/4": _CONNECTION_READ_PROFILE_V4,
        "lintel.prepared-api/5": _CONNECTION_READ_PROFILE_V5,
    }.get(version if isinstance(version, str) else "", _CONNECTION_READ_PROFILE_V3)


_GENERATED_ROOT_FIELDS = _FIELDS | {"generatedRoots"}
_GENERATED_CONNECTION_FIELDS = _GENERATED_ROOT_FIELDS | {"generatedConnections"}


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


@dataclass(frozen=True, slots=True)
class TrustedPreparedRef:
    """Host-supplied pins copied from its independently verified inventory receipt."""

    artifact_sha256: str
    artifact_digest: str
    application: str
    api_digest: str
    exposure_sha256: str
    sources: tuple[tuple[str, str], ...]
    capabilities: tuple[tuple[str, str], ...]
    binding_profile: str
    scalar_codec_profile: str
    limits: tuple[tuple[str, str], ...]
    generated_roots_sha256: str | None = None
    generated_connections_sha256: str | None = None


class AdmittedPreparedApi:
    """Nominal immutable runtime API produced only by :func:`load_prepared_api`."""

    __slots__ = (
        "_artifact_id",
        "_artifact_digest",
        "_application",
        "_identity_namespace",
        "_exposure_bytes",
        "_sources",
        "_capabilities",
        "_host_profile",
        "_binding_profile",
        "_scalar_codec_profile",
        "_records",
        "_version",
        "_generated_roots",
        "_generated_connections",
        "_commands",
        "_relationships",
        "_sdl",
        "_schema_digest",
        "_api_digest",
        "_sealed",
    )

    def __init__(self, token: object, values: Mapping[str, object]) -> None:
        if token is not _TOKEN:
            raise TypeError("AdmittedPreparedApi must come from load_prepared_api")
        for name, value in values.items():
            object.__setattr__(self, "_" + name, value)
        object.__setattr__(self, "_sealed", True)

    def __setattr__(self, name: str, value: object) -> None:
        if getattr(self, "_sealed", False):
            raise AttributeError("AdmittedPreparedApi is immutable")
        object.__setattr__(self, name, value)

    artifact_id = property(lambda self: self._artifact_id)
    artifact_digest = property(lambda self: self._artifact_digest)
    application = property(lambda self: self._application)
    identity_namespace = property(lambda self: self._identity_namespace)
    exposure_bytes = property(lambda self: self._exposure_bytes)
    source_digests = property(lambda self: self._sources)
    capabilities = property(lambda self: self._capabilities)
    host_profile = property(lambda self: self._host_profile)
    binding_profile = property(lambda self: self._binding_profile)
    scalar_codec_profile = property(lambda self: self._scalar_codec_profile)
    records = property(lambda self: self._records)
    version = property(lambda self: self._version)
    generated_roots = property(lambda self: self._generated_roots)
    generated_connections = property(lambda self: self._generated_connections)
    relationships = property(lambda self: self._relationships)
    commands = property(lambda self: self._commands)
    sdl = property(lambda self: self._sdl)
    schema_digest = property(lambda self: self._schema_digest)
    api_digest = property(lambda self: self._api_digest)


def load_prepared_api(
    artifact_bytes: bytes, trusted_ref: TrustedPreparedRef
) -> AdmittedPreparedApi:
    """Verify bytes and host pins, then return the nominal runtime artifact."""
    if type(artifact_bytes) is not bytes or len(artifact_bytes) > 10_000_000:
        raise ValueError("API_MISMATCH")
    if type(trusted_ref) is not TrustedPreparedRef:
        raise ValueError("API_MISMATCH")
    artifact = _strict_object(artifact_bytes)
    version = artifact.get("version")
    expected_fields = (
        _GENERATED_CONNECTION_FIELDS
        if version in {"lintel.prepared-api/3", "lintel.prepared-api/4", "lintel.prepared-api/5"}
        else _GENERATED_ROOT_FIELDS
        if version == "lintel.prepared-api/2"
        else _FIELDS
    )
    if version == "lintel.prepared-api/5" and "commands" in artifact:
        expected_fields = expected_fields | {"commands"}
    if _canonical_json(artifact) != artifact_bytes or set(artifact) != expected_fields:
        raise ValueError("API_MISMATCH")
    _validate_shape(artifact, version)
    if not _matches_pins(artifact_bytes, artifact, trusted_ref):
        raise ValueError("API_MISMATCH")
    sources = _source_pairs(artifact["sources"])
    capabilities = _pairs(artifact["capabilities"])
    host = _host_profile(artifact["hostProfile"])
    exposure = _decode_exposure(artifact)
    from lintel.projection.records import records_from_json

    records = records_from_json(
        artifact["records"],
        allowed_operation_kinds=("record",)
        if version
        in {
            "lintel.prepared-api/2",
            "lintel.prepared-api/3",
            "lintel.prepared-api/4",
            "lintel.prepared-api/5",
        }
        else ("table", "action"),
    )
    generated_roots, generated_connections = _generated_metadata(
        artifact, version, records, sources, exposure
    )
    sdl = string_value(artifact, "sdl")
    try:
        canonical_sdl = _canonical_sdl(sdl)
    except Exception as error:
        raise ValueError("API_MISMATCH") from error
    exposure_value = _strict_object(exposure)
    commands = admitted_commands(artifact, exposure_value, dict(capabilities))
    selected_relationships = relationships(exposure_value, dict(capabilities), str(version))
    expected_sdl = relationship_sdl(
        command_sdl(
            _expected_sdl(version, records, generated_connections, host),
            commands,
            has_decimal=any(field.scalar == "decimal" for r in records for field in r.fields),
        ),
        selected_relationships,
        records,
    )
    if canonical_sdl != sdl or _canonical_sdl(expected_sdl) != sdl:
        raise ValueError("API_MISMATCH")
    schema_digest = _digest(artifact, "schemaDigest")
    api_digest = _digest(artifact, "apiDigest")
    if hashlib.sha256(sdl.encode("utf-8")).hexdigest() != schema_digest:
        raise ValueError("API_MISMATCH")
    expected_api = _api_digest(
        exposure,
        sources,
        capabilities,
        cast(dict[str, str], host["limits"]),
        string_value(artifact, "scalarCodecProfile"),
        sdl,
        generated_roots
        if version
        in {
            "lintel.prepared-api/2",
            "lintel.prepared-api/3",
            "lintel.prepared-api/4",
            "lintel.prepared-api/5",
        }
        else None,
        generated_connections
        if version in {"lintel.prepared-api/3", "lintel.prepared-api/4", "lintel.prepared-api/5"}
        else None,
        api_version=(
            "5"
            if version == "lintel.prepared-api/5"
            else "4"
            if version == "lintel.prepared-api/4"
            else None
        ),
    )
    if expected_api != api_digest:
        raise ValueError("API_MISMATCH")
    return AdmittedPreparedApi(
        _TOKEN,
        {
            "artifact_id": string_value(artifact, "artifactId"),
            "artifact_digest": _digest(artifact, "artifactDigest"),
            "application": string_value(artifact, "application"),
            "identity_namespace": string_value(artifact, "identityNamespace"),
            "exposure_bytes": exposure,
            "sources": sources,
            "capabilities": capabilities,
            "host_profile": _freeze_host(host),
            "binding_profile": string_value(artifact, "bindingProfile"),
            "scalar_codec_profile": string_value(artifact, "scalarCodecProfile"),
            "records": records,
            "version": version,
            "generated_roots": generated_roots,
            "generated_connections": generated_connections,
            "commands": commands,
            "relationships": selected_relationships,
            "sdl": sdl,
            "schema_digest": schema_digest,
            "api_digest": api_digest,
        },
    )


def _generated_metadata(
    artifact: Mapping[str, object],
    version: object,
    records: Sequence[PreparedRecord],
    sources: Sequence[tuple[str, str]],
    exposure: bytes,
) -> tuple[tuple[PreparedGeneratedRoot, ...], tuple[PreparedConnection, ...]]:
    connection_read_profile = (
        _connection_read_profile(version)
        if version
        in {
            "lintel.prepared-api/3",
            "lintel.prepared-api/4",
            "lintel.prepared-api/5",
        }
        else _CONNECTION_READ_PROFILE_V3
    )
    roots = (
        _generated_roots_from_json(artifact["generatedRoots"])
        if version
        in {
            "lintel.prepared-api/2",
            "lintel.prepared-api/3",
            "lintel.prepared-api/4",
            "lintel.prepared-api/5",
        }
        else ()
    )
    connections = (
        _generated_connections_from_json(
            artifact["generatedConnections"], expected_read_profile=connection_read_profile
        )
        if version == "lintel.prepared-api/3"
        else _generated_connections_from_json_v4(
            artifact["generatedConnections"], expected_read_profile=connection_read_profile
        )
        if version == "lintel.prepared-api/4"
        else _generated_connections_from_json_v5(
            artifact["generatedConnections"], expected_read_profile=connection_read_profile
        )
        if version == "lintel.prepared-api/5"
        else ()
    )
    _join_generated_roots(records, roots, sources, version)
    if version in {"lintel.prepared-api/3", "lintel.prepared-api/4", "lintel.prepared-api/5"}:
        names = _connection_names(exposure, records)
        if set(names) != {connection.lookup for connection in connections}:
            raise ValueError("API_MISMATCH")
        connections = tuple(
            _connection_with_name(connection, names[connection.lookup])
            for connection in connections
        )
        join_connections = (
            _join_generated_connections_v5
            if version == "lintel.prepared-api/5"
            else _join_generated_connections_v4
            if version == "lintel.prepared-api/4"
            else _join_generated_connections
        )
        join_connections(
            records,
            roots,
            connections,
            sources,
            string_value(artifact, "scalarCodecProfile"),
            expected_read_profile=connection_read_profile,
        )
    return roots, connections


def _expected_sdl(
    version: object,
    records: Sequence[PreparedRecord],
    connections: Sequence[PreparedConnection],
    host: Mapping[str, object],
) -> str:
    return (
        _sdl_v3(records, connections, host)
        if version in {"lintel.prepared-api/3", "lintel.prepared-api/4", "lintel.prepared-api/5"}
        else _sdl(records)
    )


def _validate_shape(artifact: Mapping[str, object], version: object) -> None:
    required_strings = (
        "artifactId",
        "application",
        "identityNamespace",
        "bindingProfile",
        "scalarCodecProfile",
        "sdl",
    )
    if version not in {
        "lintel.prepared-api/1",
        "lintel.prepared-api/2",
        "lintel.prepared-api/3",
        "lintel.prepared-api/4",
        "lintel.prepared-api/5",
    } or any(not _nonempty(artifact.get(key)) for key in required_strings):
        raise ValueError("API_MISMATCH")
    for name in ("artifactDigest", "exposureSha256", "schemaDigest", "apiDigest"):
        _digest(artifact, name)
    if not _source_pairs(artifact["sources"]):
        raise ValueError("API_MISMATCH")
    pairs = _pairs(artifact["capabilities"])
    if not pairs or tuple(sorted(pairs)) != pairs:
        raise ValueError("API_MISMATCH")
    if (
        version
        in {
            "lintel.prepared-api/2",
            "lintel.prepared-api/3",
            "lintel.prepared-api/4",
            "lintel.prepared-api/5",
        }
        and dict(pairs).get("identity.codec") != NODE_ID_PROFILE
    ):
        raise ValueError("API_MISMATCH")
    _host_profile(artifact["hostProfile"])
    if not isinstance(artifact["records"], list) or not artifact["records"]:
        raise ValueError("API_MISMATCH")
    if (
        version
        in {
            "lintel.prepared-api/2",
            "lintel.prepared-api/3",
            "lintel.prepared-api/4",
            "lintel.prepared-api/5",
        }
        and "generatedRoots" not in artifact
    ):
        raise ValueError("API_MISMATCH")
    if version in {"lintel.prepared-api/3", "lintel.prepared-api/4", "lintel.prepared-api/5"}:
        caps = dict(pairs)
        if (
            "generatedConnections" not in artifact
            or caps.get("connection.forward") != "edge-cursor-1"
            or caps.get("connection.forward.binding.profile") != caps.get("binding.profile")
        ):
            raise ValueError("API_MISMATCH")


def _matches_pins(raw: bytes, artifact: Mapping[str, object], pin: TrustedPreparedRef) -> bool:
    artifact_digest = _digest(artifact, "artifactDigest")
    unsigned = dict(artifact)
    unsigned.pop("artifactDigest", None)
    exposure = _decode_exposure(artifact)
    host = _freeze_host(_host_profile(artifact["hostProfile"]))
    version = artifact.get("version")
    roots = (
        _generated_roots_from_json(artifact.get("generatedRoots"))
        if version
        in {
            "lintel.prepared-api/2",
            "lintel.prepared-api/3",
            "lintel.prepared-api/4",
            "lintel.prepared-api/5",
        }
        else ()
    )
    roots_sha256 = (
        hashlib.sha256(_generated_roots_json(roots)).hexdigest()
        if version
        in {
            "lintel.prepared-api/2",
            "lintel.prepared-api/3",
            "lintel.prepared-api/4",
            "lintel.prepared-api/5",
        }
        else None
    )
    connections = (
        _generated_connections_from_json(
            artifact["generatedConnections"],
            expected_read_profile=_connection_read_profile(version),
        )
        if version == "lintel.prepared-api/3"
        else _generated_connections_from_json_v4(
            artifact["generatedConnections"],
            expected_read_profile=_connection_read_profile(version),
        )
        if version == "lintel.prepared-api/4"
        else _generated_connections_from_json_v5(
            artifact["generatedConnections"],
            expected_read_profile=_connection_read_profile(version),
        )
        if version == "lintel.prepared-api/5"
        else ()
    )
    connections_sha256 = (
        hashlib.sha256(_generated_connections_json(connections)).hexdigest()
        if version in {"lintel.prepared-api/3", "lintel.prepared-api/4", "lintel.prepared-api/5"}
        else None
    )
    return (
        hashlib.sha256(raw).hexdigest() == pin.artifact_sha256
        and hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        == artifact_digest
        == pin.artifact_digest
        and artifact.get("application") == pin.application
        and artifact.get("apiDigest") == pin.api_digest
        and hashlib.sha256(exposure).hexdigest() == pin.exposure_sha256
        and _source_pairs(artifact["sources"]) == pin.sources
        and _pairs(artifact["capabilities"]) == pin.capabilities
        and artifact.get("bindingProfile") == pin.binding_profile
        and artifact.get("scalarCodecProfile") == pin.scalar_codec_profile
        and tuple(sorted(cast(Mapping[str, str], host["limits"]).items())) == pin.limits
        and roots_sha256 == pin.generated_roots_sha256
        and connections_sha256 == pin.generated_connections_sha256
    )
