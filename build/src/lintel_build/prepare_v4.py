"""Public strict prepared API four issuer."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from lintel_build.generated_roots import COMBINED_CONNECTION_PROFILE
from lintel_build.prepare_generated_connection import prepare_api_generated_connection


def prepare_api_v4(
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
    """Issue strict API `/4` using only Weft read algebra `/7`."""
    return prepare_api_generated_connection(
        umf_source,
        dependencies,
        exposure,
        capabilities,
        host_profile,
        scalar_codec_profile,
        generated_manifest,
        generated_files,
        generated_trust,
        generated_target,
        api_version="4",
        expected_profile=COMBINED_CONNECTION_PROFILE,
    )
