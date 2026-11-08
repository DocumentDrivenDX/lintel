"""Canonical digest framing for prepared API versions one through four."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence

from lintel.projection.prepared_v2 import PreparedGeneratedRoot, generated_roots_json
from lintel.projection.prepared_v3 import PreparedConnection, generated_connections_json


def api_digest(
    exposure: bytes,
    sources: Sequence[tuple[str, str]],
    capabilities: Sequence[tuple[str, str]],
    limits: Mapping[str, str],
    scalar_profile: str,
    sdl: str,
    generated_roots: Sequence[PreparedGeneratedRoot] | None = None,
    generated_connections: Sequence[PreparedConnection] | None = None,
    *,
    api_version: str | None = None,
) -> str:
    inferred = (
        "3" if generated_connections is not None else "2" if generated_roots is not None else "1"
    )
    version = inferred if api_version is None else api_version
    if version not in {"1", "2", "3", "4"} or (
        version == "4" and (generated_roots is None or generated_connections is None)
    ):
        raise ValueError("unsupported prepared API digest version")
    frames = [f"lintel.api/{version}".encode("ascii"), exposure]
    for identity, digest in sources:
        frames.extend((identity.encode("utf-8"), digest.encode("ascii")))
    profile = tuple(
        sorted((*capabilities, *((f"host.limit.{key}", value) for key, value in limits.items())))
    )
    frames.extend(
        (
            json.dumps(
                [list(pair) for pair in profile], ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8"),
            scalar_profile.encode("utf-8"),
        )
    )
    if generated_roots is not None:
        frames.append(generated_roots_json(generated_roots))
    if generated_connections is not None:
        frames.append(generated_connections_json(generated_connections))
    frames.append(sdl.encode("utf-8"))
    return hashlib.sha256(
        b"".join(len(item).to_bytes(8, "big") + item for item in frames)
    ).hexdigest()
