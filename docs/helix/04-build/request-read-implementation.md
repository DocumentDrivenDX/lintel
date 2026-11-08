# Upstream request-read implementation qualification

The native spike was committed and pushed as feafb8a. Its release-cohort findings
remain historical evidence. Local UMF/Weft candidates now implement its two gaps;
this does not claim the released cohort gained those interfaces.

[Installed-wheel native results](evidence/request-reads-native.json) cover exact
per-edge continuation and flags, hidden/deleted positions, resized pages, zero
first, native-role admission, stable snapshot fields, lifecycle locking, deadlines,
settings drift and cancellation. All28 leases return closed or idle. The
[legacy replay](evidence/request-reads-legacy.json) preserves S-02's ordinary page
semantics and its caller-owned RR refusal.

UMF owns `AsyncTableReader.request` and the two-lease lifecycle. Weft owns page and
previous-position SQL lowering. The model remains UMF; no description API or new
model format is introduced. API scope is a trusted host execution context value.
Source and artifact hashes live in the owning projects' verification receipts at
`docs/helix/04-build/evidence/lintel-request-reads/verification.json`.

The qualifier lives in `spikes/request_reads/qualify.py`. It requires the local
candidate UMF and Weft wheels in an isolated environment, rather than Lintel's
pinned released native-spike cohort. Run that interpreter with
`python -m spikes.request_reads.qualify`. Ordinary source verification remains
`uv run --locked --group spike --group native-spike python scripts/check_quality.py`.

No runtime package install or provider construction is added to product startup.
Initial qualification is async Psycopg3 direct leases, person identities and
PostgreSQL18.6. The host factory must support two leases. Lintel's neutral-port
adapter, generic pool/other-driver coverage, GraphQL/Relay clients and Batten
integration are not established by this native primitive qualification.


## Prepared GraphQL frontend qualification

Generic runtime/build separation and synthetic GraphQL-to-neutral-port dispatch are
recorded in [prepared API frontend evidence](evidence/prepared-api-frontend.md),
including wheel/sdist hashes, compiler-absence request output and the bounded
quality gate. This does not qualify native Batten execution or Taskboard/Relay
mounting. The next native slice is a real request-snapshot session plus ordered
batched keyed `get_many` qualification against the selected UMF/Weft cohort; the
existing singleton `get_one` result cannot establish either property.

Current staged Lintel source adds a separately versioned
`lintel.prepared-api/2` Record-root build path and the portable
`lintel.node-id.string-key/1` codec. The real `/4` generated artifact now
qualifies the build-only join; see the addendum in
[prepared API frontend evidence](evidence/prepared-api-frontend.md). This evidence
does not qualify the runtime `/2` wheel or a host adapter. The next product slice
remains native request-snapshot plus ordered batched `get_many`, followed by a
fresh runtime wheel and a compiler-absent request check.

For prepared `/2`, runtime composition now also requires exact
`StringKeyNodeCodec` validator coverage tied to each generated root's source,
artifact, receipt, binding, algebra and primary-Key pins. The callbacks must be
the pure `validate_get_many_key` method on the already admitted executor; this
prevents a canonical but invalid key from poisoning a mixed `nodes` batch. The
local `/4` candidate passed this mixed-slot GraphQL dispatch check as recorded in
the frontend evidence. Fresh wheel and provider-runtime qualification remain
separate gates.

The next source slice defines Lintel's closed `/3` prepared root-connection
issuer, strict `/5` metadata join, immutable planned-intent port, GraphQL
collection and bounded response encoding. Its source gate covers 96 tests,
including API2 fixture admission, exact connection-profile serialization,
closed `/3` exposure schema validation, grouped root alias budgets, fragment
collection, coerced defaults and active directives. The source gate itself does
not establish a Batten adapter, Host selected-session proof or a GraphQL-to-native
request. The strict `/5` artifact and Lintel a4 runtime/build a3 candidate package
checks are recorded in [API3 candidate wheel evidence](evidence/lintel-api3-a4-wheels-20261105/README.md). This evidence covers source/build admission and isolated runtime router creation only; Batten preflight, held native sessions, and native HTTP remain separate gates.

The byte limits have distinct scopes: the native result-frame guard is 8 MiB
per frame; Batten must charge serialized selected results across all calls
against the prepared `responseBytes` cap; Lintel independently caps final
UTF-8 GraphQL response bytes before releasing its request session. These
layers do not claim an 8 MiB process peak-memory bound.


## Local API3 native HTTP and Relay qualification — 2026-11-05

The exact Lintel runtime a4, UMF runtime dev15/executor a7 and seven compiler-free
Batten runtime wheels now have Sol-reviewed local macOS native HTTP and
Chromium evidence. Separate Batten
[source-composition](../../../../batten/docs/helix/04-build/evidence/local-batten-lintel-api3-http-source-20261105/browser-README.md)
and [installed-wheel](../../../../batten/docs/helix/04-build/evidence/local-batten-lintel-api3-http-installed-20261105/browser-README.md)
receipts identify their exact artifact, SDL, bundle, query/response and module
hashes. The installed runtime uses Python `-I`, no source-path fallback and no
UMF/Weft/build/compiler imports. Its dependency check covers 31 distributions.
The legacy Batten local fixture package is excluded because its initialization
extra still includes compiler tools.

One installed GraphQL request combines Note and Task connection aliases with
Node/getMany on two native leases; invalid cursors refuse with no lease.
Chromium 156.0.8078.4 traverses three Note edges over two pages, preserves exact
opaque cursor reuse, ordered Relay store merge/exhaustion and four scalar wire
values, and tests an authorized actor with no visible rows plus fresh-store
return. A parsed old response reaches the real generation/current-environment
guard after the actor transition. Unsubscription was also active, so this
proves the combined protection and stale branch observation, not isolated
causal necessity of that branch.

Browser cleanup counts are derived transcriptions of tool output; the distinct
installed direct check retains raw stdout. Temporary data, proof-owned role and
full original membership graph were restored, with no remaining client backend
excluding only the observer. The reviewed scopes do not establish a full ORM,
ordinary generated SDK `/5`, Linux `/5`, deployed Databricks Apps, or Workers
`/5` claim. The prior `/4` receipts retain their original cohorts.


## Local Workerd API3 qualification — 2026-11-05

The same API3 artifact and frozen Lintel a4/UMF dev15/executor a7 now have a
[reviewed real local Workerd receipt](../../../../batten/docs/helix/04-build/evidence/workerd-lintel-api3-20261105/README.md).
Six immutable Batten runtime wheels and the selected Worker-platform dependencies
run first=0, opaque cursor paging through three rows, mixed Note/Task/Node
requests, exact Decimal-string/Boolean transport, and an authorized actor with
no visible rows. Six database-backed requests each open and close one two-lease
pair; invalid cursors and oversized GraphQL documents open none. The selected
wheel payloads and compiler-module absence were checked in the actual Worker.

The scope is local Workerd through Wrangler Hyperdrive TCP to macOS PostgreSQL,
with a synthetic test identity header. The receipt retains actual versions and
all failed harness attempts. It records no final Workerd OS PID and the explicit
guarded fixture-cleanup fallback after the original owner process was unavailable;
rows and memberships were restored and the client census was empty. Native
8 MiB output-overflow, deployed authentication, Hyperdrive cache/pooling,
eviction/recovery, ordinary SDK `/5`, and full ORM coverage remain separate.
Linux `/5` is pending an unresponsive OrbStack environment; no VM was restarted.


## Proposed combined `/7` prepared API integration

The next combined ordinary Page and Relay proof cannot reuse prepared API `/3`:
its `generatedConnections[].profile.readProfile` is exactly Weft `/5`, while
the one-artifact UMF/Weft combined algebra is `/7`. CONTRACT-006 specifies an
additive prepared API `/4` with exact `/7` metadata and fresh digest framing.
Keep the authored `lintel.exposure/3` bytes, `prepare_api_v3` default and
accepted API `/2`/`/3` artifacts unchanged.

Build a separate `build/src/lintel_build/prepare_v4.py` public
`prepare_api_v4` entry. Parameterize the existing generated-root and
connection verifier helpers by an exact expected outer profile without
relaxing the `/3` entry: strict `/5` remains its default, strict `/7` belongs
only to `/4`. Reuse existing Record/Key/Field/native/allowed-profile joins and
SDL rendering. Issue `prepared-api/4`, `readProfile=/7`, and `lintel.api/4`
digest framing. Add a closed `prepared-api-v4.schema.json` with a new schema identity and
exact `/4` version and `/7` read-profile constraints; retain
`exposure-v3.schema.json`.

Runtime `src/lintel/projection/prepared.py` and `prepared_digest.py` register
`/4` as a connection-bearing version and verify its own schema, canonical
bytes, root/connection hashes, trust reference and `lintel.api/4` digest.
`prepared_v3.py` keeps its strict `/3` codec; a version-selected connection
codec handles exact `/7` for `/4` without rewriting `/3` rows. Extend only
version gates in `graphql/router.py`, `graphql/preflight.py`,
`graphql/resolvers.py` and `node_id.py`; retain the same
`ConnectionIntent`, planned port, SDL and StringKey Node codec. The TypeScript
client manifest stays `lintel.client/1`, using the `/4` SDL plus new API and
schema digests. Batten's adapter adds `/4` to its explicit prepared-version
admission and requires the selected `/7` capability. No runtime SQL/compiler,
native-driver or build-package import is added.

Qualify with `/3` byte-for-byte regression, default builder stability, both
cross-profile/mislabeled-profile refusals, malformed `/4` metadata and digest
refusals, exact Key/Field/native joins, Node codec registry, source/type gate,
and installed compiler-free local GraphQL/Relay first=0/interior/mixed
Note/Task/Node requests over one `/7` Host also serving standalone SDK Page.
Browser and Workerd claims need their own replay. Proposed distributions are
`lintel-api` 0.1.0a5 and `lintel-api-build` 0.1.0a4, with the builder pinning
the accepted new runtime and UMF executor versions only after their receipts
freeze; the accepted a4/a3 wheel bytes remain immutable.
