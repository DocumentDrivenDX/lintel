"""Runtime validation helpers for the additive prepared API v2 inventory."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from lintel.ports.values import OperationRef

if TYPE_CHECKING:
    from lintel.projection.prepared import PreparedRecord


@dataclass(frozen=True, slots=True)
class PreparedGeneratedRoot:
    lookup: OperationRef
    source_digest: str
    artifact_digest: str
    receipt_digest: str
    binding_digest: str
    algebra_sha256: str
    primary_key_id: str


def strict_object(raw: bytes) -> dict[str, object]:
    def pairs_hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def bad_constant(_value: str) -> object:
        raise ValueError("non-finite JSON number")

    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=pairs_hook,
            parse_constant=bad_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("API_MISMATCH") from error
    if not isinstance(value, dict):
        raise ValueError("API_MISMATCH")
    return cast(dict[str, object], value)


def generated_roots_from_json(value: object) -> tuple[PreparedGeneratedRoot, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError("API_MISMATCH")
    roots = tuple(_generated_root(raw) for raw in cast(list[object], value))
    identities = tuple((root.lookup.module, root.lookup.id) for root in roots)
    if tuple(sorted(identities)) != identities or len(set(identities)) != len(identities):
        raise ValueError("API_MISMATCH")
    return roots


def generated_roots_json(roots: Sequence[PreparedGeneratedRoot]) -> bytes:
    value = [
        {
            "lookup": {
                "module": root.lookup.module,
                "id": root.lookup.id,
                "kind": root.lookup.kind,
            },
            "sourceDigest": root.source_digest,
            "artifactDigest": root.artifact_digest,
            "receiptDigest": root.receipt_digest,
            "bindingDigest": root.binding_digest,
            "algebraSha256": root.algebra_sha256,
            "primaryKeyId": root.primary_key_id,
        }
        for root in roots
    ]
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def join_generated_roots(
    records: Sequence[PreparedRecord],
    roots: Sequence[PreparedGeneratedRoot],
    sources: Sequence[tuple[str, str]],
    version: object,
) -> None:
    if version == "lintel.prepared-api/1":
        if roots or any(record.lookup.kind == "record" for record in records):
            raise ValueError("API_MISMATCH")
        return
    record_map = {(record.source.module, record.source.element): record for record in records}
    root_map = {(root.lookup.module, root.lookup.id): root for root in roots}
    source_hashes = {digest for _identity, digest in sources}
    if set(record_map) != set(root_map):
        raise ValueError("API_MISMATCH")
    for identity, record in record_map.items():
        root = root_map[identity]
        if (
            record.lookup != root.lookup
            or record.lookup.module != record.source.module
            or record.lookup.id != record.source.element
            or record.key_id != root.primary_key_id
            or root.source_digest not in source_hashes
        ):
            raise ValueError("API_MISMATCH")


def _generated_root(value: object) -> PreparedGeneratedRoot:
    expected = {
        "lookup",
        "sourceDigest",
        "artifactDigest",
        "receiptDigest",
        "bindingDigest",
        "algebraSha256",
        "primaryKeyId",
    }
    if not isinstance(value, dict):
        raise ValueError("API_MISMATCH")
    typed = cast(dict[str, object], value)
    if set(typed) != expected:
        raise ValueError("API_MISMATCH")
    lookup = typed["lookup"]
    if not isinstance(lookup, dict):
        raise ValueError("API_MISMATCH")
    ref = cast(dict[str, object], lookup)
    if set(ref) != {"module", "id", "kind"} or ref.get("kind") != "record":
        raise ValueError("API_MISMATCH")
    module, identifier = ref.get("module"), ref.get("id")
    if type(module) is not str or not module or type(identifier) is not str or not identifier:
        raise ValueError("API_MISMATCH")
    primary_key_id = typed["primaryKeyId"]
    if type(primary_key_id) is not str or not primary_key_id:
        raise ValueError("API_MISMATCH")
    return PreparedGeneratedRoot(
        OperationRef(module, identifier, "record"),
        _digest(typed, "sourceDigest"),
        _digest(typed, "artifactDigest"),
        _digest(typed, "receiptDigest"),
        _digest(typed, "bindingDigest"),
        _digest(typed, "algebraSha256"),
        primary_key_id,
    )


def _digest(value: Mapping[str, object], key: str) -> str:
    digest = value.get(key)
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("API_MISMATCH")
    return digest
