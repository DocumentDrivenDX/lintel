# Direct UMF spike execution record

Governing scope: [SPIKE-001](../02-design/spikes/SPIKE-001-direct-umf.md),
CONTRACT-001 and the owner's direct-input clarification. HELIX catalog: installed
0.20.0 `workflows/graph.yml`. The first probe is bounded to direct scalar projection;
no token usage meter or comparable estimate is available, so no enforced spending
cap is claimed. No source changes in UMF or Batten are presumed necessary.

## Module map and boundaries

| Module | Owns | Allowed external imports |
| --- | --- | --- |
| projection | Read/validate source and resolve explicit qualified references | public umf only |
| schema | GraphQL translation and lexical codecs | projection, Strawberry, graphql-core |
| run | Fabricated ASGI composition and evidence receipt | projection, schema, FastAPI, HTTPX |

Check: `uv run --group spike python scripts/check_boundaries.py`.
AST import controls reject forbidden host/driver/framework imports, private
symbols and module paths, dynamic imports/eval/exec, and reverse schema-to-model
coupling. Allowed controls ensure the checker does not reject everything. The
permitted module graph is acyclic. It is a static architecture check, not a Python
security sandbox; no untrusted code is accepted. No existing source debt exists.

## Reproduce

```sh
uv sync --locked --group spike --python 3.11
uv run --locked --group spike python scripts/check_quality.py
uv run --locked --group spike python -m spikes.direct_umf.run
```

## Execution and continuation

Completed: governing specs now take UMF JSON directly; the actual import boundary
checker and controls pass; 40 behavioral cases pass; Ruff lint/format and strict
Pyright pass; FastAPI HTTP returns the exact fabricated Decimal string. The
lexical input codec rejects numeric JSON Decimal inputs and invalid UUID text.
GraphQL keyword names map to safe internal Python attributes without renaming
the public API or changing UMF.

Evidence: [checks and input hashes](evidence/s01-verification.json),
[ASGI response and cohort](evidence/s01-direct-umf.json),
[generated SDL](evidence/s01-direct-umf.graphql), and
[document checks](evidence/s01-document-checks.json),
[artifact checks](evidence/s01-artifact-checks.json), and
[quality negative controls](evidence/s01-quality-controls.json).

The observed cohort is Python 3.11.17, umf-core 0.10.0, Strawberry 0.339.1,
graphql-core 3.3.1, FastAPI 0.135.1 and Pydantic 2.14.2. uv.lock pins transitives.
The default local venv replacement stalled; execution used the same locked
project in `/private/tmp/lintel-s01-311`, selected through the uv build-tool
`UV_PROJECT_ENVIRONMENT` setting. This is not an application setting. The exact
commands are in the check receipt. The normal project `.venv` was subsequently
rebuilt from the lockfile, and the documented `uv run` probe succeeded there too.
No qualified Batten cohort or Databricks guarantee follows from this local probe.

**Upstream disposition:** no UMF/runtime/Batten source changes are demonstrated
necessary by this spike. The existing public UMF reader/validator suffices.
Incomplete static typing of dynamically generated upstream Document is confined
to one import and callable cast; it does not justify a new metadata interface.
The input/output echo roots are laboratory fixtures, not declared business
operations, and must not be published as a product API.

**Next action:** S-02 native reads and S-03 operation/host binding qualification.
Use existing UMF declarations first; change only an owning boundary where a real
execution probe fails. Full US-001 acceptance, native operation derivation, selective
unknown-meaning admission, Relay S-02/S-04 and Batten S-03 remain unqualified.
No OTel integration is claimed: this bounded tool writes a safe run receipt;
service/receiver instrumentation belongs to the later hosting slice.
