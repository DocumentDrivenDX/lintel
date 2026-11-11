"""In-memory execution port over a JSON records file (demo and test backend).

This is not a database integration: it serves rows held in process memory and
supports keyed ``node`` / ``nodes`` reads for prepared API v1. Connections,
relationships and commands answer ``UNSUPPORTED``.

Records file shape: ``{module: {element: {key: {field_element: value}}}}`` where
``key`` is the record's single string primary key and each field value is a JSON
string, or a boolean for boolean fields. Decimals are strings, never numbers.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from typing import Any, cast

from lintel.ports.errors import ExecutionError
from lintel.ports.values import (
    Arguments,
    CommandResult,
    ConnectionPage,
    CoreLiteral,
    ElementRef,
    NodeKey,
    NodeValue,
    OperationRef,
    RequestScope,
)
from lintel.projection.prepared import AdmittedPreparedApi, PreparedRecord

BINDING = "lintel.memory/1"
CODEC_PROFILE = "lintel.memory-node/1"
SCALAR_PROFILE = "lintel.scalars/1"
Rows = dict[str, dict[str, dict[str, dict[str, object]]]]


def _escape(segment: str) -> str:
    return segment.replace("~", "~0").replace("/", "~1")


def capabilities_for(exposure: Mapping[str, Any], host: Mapping[str, Any]) -> dict[str, str]:
    """Capability snapshot this port offers for an exposure file and host profile."""
    caps = {
        "lintel.execution": "1",
        "node.refetch": "1",
        "read.consistency": "request-snapshot-1",
        "identity.codec": CODEC_PROFILE,
        "binding.profile": BINDING,
        "scalar.codec.profile": SCALAR_PROFILE,
    }
    for name in (
        "lintel.execution",
        "node.refetch",
        "read.consistency",
        "identity.codec",
        "scalar.codec.profile",
    ):
        caps[f"{name}.binding.profile"] = BINDING
    for record in exposure.get("records", []):
        lookup = record["lookup"]
        key = f"operation.binding/{_escape(lookup['module'])}/{_escape(lookup['id'])}/"
        caps[key + lookup["kind"]] = BINDING
    for name, value in host["limits"].items():
        caps[f"limit.{name}"] = str(value)
        caps[f"limit.{name}.binding.profile"] = BINDING
    return caps


class MemoryNodeCodec:
    """Node IDs of the form ``<namespace>:<module>.<element>:<key>``."""

    def __init__(self, records: tuple[PreparedRecord, ...]) -> None:
        self._records = {f"{r.source.module}.{r.source.element}": r for r in records}

    def profile(self) -> str:
        return CODEC_PROFILE

    def encode(self, namespace: str, key: NodeKey) -> str:
        return f"{namespace}:{key.record.module}.{key.record.element}:{_key_text(key)}"

    def decode(self, namespace: str, value: str) -> NodeKey:
        prefix = namespace + ":"
        if not value.startswith(prefix):
            raise ValueError("invalid")
        name, separator, text = value[len(prefix) :].partition(":")
        record = self._records.get(name)
        if record is None or not separator or not text:
            raise ValueError("invalid")
        return NodeKey(record.source, record.key_id, ({"string": text},))


def _key_text(key: NodeKey) -> str:
    component = key.components[0] if len(key.components) == 1 else None
    text = component.get("string") if component else None
    if not isinstance(text, str):
        raise ValueError("invalid")
    return text


class _Session:
    def __init__(self, prepared: AdmittedPreparedApi, rows: Rows) -> None:
        self._records = {record.source: record for record in prepared.records}
        self._lookups = {record.lookup: record for record in prepared.records}
        self._rows = rows

    async def get_many(
        self,
        operation: OperationRef,
        keys: tuple[NodeKey, ...],
        fields: tuple[ElementRef, ...],
    ) -> tuple[NodeValue | None, ...]:
        record = self._lookups.get(operation)
        if record is None:
            raise ExecutionError("UNSUPPORTED")
        return tuple(self._value(record, key, fields) for key in keys)

    def _value(
        self, record: PreparedRecord, key: NodeKey, fields: tuple[ElementRef, ...]
    ) -> NodeValue | None:
        if key.record != record.source:
            return None
        row = self._rows.get(key.record.module, {}).get(key.record.element, {}).get(_key_text(key))
        if row is None:
            return None
        scalars = {field.source: field.scalar for field in record.fields}
        return NodeValue(key, {ref: _literal(row.get(ref.element), scalars[ref]) for ref in fields})

    async def connection(
        self,
        operation: OperationRef,
        arguments: Arguments,
        first: int,
        after: str | None,
        fields: tuple[ElementRef, ...],
    ) -> ConnectionPage:
        raise ExecutionError("UNSUPPORTED")

    async def related_many(
        self,
        operation: OperationRef,
        parents: tuple[NodeKey, ...],
        target: ElementRef,
        fields: tuple[ElementRef, ...],
    ) -> tuple[NodeValue | None, ...]:
        raise ExecutionError("UNSUPPORTED")

    async def invoke(
        self,
        operation: OperationRef,
        arguments: Arguments,
        invocation_key: str,
        confirmation: str | None,
    ) -> CommandResult:
        raise ExecutionError("UNSUPPORTED")

    async def observe(
        self, operation: OperationRef, arguments: Arguments, invocation_key: str
    ) -> CommandResult:
        raise ExecutionError("UNSUPPORTED")


def _literal(value: object, scalar: str) -> CoreLiteral:
    if value is None:
        return None
    wrapper = "decimalToken" if scalar == "decimal" else scalar
    return {wrapper: value}


class MemoryPort:
    """``ExecutionPort`` serving a records mapping for one admitted prepared API."""

    def __init__(self, prepared: AdmittedPreparedApi, rows: Rows) -> None:
        self._prepared = prepared
        self._rows = rows
        self.codec = MemoryNodeCodec(prepared.records)

    @classmethod
    def from_json(cls, prepared: AdmittedPreparedApi, raw: bytes | str) -> MemoryPort:
        rows: object = json.loads(raw)
        if not isinstance(rows, dict):
            raise ValueError("records file must be a JSON object")
        return cls(prepared, cast(Rows, rows))

    def capabilities(self) -> Mapping[str, str]:
        return dict(self._prepared.capabilities)

    @asynccontextmanager
    async def session(self, scope: RequestScope) -> AsyncGenerator[_Session, None]:
        yield _Session(self._prepared, self._rows)
