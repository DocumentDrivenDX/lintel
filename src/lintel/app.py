"""Mount an admitted prepared API on FastAPI with the in-memory port."""

from __future__ import annotations

from pathlib import Path
from time import monotonic
from typing import Any

from fastapi import FastAPI

from lintel.graphql import create_router
from lintel.memory import MemoryPort
from lintel.ports.protocols import ExecutionPort, NodeCodec
from lintel.ports.values import RequestScope
from lintel.projection import AdmittedPreparedApi, load_prepared_api
from lintel.trust import pin_for

DEMO_AUTHORITY = "lintel-demo-open-access"


def create_app(prepared: AdmittedPreparedApi, port: ExecutionPort, codec: NodeCodec) -> FastAPI:
    """Mount ``prepared`` with an unauthenticated demo scope (every caller allowed).

    Embedding hosts should call ``lintel.graphql.create_router`` with their own
    authenticating scope resolver instead.
    """

    async def resolve_context(_request: Any, digest: str) -> RequestScope:
        return RequestScope(
            prepared.application, digest, "query", DEMO_AUTHORITY, "demo", monotonic() + 30
        )

    app = FastAPI(title=f"lintel: {prepared.application}")
    app.include_router(create_router(prepared, port, codec, resolve_context))
    return app


def create_memory_app(
    artifact_path: str | Path, records_path: str | Path, expect_digest: str | None = None
) -> tuple[FastAPI, AdmittedPreparedApi]:
    """Load a prepared API artifact and records file; return the app and admitted API."""
    contents = Path(artifact_path).read_bytes()
    prepared = load_prepared_api(contents, pin_for(contents))
    if expect_digest is not None and prepared.api_digest != expect_digest:
        raise ValueError("API_MISMATCH")
    port = MemoryPort.from_json(prepared, Path(records_path).read_bytes())
    return create_app(prepared, port, port.codec), prepared
