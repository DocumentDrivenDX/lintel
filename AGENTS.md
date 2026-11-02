# Working in Lintel

Start at `docs/helix/README.md`. Use the installed HELIX skill and `.helix.yml`;
keep governed artifacts under `docs/helix/`. Resolve the catalog from the installed
plugin. Preserve IDs, frontmatter, traceability and unfamiliar metadata.

Lintel is an independently packaged, embeddable Python GraphQL/Relay API runtime
in the UMF family, intended for inclusion in Batten's qualified runtime.
The owner selected Python/FastAPI, GraphQL + Relay and TypeScript client builds.
REST/OpenAPI product APIs are outside the MVP. The name is provisional.

UMF owns modeling and executable schema semantics; Weft owns SQL compilation;
the existing access/graph runtimes own execution. Batten owns application
admission, authenticated authority, confirmation, attribution and resource custody.
Lintel defines neutral public execution ports; Batten owns its integration adapter
in Batten. Lintel must not import Batten, and generic Batten core must not import
Lintel or GraphQL. Never duplicate an engine or bypass Batten's host.
Do not depend on any consuming application's internals.

Use Python 3.11 as the initial library compatibility floor; qualify the actual
Databricks Apps interpreter separately. Use uv, Ruff, Pyright and pytest.
Use TypeScript/Bun for Relay client build tooling and real Chromium checks.
No runtime package installation; no schema-selected code execution; no new
application environment variables. Configuration is typed, file-based and injected.
Use fabricated data. Qualify every claim by cohort, subset and observed evidence.

The packet specifies desired behavior; spikes/direct_umf contains a bounded
interoperability probe, not a production runtime or full conformance claim.
Consume UMF JSON directly; do not introduce an intermediate schema API.
Make upstream changes only for demonstrated gaps. Resolve the named spikes/contracts
before dependent implementation. Do not commit, push or publish unless asked.
