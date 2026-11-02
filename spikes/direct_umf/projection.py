"""S-01: read UMF itself, project a deliberately small scalar-only subset.

Not an alternative UMF validator: core validity/completeness belongs to umf-core.
This spike has no production activation path and no executor.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

# UMF generates Document dynamically; confine its incomplete static annotations here.
from umf import read_document, validate_document  # pyright: ignore[reportUnknownVariableType]

Ref = tuple[str, str]
RESERVED = {"Node", "Query", "Mutation", "PageInfo", "Decimal", "UUID", "PresenceProbe"}


class ProjectionError(ValueError):
    pass


@dataclass(frozen=True)
class Field:
    source: Ref
    name: str
    scalar: str
    optional: bool


@dataclass(frozen=True)
class Projection:
    source_text: str
    record: Ref
    name: str
    fields: tuple[Field, ...]


def _name(name: str) -> None:
    if not re.fullmatch(r"[_A-Za-z][_0-9A-Za-z]*", name) or name.startswith("__"):
        raise ProjectionError("NAME_COLLISION: invalid or reserved GraphQL name")


def project(source_text: str, record: Ref, name: str, fields: dict[Ref, str]) -> Projection:
    index = _read_index(source_text)
    _name(name)
    if name in RESERVED or name + "Input" in RESERVED:
        raise ProjectionError("NAME_COLLISION: generated or reserved type")
    owner = index.get(record)
    if owner is None or owner["kind"] != "record":
        raise ProjectionError("INVALID_EXPOSURE: expected UMF record")
    _subset(owner, {"id", "name", "kind", "members", "keys", "extensions"})
    members = {(ref["module"], ref["element"]) for ref in owner["members"]}
    projected: list[Field] = []
    names: set[str] = set()
    for ref, api_name in fields.items():
        _name(api_name)
        if api_name in names or api_name == "id":
            raise ProjectionError("NAME_COLLISION: duplicate or Relay id field")
        names.add(api_name)
        field = index.get(ref)
        if ref not in members or field is None or field["kind"] != "field":
            raise ProjectionError("INVALID_EXPOSURE: field is not a record member")
        _subset(
            field,
            {
                "id",
                "name",
                "kind",
                "scalarType",
                "cardinality",
                "nullability",
                "extensions",
                "facets",
            },
        )
        _check_scalar(field)
        projected.append(
            Field(ref, api_name, field["scalarType"], field["nullability"] == "absent-allowed")
        )
    if not projected:
        raise ProjectionError("INVALID_EXPOSURE: empty selection")
    return Projection(source_text, record, name, tuple(sorted(projected, key=lambda f: f.name)))


def _check_scalar(field: dict[str, Any]) -> None:
    if field.get("scalarType") not in {"string", "boolean", "decimal", "uuid"}:
        raise ProjectionError("UNSUPPORTED: scalar outside spike subset")
    if field.get("cardinality") != "one":
        raise ProjectionError("UNSUPPORTED: cardinality outside spike subset")
    if field.get("nullability") not in {"required", "absent-allowed"}:
        raise ProjectionError("UNSUPPORTED: availability outside spike subset")
    if field.get("facets", {}) and (
        field["scalarType"] != "decimal" or set(field["facets"]) - {"precision", "scale"}
    ):
        raise ProjectionError("UNSUPPORTED: facet outside spike subset")


def _read_index(source_text: str) -> dict[Ref, dict[str, Any]]:
    read_public = cast(Callable[[str], Any], read_document)
    document = read_public(source_text)
    validation = validate_document(document)
    if not validation.valid or not validation.complete:
        raise ProjectionError("UNSUPPORTED: UMF validation is invalid or incomplete")
    # Keep generated UMF types at this public parsing boundary; no private imports.
    data = cast(dict[str, Any], document.to_dict())
    index: dict[Ref, dict[str, Any]] = {}
    for module in data["modules"]:
        for element in module["elements"]:
            ref = (module["id"], element["id"])
            if ref in index:
                raise ProjectionError("AMBIGUOUS_IDENTITY: duplicate UMF reference")
            index[ref] = element
    return index


def _subset(element: dict[str, Any], supported: set[str]) -> None:
    if element.get("extensions") or set(element) - supported:
        raise ProjectionError("UNSUPPORTED: selected meaning outside spike subset")
