"""Derive a prepared-API pin from artifact bytes.

A pin copied from the artifact it checks only proves the bytes were not changed
after the pin was taken. Hosts that receive artifacts from elsewhere should pin the
digests from an independently obtained record and build ``TrustedPreparedRef``
themselves.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, cast

from lintel.projection.prepared import TrustedPreparedRef


def _pairs(rows: object) -> tuple[tuple[str, str], ...]:
    return tuple((str(row[0]), str(row[1])) for row in cast(list[list[Any]], rows))


def pin_for(artifact_bytes: bytes) -> TrustedPreparedRef:
    """Build a ``TrustedPreparedRef`` for a v1 or v2 prepared API artifact."""
    artifact = cast(dict[str, Any], json.loads(artifact_bytes))
    roots_sha256: str | None = None
    if artifact.get("version") == "lintel.prepared-api/2":
        roots_bytes = json.dumps(
            artifact["generatedRoots"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        roots_sha256 = hashlib.sha256(roots_bytes).hexdigest()
    elif artifact.get("version") != "lintel.prepared-api/1":
        raise ValueError("UNSUPPORTED")
    return TrustedPreparedRef(
        artifact_sha256=hashlib.sha256(artifact_bytes).hexdigest(),
        artifact_digest=artifact["artifactDigest"],
        application=artifact["application"],
        api_digest=artifact["apiDigest"],
        exposure_sha256=artifact["exposureSha256"],
        sources=tuple((s["identity"], s["sha256"]) for s in artifact["sources"]),
        capabilities=_pairs(artifact["capabilities"]),
        binding_profile=artifact["bindingProfile"],
        scalar_codec_profile=artifact["scalarCodecProfile"],
        limits=_pairs(artifact["hostProfile"]["limits"]),
        generated_roots_sha256=roots_sha256,
    )
