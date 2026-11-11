from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, cast

import pytest
from jsonschema import Draft202012Validator

from lintel.projection.prepared_digest import api_digest
from lintel.projection.prepared_v2 import generated_roots_from_json
from lintel.projection.prepared_v3 import generated_connections_from_json
from lintel.projection.prepared_v5 import (
    generated_connections_from_json as generated_connections_v5_from_json,
)

ROOT = Path(__file__).parents[1]


def test_prepared_api_v5_schema_requires_exact_api_and_weft_eight_profiles() -> None:
    raw = json.loads(
        (ROOT / "tests/fixtures/prepared-api-v4-weft7-build27-proof.json").read_bytes()
    )
    raw["version"] = "lintel.prepared-api/5"
    for connection in raw["generatedConnections"]:
        connection["profile"]["readProfile"] = "weft.generated-read-algebra/8"
    schema = json.loads(
        (ROOT / "docs/helix/02-design/schemas/prepared-api-v5.schema.json").read_bytes()
    )
    Draft202012Validator.check_schema(schema)
    validator = cast(Any, Draft202012Validator(schema))
    validator.validate(raw)
    wrong_version = dict(raw, version="lintel.prepared-api/4")
    assert list(validator.iter_errors(wrong_version))
    wrong_profile = json.loads(json.dumps(raw))
    wrong_profile["generatedConnections"][0]["profile"]["readProfile"] = (
        "weft.generated-read-algebra/7"
    )
    assert list(validator.iter_errors(wrong_profile))


def test_prepared_api_v5_connection_codec_refuses_v7_metadata() -> None:
    raw = json.loads(
        (ROOT / "tests/fixtures/prepared-api-v4-weft7-build27-proof.json").read_bytes()
    )
    with pytest.raises(ValueError, match="API_MISMATCH"):
        generated_connections_v5_from_json(raw["generatedConnections"])


def test_prepared_api_v5_digest_has_independent_lintel_api_framing() -> None:
    artifact = json.loads(
        (ROOT / "tests/fixtures/prepared-api-v4-weft7-build27-proof.json").read_bytes()
    )
    raw_exposure = base64.b64decode(artifact["exposureBase64"])
    sources = tuple((item["identity"], item["sha256"]) for item in artifact["sources"])
    capabilities = tuple(tuple(pair) for pair in artifact["capabilities"])
    limits = dict(artifact["hostProfile"]["limits"])
    roots = generated_roots_from_json(artifact["generatedRoots"])
    connections = generated_connections_from_json(
        artifact["generatedConnections"], expected_read_profile="weft.generated-read-algebra/7"
    )
    digest4 = api_digest(
        raw_exposure,
        sources,
        capabilities,
        limits,
        artifact["scalarCodecProfile"],
        artifact["sdl"],
        roots,
        connections,
        api_version="4",
    )
    digest5 = api_digest(
        raw_exposure,
        sources,
        capabilities,
        limits,
        artifact["scalarCodecProfile"],
        artifact["sdl"],
        roots,
        connections,
        api_version="5",
    )
    assert digest4 != digest5
