# Lintel

Dynamic GraphQL + Relay APIs from UMF, with an embeddable Python/FastAPI runtime
and generated TypeScript operation/fragment artifacts for Batten applications.

Lintel is a provisional name. This repository currently contains the HELIX
specifications and a bounded [direct UMF interoperability spike](docs/helix/02-design/spikes/SPIKE-001-direct-umf.md).
The spike reads UMF JSON through the public umf-core reader/validator and builds
a dynamic Strawberry schema. It is not a production API service.

Run `uv sync --locked --group spike --python 3.11`, then
`uv run --locked --group spike python -m spikes.direct_umf.run`.
[Verification and limits](docs/helix/04-build/direct-umf-spike.md) distinguish
this proof from native execution, Relay clients and Batten embedding.

Start with [the project packet](docs/helix/README.md),
[scope and MVP](docs/helix/01-frame/prd.md), and
[architecture](docs/helix/02-design/architecture.md).

The intended family documentation location is
[documentdrivendx.github.io/lintel](https://documentdrivendx.github.io/lintel/).
The [source repository](https://github.com/DocumentDrivenDX/lintel) is created;
family-catalog registration and documentation-site publication remain pending.
