"""Closed one-hop relationship exposure shared by issuance and admission."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol, cast

from lintel.ports import ElementRef, OperationRef

_NAME = re.compile(r"(?!__)[_A-Za-z][_0-9A-Za-z]*")


class Record(Protocol):
    @property
    def source(self) -> ElementRef: ...
    @property
    def type_name(self) -> str: ...


@dataclass(frozen=True, slots=True)
class PreparedRelationship:
    source: ElementRef
    target: ElementRef
    relationship: ElementRef
    name: str
    operation: OperationRef


def relationships(
    exposure: Mapping[str, object],
    capabilities: Mapping[str, str],
    version: str,
) -> tuple[PreparedRelationship, ...]:
    result = tuple(
        _relationship(record, item)
        for record in _rows(exposure.get("records", []))
        for item in _rows(record.get("relationships", []))
    )
    if not result:
        return ()
    binding = capabilities.get("binding.profile")
    if (
        version != "lintel.prepared-api/5"
        or not binding
        or capabilities.get("relationship.batch") != "to-one-1"
        or capabilities.get("relationship.batch.binding.profile") != binding
        or {row.source for row in result} & {row.target for row in result}
        or len({(row.source, row.name) for row in result}) != len(result)
    ):
        raise ValueError("API_MISMATCH")
    return result


def _relationship(record: Mapping[str, object], item: Mapping[str, object]) -> PreparedRelationship:
    identity = _row(item.get("relationship"))
    operation = _row(item.get("operation"))
    name = item.get("name")
    if (
        set(item) != {"name", "relationship", "target", "operation"}
        or set(identity) != {"module", "id", "direction"}
        or identity["direction"] != "forward"
        or set(operation) != {"module", "id", "kind"}
        or operation["kind"] != "table"
        or type(name) is not str
        or not _NAME.fullmatch(name)
    ):
        raise ValueError("API_MISMATCH")
    return PreparedRelationship(
        _ref(record.get("record")),
        _ref(item["target"]),
        ElementRef(_text(identity["module"]), _text(identity["id"])),
        name,
        OperationRef(_text(operation["module"]), _text(operation["id"]), "table"),
    )


def relationship_sdl(
    sdl: str, selected: tuple[PreparedRelationship, ...], records: Sequence[Record]
) -> str:
    names = {record.source: record.type_name for record in records}
    if any(row.source not in names or row.target not in names for row in selected):
        raise ValueError("API_MISMATCH")
    return sdl + "".join(
        f"\nextend type {names[row.source]} {{ {row.name}: {names[row.target]} }}\n"
        for row in selected
    )


def _ref(value: object) -> ElementRef:
    row = _row(value)
    if set(row) != {"module", "element"}:
        raise ValueError("API_MISMATCH")
    return ElementRef(_text(row["module"]), _text(row["element"]))


def _rows(value: object) -> tuple[Mapping[str, object], ...]:
    if type(value) is not list or len(cast(list[object], value)) > 64:
        raise ValueError("API_MISMATCH")
    return tuple(_row(item) for item in cast(list[object], value))


def _row(value: object) -> Mapping[str, object]:
    if type(value) is not dict:
        raise ValueError("API_MISMATCH")
    return cast(dict[str, object], value)


def _text(value: object) -> str:
    if type(value) is not str or not value:
        raise ValueError("API_MISMATCH")
    return value
