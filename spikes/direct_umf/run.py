"""Reproducible local ASGI proof; no database or Batten support is claimed."""

from __future__ import annotations

import asyncio
import json
import sys
from importlib.metadata import version
from pathlib import Path

import httpx
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from spikes.direct_umf.schema import build_probe_schema, export_sdl


def main() -> None:
    # Projection import is intentionally owned by the composition root, not ASGI.
    from spikes.direct_umf.projection import project

    root = Path(__file__).resolve().parents[2]
    source = (root / "docs/helix/02-design/examples/task-board.umf.json").read_text()
    plan = project(
        source,
        ("board", "Task"),
        "Task",
        {
            ("board", "title"): "title",
            ("board", "estimate"): "estimate",
        },
    )
    schema = build_probe_schema(
        plan, {"title": "Fabricated task", "estimate": "9007199254740993.01"}
    )
    app = FastAPI()
    app.include_router(GraphQLRouter(schema), prefix="/graphql")

    async def request() -> dict[str, object]:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://spike.local"
        ) as client:
            response = await client.post("/graphql", json={"query": "{ probe { title estimate } }"})
            response.raise_for_status()
            return response.json()

    result = asyncio.run(request())
    assert result == {
        "data": {"probe": {"title": "Fabricated task", "estimate": "9007199254740993.01"}}
    }
    output = root / "docs/helix/04-build/evidence"
    (output / "s01-direct-umf.graphql").write_text(export_sdl(schema))
    receipt = {
        "spike": "S-01/direct-umf",
        "python": sys.version.split()[0],
        "cohort": {
            name: version(name)
            for name in [
                "umf-core",
                "strawberry-graphql",
                "graphql-core",
                "fastapi",
                "pydantic",
                "httpx",
            ]
        },
        "source": "docs/helix/02-design/examples/task-board.umf.json",
        "observed": result,
        "transport": "in-process HTTP through FastAPI ASGI",
        "upstreamChanges": [],
        "limitations": [
            "probe roots are not UMF operations",
            "no native execution or host admission",
            "no Relay identity/pagination/client/browser qualification",
        ],
    }
    (output / "s01-direct-umf.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
