# Lintel

Lintel turns a [UMF](https://github.com/DocumentDrivenDX/umf) document plus an
exposure file into a prepared GraphQL API and serves it with FastAPI.

**Status: alpha.** It works end to end against an in-memory data port. It has no
database-backed port yet, so it is not integrated with Truss, UMF Access or PostgreSQL.
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

Not provided: a Truss/UMF Access/PostgreSQL port, mutations, Relay connections served by
`lintel serve`, TypeScript clients, Batten embedding. Prepared-API v2 to v4 artifacts can be
loaded by the runtime, but their builders need `umf_access_generated_executor`, which is not
published, so they raise `UNSUPPORTED` without it.

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

## Experimental

`lintel.experimental` (install `lintel-api[experimental]`) is a laboratory projection with
`probe` and `echo` roots. It is not a production API and may change or disappear.

## Development

```sh
uv sync --locked
uv run ruff check . && uv run pyright && uv run pytest -q
```

[Changelog](CHANGELOG.md) · [Roadmap](ROADMAP.md)
