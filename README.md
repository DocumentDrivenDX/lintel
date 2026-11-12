# Lintel

Lintel turns a [UMF](https://github.com/DocumentDrivenDX/umf) document plus an
exposure file into a prepared GraphQL API and serves it with FastAPI.

**Status: alpha.** The standalone quickstart uses an in-memory data port.
Batten supplies PostgreSQL access for the qualified local task-board profile.
The PyPI project is `lintel-api` (the unrelated `lintel` project is a docstring checker).

## Quickstart

Python 3.11 or newer. This block is executed by CI from a freshly built wheel.

```sh quickstart
pip install --pre "lintel-api[build,serve]"
lintel example task-board demo
lintel prepare demo/task-board.umf.json --exposure demo/exposure.json --host demo/host-profile.json -o demo/api.json
# The server prints its x-lintel-api digest; use it as $DIGEST in a second terminal.
lintel serve demo/api.json --records demo/records.json &
curl -s localhost:8000/graphql -H "x-lintel-api: $DIGEST" -H 'content-type: application/json' -d '{"query":"{ node(id: \"demo.task-board.identity-v1:board.Task:task-1\") { id ... on Task { title estimate } } }"}'
```

The answer is `{"data":{"node":{"id":"demo.task-board.identity-v1:board.Task:task-1","title":"Write the quickstart","estimate":"3.50"}}}`.

`lintel example` writes four files: the UMF model, an exposure file (which records and
fields the API shows), a host profile (limits) and `records.json` (the demo rows).
`lintel prepare` validates the UMF document and issues `api.json`, a pinned artifact.
`lintel serve` admits the artifact and serves `POST /graphql` on `127.0.0.1:8000`.
Every request must send the artifact's digest in `x-lintel-api`. `serve` applies no
authentication; keep it on localhost.

## What is tested

CI (Linux, Python 3.11) tests: preparing v1 prepared APIs from UMF (`umf-core` 0.10.x),
keyed `node` / `nodes` reads through the in-memory port, runtime admission and tamper
checks, Node IDs, and the commands above from a built wheel in a fresh virtualenv.

The standalone `lintel serve` command covers in-memory keyed reads. The local
Batten comparison separately exercises prepared API v5 routes against PostgreSQL
18.6 with generated TypeScript in Chromium. The v2 through v5 builders require
`umf_access_generated_executor` and refuse when it is unavailable.

## Stack integration

Lintel imports only `umf-core` (the `build` extra; UMF validation and reading). It does not
import `umf-weft`, `umf-codegen`, `umf-access`, Truss or Ashlar. The runtime itself imports
no UMF package.

## Embedding

Mount the router in your own FastAPI app with your own authenticated scope and port:

```python
from lintel.graphql import create_router
from lintel.projection import load_prepared_api
router = create_router(prepared, my_execution_port, my_node_codec, resolve_scope)
```

`my_execution_port` implements `lintel.ports.ExecutionPort`; `lintel.memory.MemoryPort` is a
reference implementation. See [architecture](docs/helix/02-design/architecture.md) and the
[contracts](docs/helix/02-design/contracts/README.md).

## Prepared API v5 HTTP routes

`lintel.build.http_projection.project_http(prepared)` returns the OpenAPI 3.1
document and named operation definitions. Generate the browser client against
that document and configure its base URL to the deployed Lintel prefix. The
HTTP profile includes resource refetch, forward pages, one selected to-one
relationship per request, and separate command invocation and observation.

For Batten, mount both Lintel routers under the same `HostScopeIngress` and
pass its `resolve_context` to each. Give the HTTP router a dedicated prefix so
its operations do not collide with Batten's own `/api/operations` routes.

```python
from lintel.graphql import create_router as graphql_router
from lintel.http import create_router as http_router

api.include_router(graphql_router(prepared, execution, codec, ingress.resolve_context))
api.include_router(
    http_router(prepared, execution, codec, ingress.resolve_context), prefix="/lintel"
)
# Batten mounts ingress.wrap(api) at /api.
```

Requests send the admitted digest in `x-lintel-api`. This is the local Batten
task-board profile. The standalone quickstart continues to serve GraphQL.

## Experimental

`lintel.experimental` (install `lintel-api[experimental]`) is a laboratory projection with
`probe` and `echo` roots. It is not a production API and may change or disappear.

## Development

```sh
uv sync --locked
uv run ruff check . && uv run pyright && uv run pytest -q
```

[Changelog](CHANGELOG.md) · [Roadmap](ROADMAP.md)
