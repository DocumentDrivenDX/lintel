"""Join explicit Record exposure to a verifier-issued generated read artifact."""

from __future__ import annotations

import hashlib
import importlib
import json
from collections.abc import Mapping, Sequence
from typing import Protocol, cast

from lintel.ports.values import ElementRef
from lintel_build.errors import PreparationError
from lintel_build.model import PreparedRecord

_PROFILE = "weft.generated-read-algebra/4"
_CONNECTION_PROFILE = "weft.generated-read-algebra/5"
_COMBINED_CONNECTION_PROFILE = "weft.generated-read-algebra/7"
_ALGEBRA_PATH = "algebra/read.json"


class _GeneratedExecutor(Protocol):
    @property
    def read_profile(self) -> str | None: ...

    @property
    def read_algebra_json(self) -> bytes: ...

    @property
    def native_table(self) -> object: ...

    @property
    def target(self) -> object: ...


class _NativeTable(Protocol):
    @property
    def source_digest(self) -> str: ...

    @property
    def native_source(self) -> Mapping[str, object]: ...


class _TargetBinding(Protocol):
    id: str
    profile: str
    version: str
    binding_digest: str


class _TrustedArtifactRef(Protocol):
    artifact_id: str
    artifact_digest: str
    receipt_digest: str
    source_digest: str
    target_binding_digest: str
    inventory: tuple[tuple[str, str], ...]


class _GeneratedFiles(Protocol):
    @property
    def mapping(self) -> Mapping[str, bytes]: ...

    @property
    def inventory(self) -> tuple[tuple[str, str], ...]: ...


class _GeneratedManifest(Protocol):
    @property
    def value(self) -> Mapping[str, object]: ...


class _GeneratedExecutorPackage(Protocol):
    GeneratedManifest: type[object]
    GeneratedFiles: type[object]
    TrustedArtifactRef: type[object]
    TargetBinding: type[object]

    def prepare_generated(
        self, manifest: object, files: object, trusted: object, target: object
    ) -> object: ...


def verify_generated_roots(
    manifest: object,
    files: object,
    trusted: object,
    target: object,
    source_identity: str,
    source_sha256: str,
    binding_profile: str,
    records: Sequence[PreparedRecord],
    *,
    expected_profile: str = _PROFILE,
) -> tuple[dict[str, object], ...]:
    """Validate the exact generated executor and produce its root receipt rows.

    Public package types are checked nominally here; `prepare_generated` repeats
    those checks at its own trust boundary. A mapping or caller-built root is
    never accepted as evidence.
    """
    executor = _admit_generated(manifest, files, trusted, target)
    try:
        read_profile = executor.read_profile
    except Exception as error:
        raise PreparationError("API_MISMATCH", "generated read profile") from error
    if read_profile != expected_profile:
        raise PreparationError("UNSUPPORTED", "generated read algebra profile")
    try:
        native = cast(_NativeTable, executor.native_table)
        executor_target = executor.target
    except Exception as error:
        raise PreparationError("API_MISMATCH", "generated native catalog") from error
    trusted_ref, target_binding, inventory = _verify_bindings(
        trusted, files, target, executor_target, native, source_sha256, binding_profile
    )
    algebra = _verified_algebra(executor, files, inventory)
    _check_manifest_source(
        cast(_GeneratedManifest, manifest).value, source_identity, source_sha256, records
    )
    roots = _algebra_roots(algebra, expected_profile)
    native_rows = _native_records(native.native_source, source_sha256)
    return _make_root_rows(
        roots, native_rows, records, source_sha256, trusted_ref, target_binding, inventory
    )


def _admit_generated(
    manifest: object, files: object, trusted: object, target: object
) -> _GeneratedExecutor:
    try:
        package = importlib.import_module("umf_access_generated_executor")
    except ImportError as error:
        raise PreparationError("UNSUPPORTED", "generated executor unavailable") from error
    public_package = cast(_GeneratedExecutorPackage, package)
    try:
        expected = (
            public_package.GeneratedManifest,
            public_package.GeneratedFiles,
            public_package.TrustedArtifactRef,
            public_package.TargetBinding,
        )
        prepare = public_package.prepare_generated
    except AttributeError as error:
        raise PreparationError("UNSUPPORTED", "generated executor API version") from error
    if tuple(type(value) for value in (manifest, files, trusted, target)) != expected:
        raise PreparationError("API_MISMATCH", "generated artifact value types")
    try:
        executor = prepare(manifest, files, trusted, target)
    except Exception as error:
        raise PreparationError("API_MISMATCH", "generated artifact admission") from error
    return cast(_GeneratedExecutor, executor)


def _verify_bindings(
    trusted: object,
    files: object,
    target: object,
    executor_target: object,
    native: _NativeTable,
    source_sha256: str,
    binding_profile: str,
) -> tuple[_TrustedArtifactRef, _TargetBinding, dict[str, str]]:
    trusted_ref = cast(_TrustedArtifactRef, trusted)
    target_binding = cast(_TargetBinding, target)
    if (
        executor_target != target
        or native.source_digest != source_sha256
        or trusted_ref.source_digest != source_sha256
        or trusted_ref.target_binding_digest != target_binding.binding_digest
        or target_binding.profile != binding_profile
    ):
        raise PreparationError("API_MISMATCH", "generated source or target binding")
    inventory = dict(cast(_GeneratedFiles, files).inventory)
    if inventory != dict(trusted_ref.inventory):
        raise PreparationError("API_MISMATCH", "generated inventory")
    return trusted_ref, target_binding, inventory


def _verified_algebra(
    executor: _GeneratedExecutor, files: object, inventory: Mapping[str, str]
) -> dict[str, object]:
    algebra_bytes = executor.read_algebra_json
    if (
        type(algebra_bytes) is not bytes
        or cast(_GeneratedFiles, files).mapping.get(_ALGEBRA_PATH) != algebra_bytes
        or inventory.get(_ALGEBRA_PATH) != hashlib.sha256(algebra_bytes).hexdigest()
    ):
        raise PreparationError("API_MISMATCH", "generated read algebra inventory")
    return _strict_object(algebra_bytes)


def _make_root_rows(
    roots: Mapping[str, object],
    native_rows: Mapping[tuple[str, str], frozenset[ElementRef]],
    records: Sequence[PreparedRecord],
    source_sha256: str,
    trusted_ref: _TrustedArtifactRef,
    target_binding: _TargetBinding,
    inventory: Mapping[str, str],
) -> tuple[dict[str, object], ...]:
    result: list[dict[str, object]] = []
    for record in records:
        identity = (record.source.module, record.source.element)
        root = _root_for(roots, identity, record)
        selected_fields = (*record.key_fields, *(field.source for field in record.fields))
        _check_native_fields(native_rows, identity, selected_fields)
        result.append(
            {
                "lookup": {"module": identity[0], "id": identity[1], "kind": "record"},
                "sourceDigest": source_sha256,
                "artifactDigest": trusted_ref.artifact_digest,
                "receiptDigest": trusted_ref.receipt_digest,
                "bindingDigest": target_binding.binding_digest,
                "algebraSha256": inventory[_ALGEBRA_PATH],
                "primaryKeyId": root["primaryKeyId"],
            }
        )
    return tuple(sorted(result, key=_root_order))


def _root_order(root: Mapping[str, object]) -> tuple[str, str]:
    lookup = root["lookup"]
    if not isinstance(lookup, Mapping):
        raise PreparationError("API_MISMATCH", "generated root lookup")
    typed = cast(Mapping[str, object], lookup)
    module, identifier = typed.get("module"), typed.get("id")
    if type(module) is not str or type(identifier) is not str:
        raise PreparationError("API_MISMATCH", "generated root identity")
    return (module, identifier)


def _strict_object(raw: bytes) -> dict[str, object]:
    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON member")
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=object_pairs)
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise PreparationError("API_MISMATCH", "generated read algebra JSON") from error
    if not isinstance(value, dict):
        raise PreparationError("API_MISMATCH", "generated read algebra shape")
    return cast(dict[str, object], value)


def _check_manifest_source(
    manifest: Mapping[str, object],
    source_identity: str,
    source_sha256: str,
    records: Sequence[PreparedRecord],
) -> None:
    source = manifest.get("source")
    if not isinstance(source, Mapping):
        raise PreparationError("API_MISMATCH", "generated manifest source")
    typed = cast(Mapping[str, object], source)
    if (
        typed.get("documentId") != source_identity
        or typed.get("sha256") != source_sha256
        or not isinstance(typed.get("moduleIds"), (list, tuple))
    ):
        raise PreparationError("API_MISMATCH", "generated manifest source")
    module_ids = cast(Sequence[object], typed["moduleIds"])
    if any(type(module) is not str or not module for module in module_ids) or not {
        record.source.module for record in records
    }.issubset(set(cast(Sequence[str], module_ids))):
        raise PreparationError("API_MISMATCH", "generated source modules")


def _algebra_roots(
    algebra: Mapping[str, object], expected_profile: str = _PROFILE
) -> Mapping[str, object]:
    if algebra.get("version") != expected_profile:
        raise PreparationError("UNSUPPORTED", "generated read algebra profile")
    raw_roots = algebra.get("roots")
    if not isinstance(raw_roots, Mapping):
        raise PreparationError("API_MISMATCH", "generated read roots")
    return cast(Mapping[str, object], raw_roots)


def _root_for(
    roots: Mapping[str, object], identity: tuple[str, str], record: PreparedRecord
) -> Mapping[str, object]:
    matches: list[Mapping[str, object]] = []
    for raw in roots.values():
        if not isinstance(raw, Mapping):
            raise PreparationError("API_MISMATCH", "generated read root")
        root = cast(Mapping[str, object], raw)
        if root.get("module") == identity[0] and root.get("record") == identity[1]:
            matches.append(root)
    if len(matches) != 1:
        raise PreparationError("UNSUPPORTED", "generated Record root")
    root = matches[0]
    fields = _root_fields(root, record)
    _check_primary_key(root, fields, record)
    _check_selected_fields(fields, record)
    return root


def _root_fields(root: Mapping[str, object], record: PreparedRecord) -> Mapping[str, object]:
    raw_fields = root.get("fields")
    if root.get("primaryKeyId") != record.key_id or not isinstance(raw_fields, Mapping):
        raise PreparationError("API_MISMATCH", "generated primary Key")
    return cast(Mapping[str, object], raw_fields)


def _check_primary_key(
    root: Mapping[str, object], fields: Mapping[str, object], record: PreparedRecord
) -> None:
    raw_primary = root.get("primaryKey")
    if not isinstance(raw_primary, list):
        raise PreparationError("API_MISMATCH", "generated primary Key")
    primary_fields = tuple(_primary_field(fields, item) for item in cast(list[object], raw_primary))
    if primary_fields != record.key_fields:
        raise PreparationError("API_MISMATCH", "generated primary Key fields")


def _primary_field(fields: Mapping[str, object], field_id: object) -> ElementRef:
    if not isinstance(field_id, Mapping):
        raise PreparationError("API_MISMATCH", "generated primary Key fields")
    primary = cast(Mapping[str, object], field_id)
    identifier, predicate = primary.get("fieldId"), primary.get("predicateId")
    if (
        set(primary) != {"fieldId", "predicateId"}
        or type(identifier) is not str
        or not identifier
        or type(predicate) is not str
        or not predicate
        or identifier not in fields
    ):
        raise PreparationError("API_MISMATCH", "generated primary Key fields")
    raw_field = fields[identifier]
    if not isinstance(raw_field, Mapping):
        raise PreparationError("API_MISMATCH", "generated Key field")
    return _element_ref(cast(Mapping[str, object], raw_field).get("sourceField"))


def _check_selected_fields(fields: Mapping[str, object], record: PreparedRecord) -> None:
    for selected in record.fields:
        matches: list[Mapping[str, object]] = []
        for item in fields.values():
            if not isinstance(item, Mapping):
                continue
            typed = cast(Mapping[str, object], item)
            if _element_ref(typed.get("sourceField")) == selected.source:
                matches.append(typed)
        if len(matches) != 1:
            raise PreparationError("UNSUPPORTED", "generated selected Field")


def _native_records(
    native_source: Mapping[str, object], source_sha256: str
) -> Mapping[tuple[str, str], frozenset[ElementRef]]:
    if native_source.get("sourceDigest") != source_sha256:
        raise PreparationError("API_MISMATCH", "native projection source")
    catalog = native_source.get("expectedCatalog")
    if not isinstance(catalog, Mapping):
        raise PreparationError("API_MISMATCH", "native catalog")
    tables = cast(Mapping[str, object], catalog).get("tables")
    if not isinstance(tables, (list, tuple)):
        raise PreparationError("API_MISMATCH", "native catalog tables")
    result: dict[tuple[str, str], frozenset[ElementRef]] = {}
    for raw in cast(Sequence[object], tables):
        if not isinstance(raw, Mapping):
            raise PreparationError("API_MISMATCH", "native table mapping")
        table = cast(Mapping[str, object], raw)
        record = table.get("record")
        identity = _element_ref(record)
        columns = table.get("columns")
        if not isinstance(columns, (list, tuple)):
            raise PreparationError("API_MISMATCH", "native table columns")
        field_refs: list[ElementRef] = []
        for column in cast(Sequence[object], columns):
            if not isinstance(column, Mapping):
                raise PreparationError("API_MISMATCH", "native table column")
            field_refs.append(_element_ref(cast(Mapping[str, object], column).get("field")))
        fields = frozenset(field_refs)
        key = (identity.module, identity.element)
        if key in result:
            raise PreparationError("AMBIGUOUS_IDENTITY", "native Record catalog")
        result[key] = fields
    return result


def _check_native_fields(
    native_rows: Mapping[tuple[str, str], frozenset[ElementRef]],
    identity: tuple[str, str],
    fields: Sequence[ElementRef],
) -> None:
    available = native_rows.get(identity)
    if available is None or any(field not in available for field in fields):
        raise PreparationError("UNSUPPORTED", "native Record fields")


def _element_ref(value: object) -> ElementRef:
    if not isinstance(value, Mapping):
        raise PreparationError("API_MISMATCH", "generated source reference")
    typed = cast(Mapping[str, object], value)
    module, element = typed.get("module"), typed.get("element")
    if type(module) is not str or not module or type(element) is not str or not element:
        raise PreparationError("API_MISMATCH", "generated source reference")
    return ElementRef(module, element)


# Shared build-only helpers used by the strict `/5` connection projector.
CONNECTION_PROFILE = _CONNECTION_PROFILE
COMBINED_CONNECTION_PROFILE = _COMBINED_CONNECTION_PROFILE
GeneratedNativeTable = _NativeTable
GeneratedManifestValue = _GeneratedManifest
admit_generated = _admit_generated
algebra_roots = _algebra_roots
check_manifest_source = _check_manifest_source
element_ref = _element_ref
native_records = _native_records
root_fields = _root_fields
root_for = _root_for
verified_algebra = _verified_algebra
verify_bindings = _verify_bindings
