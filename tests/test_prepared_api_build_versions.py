from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import cast

from lintel.build.prepare_generated_connection import api_digest_for_version

ROOT = Path(__file__).parents[1]


def test_shared_build_issuer_preserves_api4_digest_frame() -> None:
    artifact = json.loads(
        (ROOT / "tests/fixtures/prepared-api-v4-weft7-build27-proof.json").read_bytes()
    )
    sources = tuple((row["identity"], row["sha256"]) for row in artifact["sources"])
    capabilities = tuple(tuple(pair) for pair in artifact["capabilities"])
    digest = api_digest_for_version(
        base64.b64decode(artifact["exposureBase64"], validate=True),
        sources,
        capabilities,
        cast(dict[str, object], artifact["hostProfile"]),
        artifact["scalarCodecProfile"],
        artifact["generatedRoots"],
        artifact["generatedConnections"],
        artifact["sdl"],
        api_version="4",
    )
    assert digest == artifact["apiDigest"]
