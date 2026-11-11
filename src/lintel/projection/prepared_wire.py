"""Closed JSON and scalar field readers for prepared API artifacts."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from collections.abc import Mapping
from typing import Final, cast

from graphql import build_schema, lexicographic_sort_schema, print_schema

from lintel.projection.prepared_v2 import strict_object

_SHA256: Final = re.compile(r"^[0-9a-f]{64}$")


def canonical_json(value: Mapping[str, object]) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def decode_exposure(artifact: Mapping[str, object]) -> bytes:
    encoded = artifact.get("exposureBase64")
    if not isinstance(encoded, str):
        raise ValueError("API_MISMATCH")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except ValueError as error:
        raise ValueError("API_MISMATCH") from error
    if base64.b64encode(raw).decode("ascii") != encoded or hashlib.sha256(
        raw
    ).hexdigest() != digest(artifact, "exposureSha256"):
        raise ValueError("API_MISMATCH")
    exposure = strict_object(raw)
    expected_format = {
        "lintel.prepared-api/2": "lintel.exposure/2",
        "lintel.prepared-api/3": "lintel.exposure/3",
        "lintel.prepared-api/4": "lintel.exposure/3",
        "lintel.prepared-api/5": "lintel.exposure/3",
    }.get(cast(str, artifact.get("version")), "lintel.exposure/1")
    if exposure.get("format") != expected_format:
        raise ValueError("API_MISMATCH")
    return raw


def source_pairs(value: object) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, list):
        raise ValueError("API_MISMATCH")
    pairs: list[tuple[str, str]] = []
    for raw_source in cast(list[object], value):
        if not isinstance(raw_source, dict):
            raise ValueError("API_MISMATCH")
        typed = cast(dict[str, object], raw_source)
        if set(typed) != {"identity", "sha256"}:
            raise ValueError("API_MISMATCH")
        pairs.append((string_value(typed, "identity"), digest(typed, "sha256")))
    result = tuple(pairs)
    if (
        not result
        or tuple(sorted(result)) != result
        or len({key for key, _ in result}) != len(result)
    ):
        raise ValueError("API_MISMATCH")
    return result


def pairs(value: object) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, list):
        raise ValueError("API_MISMATCH")
    result: list[tuple[str, str]] = []
    for raw_pair in cast(list[object], value):
        if not isinstance(raw_pair, list):
            raise ValueError("API_MISMATCH")
        pair = cast(list[object], raw_pair)
        if len(pair) != 2 or not all(nonempty(item) for item in pair):
            raise ValueError("API_MISMATCH")
        result.append((cast(str, pair[0]), cast(str, pair[1])))
    if len({key for key, _ in result}) != len(result):
        raise ValueError("API_MISMATCH")
    return tuple(result)


def canonical_sdl(sdl: str) -> str:
    schema = lexicographic_sort_schema(build_schema(sdl))
    return print_schema(schema).rstrip() + "\n"


def digest(value: Mapping[str, object], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not _SHA256.fullmatch(item):
        raise ValueError("API_MISMATCH")
    return item


def string_value(value: Mapping[str, object], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ValueError("API_MISMATCH")
    return item


def bool_value(value: Mapping[str, object], key: str) -> bool:
    item = value.get(key)
    if not isinstance(item, bool):
        raise ValueError("API_MISMATCH")
    return item


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value)
