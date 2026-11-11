"""Generated-artifact-backed Record-root prepared API issuer."""

from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import cast

from graphql import build_schema, lexicographic_sort_schema, print_schema

from lintel.build.errors import PreparationError
from lintel.build.generated_roots import verify_generated_roots
from lintel.build.model import project_records
from lintel.build.prepare import (
    canonical_json,
    check_capabilities,
    check_exposure_shape,
    check_host,
    json_object,
    read_umf,
    record_json,
)
from lintel.build.prepare import render_sdl as build_sdl
from lintel.node_id import PROFILE as NODE_ID_PROFILE


def prepare_api_v2(
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
    """Issue exposure/2 only when UMF's generated verifier proves its Record roots."""
    source_bytes = bytes(umf_source)
    exposure_bytes = bytes(exposure)
    config = json_object(exposure_bytes, "INVALID_EXPOSURE")
    check_exposure_shape(config, "lintel.exposure/2", record_roots=True)
    profile = check_host(host_profile)
    caps = check_capabilities(capabilities, False, False, host_profile)
    cap_map = dict(caps)
    if cap_map.get("identity.codec") != NODE_ID_PROFILE:
        raise PreparationError("UNSUPPORTED", "identity.codec")
    profile["binding"] = cap_map["binding.profile"]
    if not scalar_codec_profile or cap_map.get("scalar.codec.profile") != scalar_codec_profile:
        raise PreparationError("UNSUPPORTED", "scalar.codec.profile")
    if config["connections"] or config["mutations"]:
        raise PreparationError("UNSUPPORTED", "selected operation binding profile")
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
    source_digest = hashlib.sha256(source_bytes).hexdigest()
    generated_roots = verify_generated_roots(
        generated_manifest,
        generated_files,
        generated_trust,
        generated_target,
        identity,
        source_digest,
        cap_map["binding.profile"],
        records,
    )
    _check_generated_bindings(generated_roots, cap_map, profile["binding"])
    sdl = print_schema(lexicographic_sort_schema(build_schema(build_sdl(records)))).rstrip() + "\n"
    schema_digest = hashlib.sha256(sdl.encode("utf-8")).hexdigest()
    api_digest = _api_digest_v2(
        exposure_bytes, source_entries, caps, profile, scalar_codec_profile, generated_roots, sdl
    )
    base: dict[str, object] = {
        "version": "lintel.prepared-api/2",
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
        "sdl": sdl,
        "schemaDigest": schema_digest,
        "apiDigest": api_digest,
        "generatedRoots": list(generated_roots),
    }
    base["artifactDigest"] = hashlib.sha256(canonical_json(base)).hexdigest()
    return canonical_json(base)


def _check_generated_bindings(
    roots: Sequence[Mapping[str, object]], capabilities: Mapping[str, str], binding: object
) -> None:
    if type(binding) is not str or not binding:
        raise PreparationError("UNSUPPORTED", "binding.profile")
    for root in roots:
        raw_lookup = root.get("lookup")
        if not isinstance(raw_lookup, Mapping):
            raise PreparationError("API_MISMATCH", "generated Record lookup")
        lookup = cast(Mapping[str, object], raw_lookup)
        module, identifier = lookup.get("module"), lookup.get("id")
        if type(module) is not str or type(identifier) is not str:
            raise PreparationError("API_MISMATCH", "generated Record lookup")
        identity = "/".join(_pointer(part) for part in (module, identifier, "record"))
        if (
            lookup.get("kind") != "record"
            or capabilities.get(f"operation.binding/{identity}") != binding
        ):
            raise PreparationError("UNSUPPORTED", "generated Record binding profile")


def _pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _api_digest_v2(
    exposure: bytes,
    sources: Sequence[tuple[str, str]],
    capabilities: Sequence[tuple[str, str]],
    host_profile: Mapping[str, object],
    scalar_profile: str,
    generated_roots: Sequence[Mapping[str, object]],
    sdl: str,
) -> str:
    limits = cast(Sequence[tuple[str, str]], host_profile["limits"])
    profile = tuple(
        sorted((*capabilities, *((f"host.limit.{key}", value) for key, value in limits)))
    )
    frames = [b"lintel.api/2", exposure]
    for identity, digest in sources:
        frames.extend((identity.encode("utf-8"), digest.encode("ascii")))
    frames.extend(
        (
            json.dumps(
                [list(pair) for pair in profile], ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8"),
            scalar_profile.encode("utf-8"),
            json.dumps(
                list(generated_roots),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8"),
            sdl.encode("utf-8"),
        )
    )
    return hashlib.sha256(b"".join(_frame(frame) for frame in frames)).hexdigest()


def _frame(value: bytes) -> bytes:
    return len(value).to_bytes(8, "big") + value


# Shared strict binding check for the API3 connection issuer.
check_generated_bindings = _check_generated_bindings
