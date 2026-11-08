from __future__ import annotations

import hashlib
import json
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path
from time import monotonic
from typing import Any, cast

from jsonschema import Draft202012Validator

from lintel.graphql import create_router
from lintel.node_id import PreparedRoots, StringKeyNodeCodec
from lintel.ports.protocols import RequestSession
from lintel.ports.values import ConnectionIntent, ElementRef, RequestScope
from lintel.projection import TrustedPreparedRef, load_prepared_api
from lintel.projection.prepared_v3 import generated_connections_from_json
from lintel.projection.prepared_v4 import (
    generated_connections_from_json as generated_connections_from_json_v4,
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


def test_combined_v7_build_artifact_is_closed_admitted_and_routed() -> None:
    raw = (ROOT / "tests/fixtures/prepared-api-v4-weft7-build27-proof.json").read_bytes()
    trust = json.loads(
        (ROOT / "tests/fixtures/prepared-api-v4-weft7-build27-trust.json").read_bytes()
    )
    assert hashlib.sha256(raw).hexdigest() == trust["artifactSha256"]
    artifact = json.loads(raw)
    schema = json.loads(
        (ROOT / "docs/helix/02-design/schemas/prepared-api-v4.schema.json").read_bytes()
    )
    Draft202012Validator.check_schema(schema)
    validator = cast(Any, Draft202012Validator(schema))
    assert not list(validator.iter_errors(artifact))
    assert artifact["version"] == "lintel.prepared-api/4"
    assert artifact["generatedConnections"][0]["profile"]["readProfile"] == (
        "weft.generated-read-algebra/7"
    )

    pin = TrustedPreparedRef(
        artifact_sha256=trust["artifactSha256"],
        artifact_digest=trust["artifactDigest"],
        application=trust["application"],
        api_digest=trust["apiDigest"],
        exposure_sha256=trust["exposureSha256"],
        sources=tuple((row["identity"], row["sha256"]) for row in trust["sources"]),
        capabilities=tuple(tuple(row) for row in trust["capabilities"]),
        binding_profile=trust["bindingProfile"],
        scalar_codec_profile=trust["scalarCodecProfile"],
        limits=tuple(tuple(row) for row in trust["limits"]),
        generated_roots_sha256=trust["generatedRootsSha256"],
        generated_connections_sha256=trust["generatedConnectionsSha256"],
    )
    prepared = load_prepared_api(raw, pin)
    assert prepared.api_digest == trust["apiDigest"]
    assert prepared.generated_connections[0].read_profile == "weft.generated-read-algebra/7"

    with_v7 = json.loads(json.dumps(artifact["generatedConnections"]))
    with_v7[0]["profile"]["readProfile"] = "weft.generated-read-algebra/7"
    try:
        generated_connections_from_json(with_v7)
    except ValueError as error:
        assert "API_MISMATCH" in str(error)
    else:
        raise AssertionError("the strict API3 connection codec accepted Weft /7")
    with_v5 = json.loads(json.dumps(artifact["generatedConnections"]))
    with_v5[0]["profile"]["readProfile"] = "weft.generated-read-algebra/5"
    try:
        generated_connections_from_json_v4(with_v5)
    except ValueError as error:
        assert "API_MISMATCH" in str(error)
    else:
        raise AssertionError("the API4 connection codec accepted Weft /5")

    def validate_key(
        _module: str, _record: str, _key_id: str, components: tuple[object, ...]
    ) -> tuple[object, ...]:
        return tuple(cast(str, cast(Mapping[str, object], item)["string"]) for item in components)

    codec = StringKeyNodeCodec.for_prepared_api(
        cast(PreparedRoots, prepared), {(ElementRef("demo", "Note"), "primary"): validate_key}
    )
    assert create_router(prepared, _PreparedPort(prepared), codec, _resolve_scope)


async def _resolve_scope(_request: Any, digest: str) -> RequestScope:
    return RequestScope("fixture-app", digest, "query", object(), "api4-test", monotonic() + 60)
