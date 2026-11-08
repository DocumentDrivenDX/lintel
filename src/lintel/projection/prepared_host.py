"""Closed validation and freezing for admitted host limit profiles."""

from __future__ import annotations

import re
from collections.abc import Mapping
from types import MappingProxyType
from typing import cast

_LIMIT_BOUNDS = {
    "defaultPage": (0, 25),
    "maxPage": (1, 100),
    "maxLookup": (1, 100),
    "relationshipBatch": (1, 100),
    "maxRelationshipHops": (1, 1),
    "maxDepth": (1, 8),
    "maxFieldOccurrences": (1, 256),
    "maxAliases": (1, 32),
    "maxCost": (1, 10000),
    "maxMutationFields": (1, 4),
    "maxConcurrentDispatch": (1, 8),
    "requestBytes": (1, 1048576),
    "responseBytes": (1, 8388608),
    "documentBytes": (1, 262144),
    "deadlineMs": (1, 30000),
    "nodeIdBytes": (1, 2048),
    "cursorBytes": (1, 4096),
    "invocationKeyBytes": (1, 128),
}


def host_profile(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("API_MISMATCH")
    typed = cast(dict[str, object], value)
    if set(typed) != {"mount", "introspection", "limits"}:
        raise ValueError("API_MISMATCH")
    mount, introspection, raw_limits = (
        typed.get("mount"),
        typed.get("introspection"),
        typed.get("limits"),
    )
    pairs = _host_pairs(raw_limits)
    if tuple(sorted(pairs)) != tuple(pairs) or len({key for key, _ in pairs}) != len(pairs):
        raise ValueError("API_MISMATCH")
    limits = dict(pairs)
    if not _valid_host_envelope(mount, introspection, limits):
        raise ValueError("API_MISMATCH")
    numeric = {name: int(item) for name, item in limits.items()}
    if any(not low <= numeric[name] <= high for name, (low, high) in _LIMIT_BOUNDS.items()):
        raise ValueError("API_MISMATCH")
    if (
        numeric["defaultPage"] > numeric["maxPage"]
        or numeric["relationshipBatch"] > numeric["maxLookup"]
    ):
        raise ValueError("API_MISMATCH")
    return {"mount": mount, "introspection": introspection, "limits": limits}


def _host_pairs(value: object) -> list[tuple[str, str]]:
    if not isinstance(value, list):
        raise ValueError("API_MISMATCH")
    pairs: list[tuple[str, str]] = []
    for pair in cast(list[object], value):
        if not isinstance(pair, list) or len(cast(list[object], pair)) != 2:
            raise ValueError("API_MISMATCH")
        key, item = cast(list[object], pair)
        if type(key) is not str or not key or type(item) is not str or not item:
            raise ValueError("API_MISMATCH")
        pairs.append((key, item))
    return pairs


def _valid_host_envelope(mount: object, introspection: object, limits: Mapping[str, str]) -> bool:
    return (
        isinstance(mount, str)
        and re.fullmatch(r"/(?:[A-Za-z0-9_-]+/)*graphql", mount) is not None
        and isinstance(introspection, bool)
        and set(limits) == set(_LIMIT_BOUNDS)
        and all(item.isdecimal() for item in limits.values())
    )


def freeze_host(host: dict[str, object]) -> Mapping[str, object]:
    limits = cast(dict[str, str], host["limits"])
    frozen: dict[str, object] = {
        "mount": host["mount"],
        "introspection": host["introspection"],
        "limits": MappingProxyType(dict(limits)),
    }
    return MappingProxyType(frozen)
