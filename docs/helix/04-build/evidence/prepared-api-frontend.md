# Prepared API frontend qualification

Governing sources: CONTRACT-001 through CONTRACT-006, SD-001/SD-002, the
exposure/host/prepared-API schemas, the task-board logical example, and the
current execution-port interfaces. This receipt covers generic prepared-schema
loading and bounded GraphQL keyed refetch mechanics. The fixture is synthetic;
it does not qualify native Batten execution or the task-board host operations.

## Source and quality gate

Source checkout HEAD: `47fb8b2a3348307e52cddc2ad6bffb9ec3899c8c`;
the checkout had the frontend source changes shown in the accompanying patch
and one test-fixture path correction (`docs-design/examples` to the governed
`docs/helix/02-design/examples`). The repository itself was not modified while
running the gate; the corrected candidate was checked in `/private/tmp/lintel-full-quality`.

Command (with Ruff and uv caches redirected to `/private/tmp` and pytest's cache
provider disabled to avoid writing into the protected source checkout):

```sh
PYTHONPATH=build/src:src PYTEST_ADDOPTS='-p no:cacheprovider' \
  RUFF_CACHE_DIR=/private/tmp/lintel-ruff-cache \
  UV_CACHE_DIR=/private/tmp/lintel-uv-cache \
  /Users/erik/Projects/lintel/.venv/bin/python \
  /private/tmp/lintel-full-quality/scripts/check_quality.py
```

Observed output:

```text
All checks passed!
35 files already formatted
0 errors, 0 warnings, 0 informations
Spike import boundaries: PASS
63 passed, 1 warning in 1.14s
```

The sole warning is Starlette's deprecation notice for `httpx` with
`starlette.testclient`. The first direct-checkout attempt stopped during test
collection because the fixture path was wrong; the corrected candidate above
passes all 63 tests. The one-line source correction is included for application
with this evidence. No compiler is needed by runtime imports or requests.

## Artifact packaging and compiler separation

Fresh candidate set: `/private/tmp/lintel-frontend-candidate-20261104b/`.
The runtime `lintel-api` 0.1.0a2 wheel/sdist own `src/lintel` only and depend on
FastAPI 0.135.1, Strawberry GraphQL 0.339.1 and graphql-core 3.3.1. The distinct
`lintel-api-build` 0.1.0a1 wheel/sdist own `src/lintel_build`; it contains the
build-time UMF reader/validator path. RECORD and sdist ownership checks found no
runtime/build overlap. Earlier candidate directories were retained.

| Candidate | SHA-256 |
| --- | --- |
| `lintel_api-0.1.0a2-py3-none-any.whl` | `94f1540f3137cbae6b195083e791d52389540fdbba262bf70b13602c01c9924c` |
| `lintel_api-0.1.0a2.tar.gz` | `371086cbcb8c491be6e4a6bb6b90c5d2adb758d9efa920d2d51e77cd785e29d8` |
| `lintel_api_build-0.1.0a1-py3-none-any.whl` | `9e2114f71147bb36c0bfee3ea0bda183068dcb59dc0cb1260a104d3dfbb1a83c` |
| `lintel_api_build-0.1.0a1.tar.gz` | `be931d08a79d2247f3d398afdf42abe0cd615d1ed655a301fa436981fda1d352` |

The runtime wheel was installed alone into a clean target containing its selected
framework/runtime dependencies. Python started with site initialization disabled
(`-S`); the test inserted only that clean target and installed a finder that
raises if `umf` or `lintel_build` imports are attempted. Command:

```sh
/Users/erik/Projects/lintel/.venv/bin/python -S \
  /private/tmp/lintel-frontend-candidate-20261104b/clean-asgi.py
```

Observed output:

```text
clean runtime wheel ASGI request passed: {'data': {'node': {'id': 'demo.task-board.identity-v1:task-1', 'title': 'CleanWheel'}}}
```

The request traversed ASGI and GraphQL, read one selected `board.title` value
from a neutral fake execution port, used only the host-created authority handle,
and closed its request session. The fake is synthetic and returns a fixed row;
this proves package/compiler separation and generic dispatch wiring, not native
provider behavior, the real task-board model operations, Relay connections, or
Batten integration.

## Bounded result and remaining native work

The generic frontend supports a prepared-artifact path: the build distribution
produces a canonical artifact; runtime admission verifies it against an
independently supplied host pin; `create_router` requires the nominal admitted
artifact and checks port/codec profiles. The synthetic positive GraphQL fixture
covers selection collection including fragment/type-condition handling and
executable directives; malformed JSON and unsupported request extensions refuse
before dispatch; immutable host-profile and exact-type admission checks pass.

The fixture intentionally supplies synthetic qualified `request-snapshot-1`,
keyed lookup and scalar/identity binding capabilities. This is test scaffolding,
not evidence those capabilities exist in the selected native UMF/Weft cohort.
No Taskboard/Relay route is qualified for Batten. In particular, a singleton
native `get_one` observation does not establish request snapshot or ordered
batched `get_many` semantics.

Next native qualification slice: define and prove the concrete native request
session/snapshot lifecycle and ordered batched keyed `get_many` port semantics
(including duplicate, missing/denied slots, cancellation and cleanup) against the
selected UMF/Weft cohort. Then separately test a real Lintel adapter over that
port and update only the capability evidence it proves. Keep Taskboard/Relay
mounting gated until request-snapshot and the other selected profiles are proven.

## `/2` Record-root and string-key build-only qualification

This addendum records source-level `/2` preparation against the real local
Weft-generated `/4` artifact and `umf-access-generated-executor` 0.1.0a6 source.
The artifact was built from UMF core 0.10.0 and Weft SQL 0.4.63.dev1. The
original model SHA-256 is `856c0e5907aa16c77769e7ad75536b7b06bfe2fb7690a547a32f51249931dbbd`;
the generated read algebra SHA-256 is
`c1fe3e0e8458d32a181a3f4add612feb1e894fe422fdabfc92b1b08e66851f82`.
The build issuer used the real `GeneratedManifest`, `GeneratedFiles`,
`TrustedArtifactRef`, and `TargetBinding` classes and public `prepare_generated`
admission; no caller-created root map was supplied.

Command (local paths are the fixture and source checkouts used for this run):

```sh
PYTHONPATH=/private/tmp/lintel-record-root-stage/build/src:/private/tmp/lintel-record-root-stage/src:/Users/erik/Projects/umf/python/src:/private/tmp/umf-generated-read-v4-executor-a6-candidate4-unpack \
  /Users/erik/Projects/lintel/.venv/bin/python /private/tmp/lintel_v2_positive.py
```

Observed output:

```text
prepared version: lintel.prepared-api/2
source digest: 856c0e5907aa16c77769e7ad75536b7b06bfe2fb7690a547a32f51249931dbbd
root entries: [{"algebraSha256":"c1fe3e0e8458d32a181a3f4add612feb1e894fe422fdabfc92b1b08e66851f82","artifactDigest":"4fa4a4e62d57d6bb0794184896f1901e9b1c798f1a7b53052db2af81e917eb73","bindingDigest":"c09df86d9945ab99d79d15054df8d4d92c393444e125df1a40fe75b1b6ac2556","lookup":{"id":"Note","kind":"record","module":"demo"},"primaryKeyId":"primary","receiptDigest":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","sourceDigest":"856c0e5907aa16c77769e7ad75536b7b06bfe2fb7690a547a32f51249931dbbd"}]
SDL fields: owner,enabled,amount,payload
artifact bytes: 5287 artifact sha256: 53fa234381c5339d4c810f702b9b09fc3d6ec720adb252ba077205cae00414dc
```

This verifies the build-only parser/projection and the joins from exact source
bytes through the issued `/4` algebra, trusted receipt, target binding, native
catalog and selected Record/Key/Fields. The core UMF reader reported only
`UNKNOWN_EXTENSION` warnings for retained `umf.tables` and `umf.access` content;
the build issuer accepts those warning-only diagnostics only at the exact
`/vocabularies/umf.tables` and `/vocabularies/umf.access` paths and does not
interpret or rewrite either extension. The explicit GraphQL selection is limited
to `owner`, `enabled`, `amount`, and `payload`; the original string primary Key
field remains the hidden Node identity. This is not a native execution, request
snapshot, ordered `get_many`, or Batten route claim.

The runtime candidate is now 0.1.0a3 and the separate build candidate 0.1.0a2;
build metadata pins `umf-access-generated-executor==0.1.0a6`. Earlier a2/a1
wheel and sdist receipts above remain historical and unchanged. Fresh a3/a2
wheel/sdist hashes, clean installed-wheel request proof, and packaging ownership
checks are pending. Source quality for this staged candidate passes with Ruff,
Pyright (0 errors), import boundaries, and 83 tests (one existing
Starlette/httpx deprecation warning).

The stdlib `lintel.node-id.string-key/1` codec has round-trip, canonical input,
namespace mismatch, malformed string-wrapper, Unicode-surrogate, NUL and
byte-bound tests. It is routing identity only.

## Mixed `nodes` validation against the issued executor codec

The runtime owner supplied the pure public
`GeneratedExecutor.validate_get_many_key(module, record, key_id, components)`
validator in the 0.1.0a6 candidate wheel (SHA-256
`696dc892fa3e8929f210b6e49828e268a567384adfae6083656f5d2bb5f19fe9`). It uses
the same Rust-issued Key codec helper as `bind_get_many` and needs no scope,
lease or SQL operation. Host composition passed that bound method for the exact
prepared `demo.Note/primary` root to `StringKeyNodeCodec.for_prepared_api`.

Command:

```sh
PYTHONPATH=/private/tmp/lintel-record-root-stage/build/src:/private/tmp/lintel-record-root-stage/src:/private/tmp/lintel-record-root-stage/tests:/Users/erik/Projects/umf/python/src:/private/tmp/umf-generated-read-v4-executor-a6-candidate4-unpack \
  /Users/erik/Projects/lintel/.venv/bin/python /private/tmp/lintel_v2_mixed_real.py
```

Observed output:

```text
executor profile: weft.generated-read-algebra/4
status: 200
nodes: [{"id":"WyJsaW50ZWwubm9kZS1pZC5zdHJpbmcta2V5LzEiLCJmaXh0dXJlLmRlbW8udjEiLCJkZW1vIiwiTm90ZSIsInByaW1hcnkiLFsiZml4dHVyZS1ub3RlLTEiXV0","owner":"owner-value"},null,{"id":"WyJsaW50ZWwubm9kZS1pZC5zdHJpbmcta2V5LzEiLCJmaXh0dXJlLmRlbW8udjEiLCJkZW1vIiwiTm90ZSIsInByaW1hcnkiLFsiZml4dHVyZS1ub3RlLTEiXV0","owner":"owner-value"}]
dispatched keys: 2
invalid arity dispatched: False
```

This request traversed the Lintel GraphQL router with a fake neutral execution
port. The actual admitted `/4` executor validator rejected a canonical ID with
the wrong Key arity before dispatch; the two valid duplicate IDs remained
ordered and the middle slot returned null. This establishes the invalid-slot
filtering path against the issued key codec and generic router dispatch. It is
not evidence of a native provider session, request snapshot, batching semantics
for a native adapter, or Batten mount.
