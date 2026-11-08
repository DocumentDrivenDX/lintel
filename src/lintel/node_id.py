"""Portable, routing-only Node IDs for string-valued UMF primary Keys."""

from __future__ import annotations

import base64
import binascii
import json
from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import NamedTuple, Protocol, cast

from lintel.ports.values import ElementRef, NodeKey, OperationRef

PROFILE = "lintel.node-id.string-key/1"
_MAX_BYTES = 2048
_MAX_COMPONENTS = 16
KeyValidator = Callable[[str, str, str, tuple[object, ...]], tuple[object, ...]]
_ValidatorKey = tuple[ElementRef, str]
_Proof = tuple[str, str, str, str, str, str]


class PreparedRoots(Protocol):
    @property
    def version(self) -> str: ...

    @property
    def generated_roots(self) -> tuple[GeneratedRootInfo, ...]: ...


class GeneratedRootInfo(Protocol):
    @property
    def lookup(self) -> OperationRef: ...

    @property
    def source_digest(self) -> str: ...

    @property
    def artifact_digest(self) -> str: ...

    @property
    def receipt_digest(self) -> str: ...

    @property
    def binding_digest(self) -> str: ...

    @property
    def algebra_sha256(self) -> str: ...

    @property
    def primary_key_id(self) -> str: ...


class _ValidatorEntry(NamedTuple):
    proof: _Proof
    validator: KeyValidator


class StringKeyNodeCodec:
    """Canonical stdlib-only codec for required string Key components.

    Encoded values carry lookup identity only. They never confer host authority.
    """

    __slots__ = ("_validators", "_sealed")

    def __init__(self) -> None:
        self._validators: Mapping[_ValidatorKey, _ValidatorEntry] = MappingProxyType({})
        self._sealed = True

    def __setattr__(self, name: str, value: object) -> None:
        if getattr(self, "_sealed", False):
            raise AttributeError("StringKeyNodeCodec registry is immutable")
        object.__setattr__(self, name, value)

    @classmethod
    def for_prepared_api(
        cls,
        prepared: PreparedRoots,
        validators: Mapping[_ValidatorKey, KeyValidator],
    ) -> StringKeyNodeCodec:
        """Bind host-supplied executor validators to every admitted /2 or /3 root pin."""
        if prepared.version not in {
            "lintel.prepared-api/2",
            "lintel.prepared-api/3",
            "lintel.prepared-api/4",
        }:
            raise ValueError("API_MISMATCH")
        expected = _prepared_root_proofs(prepared)
        if set(validators) != set(expected) or any(
            not callable(value) for value in validators.values()
        ):
            raise ValueError("API_MISMATCH")
        instance = cls()
        entries = {key: _ValidatorEntry(proof, validators[key]) for key, proof in expected.items()}
        object.__setattr__(instance, "_validators", MappingProxyType(entries))
        return instance

    def registry_matches(self, prepared: PreparedRoots) -> bool:
        if prepared.version not in {
            "lintel.prepared-api/2",
            "lintel.prepared-api/3",
            "lintel.prepared-api/4",
        }:
            return False
        try:
            return _prepared_root_proofs(prepared) == {
                key: entry.proof for key, entry in self._validators.items()
            } and bool(self._validators)
        except ValueError:
            return False

    def profile(self) -> str:
        return PROFILE

    def encode(self, namespace: str, key: NodeKey) -> str:
        _nonempty_text(namespace)
        if type(key) is not NodeKey or type(key.record) is not ElementRef:
            raise ValueError("invalid NodeKey")
        _reference(key.record.module)
        _reference(key.record.element)
        _reference(key.key_id)
        components = _string_components(key.components)
        self._validate_components(key.record, key.key_id, components)
        payload = [
            PROFILE,
            namespace,
            key.record.module,
            key.record.element,
            key.key_id,
            components,
        ]
        raw = _canonical_json(payload)
        if len(raw) > _MAX_BYTES:
            raise ValueError("Node ID too large")
        encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
        if len(encoded) > _MAX_BYTES:
            raise ValueError("Node ID too large")
        return encoded

    def decode(self, namespace: str, value: str) -> NodeKey:
        _nonempty_text(namespace)
        key = _decode_key(namespace, _decode_payload(value))
        self._validate_components(key.record, key.key_id, _string_components(key.components))
        return key

    def _validate_components(self, record: ElementRef, key_id: str, components: list[str]) -> None:
        entry = self._validators.get((record, key_id))
        if entry is None:
            if self._validators:
                raise ValueError("unregistered Node Key")
            return
        wrappers = tuple({"string": value} for value in components)
        normalized = entry.validator(record.module, record.element, key_id, wrappers)
        if type(normalized) is not tuple or normalized != tuple(components):
            raise ValueError("Node Key rejected by issued codec")


def _prepared_root_proofs(prepared: PreparedRoots) -> dict[_ValidatorKey, _Proof]:
    result: dict[_ValidatorKey, _Proof] = {}
    for root in prepared.generated_roots:
        module, record, kind = root.lookup.module, root.lookup.id, root.lookup.kind
        key_id = root.primary_key_id
        if (
            type(module) is not str
            or not module
            or type(record) is not str
            or not record
            or kind != "record"
            or type(key_id) is not str
            or not key_id
        ):
            raise ValueError("API_MISMATCH")
        proof_values = (
            root.source_digest,
            root.artifact_digest,
            root.receipt_digest,
            root.binding_digest,
            root.algebra_sha256,
            root.primary_key_id,
        )
        if any(type(value) is not str or not value for value in proof_values):
            raise ValueError("API_MISMATCH")
        identity = (ElementRef(module, record), key_id)
        if identity in result:
            raise ValueError("API_MISMATCH")
        result[identity] = proof_values
    if not result:
        raise ValueError("API_MISMATCH")
    return result


def _decode_payload(value: str) -> list[object]:
    if type(value) is not str or not value or len(value) > _MAX_BYTES:
        raise ValueError("invalid Node ID")
    try:
        token = value.encode("ascii", errors="strict")
        if b"=" in token:
            raise ValueError("invalid Node ID")
        raw = base64.b64decode(token + b"=" * ((-len(token)) % 4), altchars=b"-_", validate=True)
        if len(raw) > _MAX_BYTES or _encode_raw(raw) != value:
            raise ValueError("invalid Node ID")
        decoded: object = json.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeError, binascii.Error, json.JSONDecodeError, ValueError) as error:
        raise ValueError("invalid Node ID") from error
    if type(decoded) is not list:
        raise ValueError("invalid Node ID")
    payload = cast(list[object], decoded)
    if len(payload) != 6 or _canonical_json(payload) != raw:
        raise ValueError("invalid Node ID")
    return payload


def _decode_key(namespace: str, payload: list[object]) -> NodeKey:
    profile, encoded_namespace, module, record, key_id, components = payload
    if (
        profile != PROFILE
        or encoded_namespace != namespace
        or type(module) is not str
        or type(record) is not str
        or type(key_id) is not str
    ):
        raise ValueError("invalid Node ID")
    _reference(module)
    _reference(record)
    _reference(key_id)
    if type(components) is not list:
        raise ValueError("invalid Node ID")
    typed_components = cast(list[object], components)
    if not 1 <= len(typed_components) <= _MAX_COMPONENTS:
        raise ValueError("invalid Node ID")
    return NodeKey(
        ElementRef(module, record),
        key_id,
        tuple(_wrapped_components(typed_components)),
    )


def _wrapped_components(components: list[object]) -> list[Mapping[str, object]]:
    wrapped: list[Mapping[str, object]] = []
    for component in components:
        if type(component) is not str:
            raise ValueError("invalid Node ID")
        _well_formed(component)
        wrapped.append({"string": component})
    return wrapped


def _string_components(values: tuple[object, ...]) -> list[str]:
    if type(values) is not tuple or not 1 <= len(values) <= _MAX_COMPONENTS:
        raise ValueError("invalid Key components")
    result: list[str] = []
    for value in values:
        if not isinstance(value, Mapping):
            raise ValueError("unsupported Key component")
        typed = cast(Mapping[str, object], value)
        if set(typed) != {"string"}:
            raise ValueError("unsupported Key component")
        component = typed.get("string")
        if type(component) is not str:
            raise ValueError("unsupported Key component")
        _well_formed(component)
        result.append(component)
    return result


def _canonical_json(value: object) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode(
            "utf-8", errors="strict"
        )
    except (UnicodeError, ValueError) as error:
        raise ValueError("invalid Node ID value") from error


def _encode_raw(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _nonempty_text(value: object) -> None:
    if type(value) is not str or not value:
        raise ValueError("expected nonempty text")
    _well_formed(value)


def _reference(value: object) -> None:
    _nonempty_text(value)


def _well_formed(value: str) -> None:
    if "\x00" in value:
        raise ValueError("NUL is unsupported by native text profile")
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError as error:
        raise ValueError("invalid UTF-8 text") from error


__all__ = ["PROFILE", "StringKeyNodeCodec"]
