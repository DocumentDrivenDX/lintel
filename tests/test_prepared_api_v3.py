from __future__ import annotations

import hashlib
import json
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path
from time import monotonic
from typing import Any, cast

import pytest
from jsonschema import Draft202012Validator

from lintel.build.errors import PreparationError
from lintel.build.generated_connections import eligible_connection
from lintel.graphql import create_router
from lintel.node_id import PreparedRoots, StringKeyNodeCodec
from lintel.ports.protocols import RequestSession
from lintel.ports.values import ConnectionIntent, ElementRef, OperationRef, RequestScope
from lintel.projection import TrustedPreparedRef, load_prepared_api
from lintel.projection.prepared import PreparedField, PreparedRecord
from lintel.projection.prepared_v2 import (
    PreparedGeneratedRoot,
    generated_roots_from_json,
    generated_roots_json,
)
from lintel.projection.prepared_v3 import (
    PreparedConnection,
    allowed_field_profile_to_dict,
    connection_names,
    generated_connections_from_json,
    generated_connections_json,
    join_generated_connections,
)

ROOT = Path(__file__).parents[1]


class _PreparedPort:
    def __init__(self, prepared: Any) -> None:
        self._capabilities = dict(prepared.capabilities)

    def capabilities(self) -> Mapping[str, str]:
        return self._capabilities

    @asynccontextmanager
    async def session(self, scope: RequestScope) -> AsyncGenerator[RequestSession, None]:
        del scope
        yield cast(RequestSession, self)

    @asynccontextmanager
    async def session_planned(
        self, scope: RequestScope, intents: tuple[ConnectionIntent, ...]
    ) -> AsyncGenerator[RequestSession, None]:
        del scope, intents
        yield cast(RequestSession, self)


def _admit_v3_fixture():
    contents = (ROOT / "tests/fixtures/prepared-api-v3-strict5-proof.json").read_bytes()
    trust = json.loads((ROOT / "tests/fixtures/prepared-api-v3-strict5-trust.json").read_bytes())
    pin = TrustedPreparedRef(
        artifact_sha256=trust["artifactSha256"],
        artifact_digest=trust["artifactDigest"],
        application=trust["application"],
        api_digest=trust["apiDigest"],
        exposure_sha256=trust["exposureSha256"],
        sources=tuple((item["identity"], item["sha256"]) for item in trust["sources"]),
        capabilities=tuple(tuple(pair) for pair in trust["capabilities"]),
        binding_profile=trust["bindingProfile"],
        scalar_codec_profile=trust["scalarCodecProfile"],
        limits=tuple(tuple(pair) for pair in trust["limits"]),
        generated_roots_sha256=trust["generatedRootsSha256"],
        generated_connections_sha256=trust["generatedConnectionsSha256"],
    )
    return load_prepared_api(contents, pin)


def _admit_v2_fixture():
    contents = (ROOT / "tests/fixtures/prepared-api-v2-build-proof.json").read_bytes()
    artifact = json.loads(contents)
    roots = generated_roots_from_json(artifact["generatedRoots"])
    pin = TrustedPreparedRef(
        artifact_sha256=hashlib.sha256(contents).hexdigest(),
        artifact_digest=artifact["artifactDigest"],
        application=artifact["application"],
        api_digest=artifact["apiDigest"],
        exposure_sha256=artifact["exposureSha256"],
        sources=tuple((source["identity"], source["sha256"]) for source in artifact["sources"]),
        capabilities=tuple(tuple(pair) for pair in artifact["capabilities"]),
        binding_profile=artifact["bindingProfile"],
        scalar_codec_profile=artifact["scalarCodecProfile"],
        limits=tuple(tuple(pair) for pair in artifact["hostProfile"]["limits"]),
        generated_roots_sha256=hashlib.sha256(generated_roots_json(roots)).hexdigest(),
    )
    return load_prepared_api(contents, pin)


def test_connection_profile_is_closed_and_exports_json_compatible_body() -> None:
    body: dict[str, object] = {
        "version": "umf.allowed-connection-fields/1",
        "scalarCodecProfile": "lintel.scalars/1",
        "fields": [
            {
                "fieldId": "task.id",
                "sourceField": {"module": "board", "element": "id"},
                "output": {
                    "carrier": "string",
                    "name": "id",
                    "nativeType": {"schema": "public", "name": "text", "attributes": []},
                    "nullable": False,
                    "oid": 25,
                },
                "scalar": "string",
                "nullable": False,
            },
            {
                "fieldId": "task.title",
                "sourceField": {"module": "board", "element": "title"},
                "output": {
                    "carrier": "decimal",
                    "name": "title",
                    "nativeType": {"schema": "public", "name": "numeric", "attributes": []},
                    "nullable": True,
                    "oid": 1700,
                },
                "scalar": "decimal",
                "nullable": True,
            },
        ],
    }
    canonical = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    wire: dict[str, object] = {
        "lookup": {"module": "board", "id": "Task", "kind": "record"},
        "fieldRefs": [{"module": "board", "element": "title"}],
        "primaryKeyField": {"module": "board", "element": "id"},
        "profile": {
            "connectionProfile": "connection.forward=edge-cursor-1",
            "readProfile": "weft.generated-read-algebra/5",
            "allowedFieldProfile": {
                "version": "umf.allowed-connection-fields/1",
                "digest": digest,
                "body": body,
            },
        },
    }
    parsed = generated_connections_from_json([wire])[0]
    exported = allowed_field_profile_to_dict(parsed)
    assert exported == body
    assert exported is not parsed.profile_body
    assert exported["fields"] is not parsed.profile_body["fields"]
    assert (
        json.loads(generated_connections_json((parsed,)))[0]["profile"]["allowedFieldProfile"][
            "digest"
        ]
        == digest
    )

    malformed = json.loads(json.dumps(wire))
    malformed["profile"]["allowedFieldProfile"]["body"]["fields"][1]["scalar"] = "Decimal"
    with pytest.raises(ValueError, match="API_MISMATCH"):
        generated_connections_from_json([malformed])


def test_exposure_schema_is_closed_and_requires_declared_connections() -> None:
    schema = json.loads(
        (ROOT / "docs/helix/02-design/schemas/exposure-v3.schema.json").read_bytes()
    )
    Draft202012Validator.check_schema(schema)
    prepared_schema = json.loads(
        (ROOT / "docs/helix/02-design/schemas/prepared-api-v3.schema.json").read_bytes()
    )
    Draft202012Validator.check_schema(prepared_schema)
    connections: list[dict[str, object]] = [
        {"name": "notes", "record": {"module": "demo", "element": "Note"}}
    ]
    exposure: dict[str, object] = {
        "format": "lintel.exposure/3",
        "application": "fixture",
        "identityNamespace": "fixture.v1",
        "records": [
            {
                "record": {"module": "demo", "element": "Note"},
                "key": "primary",
                "typeName": "Note",
                "lookup": {"module": "demo", "id": "Note", "kind": "record"},
                "fields": [],
                "relationships": [],
            }
        ],
        "connections": connections,
        "mutations": [],
    }
    validator = cast(Any, Draft202012Validator(schema))
    assert not list(validator.iter_errors(exposure))
    connections[0]["operation"] = {"module": "demo", "id": "Note"}
    assert list(validator.iter_errors(exposure))


def test_api2_fixture_bytes_and_digest_stay_pinned() -> None:
    raw = (ROOT / "tests/fixtures/prepared-api-v2-build-proof.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        "53fa234381c5339d4c810f702b9b09fc3d6ec720adb252ba077205cae00414dc"
    )
    artifact = json.loads(raw)
    assert (
        artifact["apiDigest"] == "3a58d05f097f5feeb7ce55598711c260d101bf59c9de77f38a89a0e9d9ef1935"
    )
    admitted = _admit_v2_fixture()
    assert admitted.api_digest == artifact["apiDigest"]


def test_real_strict_v5_api3_artifact_is_schema_valid_and_admitted() -> None:
    raw = (ROOT / "tests/fixtures/prepared-api-v3-strict5-proof.json").read_bytes()
    trust = json.loads((ROOT / "tests/fixtures/prepared-api-v3-strict5-trust.json").read_bytes())
    assert hashlib.sha256(raw).hexdigest() == trust["artifactSha256"]
    artifact = json.loads(raw)
    schema = json.loads(
        (ROOT / "docs/helix/02-design/schemas/prepared-api-v3.schema.json").read_bytes()
    )
    Draft202012Validator.check_schema(schema)
    validator = cast(Any, Draft202012Validator(schema))
    assert not list(validator.iter_errors(artifact))
    admitted = _admit_v3_fixture()
    assert admitted.version == "lintel.prepared-api/3"
    assert admitted.api_digest == trust["apiDigest"]
    assert tuple(route.name for route in admitted.generated_connections) == ("notes", "tasks")


def test_api3_router_requires_exact_prepared_node_key_registry() -> None:
    prepared = _admit_v3_fixture()
    port = _PreparedPort(prepared)

    async def resolve_context(_request: Any, digest: str) -> RequestScope:
        return RequestScope(
            prepared.application,
            digest,
            "query",
            object(),
            "codec-test",
            monotonic() + 60,
        )

    with pytest.raises(ValueError, match="API_MISMATCH"):
        create_router(prepared, port, StringKeyNodeCodec(), resolve_context)

    def validate_key(
        _module: str, _record: str, _key_id: str, components: tuple[object, ...]
    ) -> tuple[object, ...]:
        return tuple(
            cast(str, cast(Mapping[str, object], component)["string"]) for component in components
        )

    codec = StringKeyNodeCodec.for_prepared_api(
        cast(PreparedRoots, prepared),
        {
            (ElementRef("demo", "Note"), "primary"): validate_key,
            (ElementRef("demo", "Task"), "primary"): validate_key,
        },
    )
    assert codec.registry_matches(cast(PreparedRoots, prepared))
    assert create_router(prepared, port, codec, resolve_context)


def test_runtime_connection_join_refuses_composite_record_key() -> None:
    key = ElementRef("demo", "id")
    title = ElementRef("demo", "title")
    lookup = OperationRef("demo", "Note", "record")
    record = PreparedRecord(
        ElementRef("demo", "Note"),
        "primary",
        (key, ElementRef("demo", "tenant")),
        "Note",
        lookup,
        (PreparedField(title, "title", "string", True),),
    )
    body = {
        "version": "umf.allowed-connection-fields/1",
        "scalarCodecProfile": "lintel.scalars/1",
        "fields": [
            {
                "fieldId": "demo/id",
                "sourceField": {"module": "demo", "element": "id"},
                "output": {"carrier": "string", "nullable": False},
                "scalar": "string",
                "nullable": False,
            },
            {
                "fieldId": "demo/title",
                "sourceField": {"module": "demo", "element": "title"},
                "output": {"carrier": "string", "nullable": True},
                "scalar": "string",
                "nullable": True,
            },
        ],
    }
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    connection = PreparedConnection(lookup, "notes", (title,), key, digest, body)
    root = PreparedGeneratedRoot(
        lookup, "a" * 64, "b" * 64, "c" * 64, "d" * 64, "e" * 64, "primary"
    )
    with pytest.raises(ValueError, match="API_MISMATCH"):
        join_generated_connections(
            (record,), (root,), (connection,), (("demo", "a" * 64),), "lintel.scalars/1"
        )


def test_runtime_exposure_join_refuses_two_connection_names_for_one_record() -> None:
    record = PreparedRecord(
        ElementRef("demo", "Note"),
        "primary",
        (ElementRef("demo", "id"),),
        "Note",
        OperationRef("demo", "Note", "record"),
        (),
    )
    exposure = json.dumps(
        {
            "connections": [
                {"name": "notes", "record": {"module": "demo", "element": "Note"}},
                {"name": "otherNotes", "record": {"module": "demo", "element": "Note"}},
            ]
        }
    ).encode()
    with pytest.raises(ValueError, match="API_MISMATCH"):
        connection_names(exposure, (record,))


def test_v5_connection_bound_must_cover_prepared_host_max_page() -> None:
    root = {
        "forwardConnectionSupport": {
            "status": "eligible",
            "profile": "weft.generated-forward-connection/1",
        },
        "forwardConnection": {
            "profile": "weft.generated-forward-connection/1",
            "forward": {},
            "maxFirst": 99,
            "key": {
                "fieldId": "demo/id",
                "direction": "asc",
                "collation": 'pg_catalog."C"',
            },
        },
    }
    with pytest.raises(PreparationError) as raised:
        eligible_connection(root, "demo/id", 100)
    assert raised.value.code == "UNSUPPORTED"
