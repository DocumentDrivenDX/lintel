---
ddx:
  id: lintel.upstream-changes
  type: design-note
  activity: design
  authoring:
    home: repo
  links:
    - id: lintel.prd
      kind: informed_by
    - id: lintel.architecture
      kind: informed_by
---

# Required upstream changes and qualification gates

This is an upstream planning inventory; CONTRACT-001–005 now define Lintel target
interfaces, not accepted or implemented upstream APIs. No source
change or release is performed by this packet. Each row names its actual owner;
Lintel does not take ownership merely because it is the first consumer.

## Baseline and interpretation

UMF SDK 0.5.2 / core 0.10.0 / umf_access 0.1.0.dev4 / Weft 0.4.48 has published
scoped Python/PostgreSQL evidence. Batten's local candidate separately pins Weft
0.4.51. These are different cohorts: choose and qualify one intersection before
shipping Lintel. Older narrative entries saying seeds/evolution are wholly absent
are superseded by the scoped 0.5.2 release record; broader support is still bounded.

The UMF primary checkout has an uncommitted ADR-006/shared-Rust migration proposal.
Lintel should consume the shared engine's public Python descriptions as available;
it must not introduce an independent Python implementation of UMF semantics or
require the whole migration to finish before a bounded compatible delivery.

## Change inventory

| ID | Owner | Existing foundation | Required change / acceptance boundary |
| --- | --- | --- | --- |
| U-01 | UMF | Current core Fields/Records/Keys/Relationships/actions; Python reader | Supported language-neutral access-description API/schema available to Python; exact source/dependency identity, interpretation completeness, selectable operations and qualified capabilities. Remove Python-generator naming from semantic metadata. |
| U-02 | UMF | TypeScript Python-client generator returns a JSON description | Make description derivation independently callable without generating/importing Python code; expose through the shared engine/binding or a pinned build artifact. Dynamic runtime construction cannot scrape TS internals or run schema-selected templates. |
| U-03 | UMF | Exact literals, facets, unknown-preserving model | Reuse exact scalar/presence/identity metadata and operation input/output derivation. Add only demonstrated general metadata gaps upstream; keep GraphQL names/Relay cursors out of core. Semantic vocabulary references remain reference-only unless enforced. |
| R-01 | UMF access/runtime | Bounded pages and opaque next-page tokens | Versioned Relay-capable connection evidence: per-edge typed positions, stable ordering/key tie breaks, honest PageInfo, identity/query/order/source scope and explicit consistency. Interior-edge continuation must work; never synthesize offset paging. |
| R-02 | UMF access/runtime; Weft where lowering needs it | Keyed/related reads and declared native operations | Qualified batched key/relationship access with ordered missing slots, native policy enforcement, finite chunks and cancellation. No per-parent resolver query loop. |
| R-03 | Runtime | Per-call native sessions and source/head checks | Request-level consistency or equivalent materialization/reuse meeting Relay Node field stability under concurrency. State the actual snapshot guarantee and transaction ownership; do not infer a snapshot from a cursor or cache. |
| R-04 | Runtime | Declared writes, invocation keys, durable outcome observation | Public safe result/outcome metadata usable without generated client internals; retain applied/recovered/not-observed/unknown and durability facts, exact values and no retry. Qualify only supported native command/action profiles. |
| B-01 | Batten | Public async host and optional ASGI/table modules | Batten-owned optional `batten.lintel` adapter implements Lintel neutral ports; host composition injects its router. Query/mutation calls pass host admission, authority, confirmation and attribution. No Lintel-to-Batten dependency; generic core/ASGI do not import Lintel. |
| B-02 | Batten table/provider boundary | Local candidate TablePort.execute carries operation, inputs, phase, key and mutation | Public capability/description and bounded connection/batch/selection metadata seam. Current port does not expose page size/cursor context explicitly; resolve through a versioned owning contract, not private/native calls. |
| B-03 | Batten identity/provider boundary | Native adapter's local source constructs a person SessionIdentity | Preserve authenticated person versus explicit batch/service authority. Do not relabel all callers as people or infer batch authority from request shape. Required before claiming non-person API execution. |
| B-04 | Batten platform build | Complete runtime and TypeScript app direction | Include installed Lintel Python dependencies, Relay runtime/compiler build assets, exported SDL and exact manifests in the qualified cohort. No per-app pip/npm installation or startup tool download. |
| L-01 | Lintel | New project | Exposure selection, dynamic GraphQL schema/resolvers, Node IDs, connections/scalars, complexity limits, schema export and Relay build/check/network integration. Target Contracts 001–005 govern behavior; bounded spikes prove selected seams. |
| F-01 | Family site maintainer + Lintel | Existing Batten project Pages configuration; owner requests family membership | Identify actual landing-page/catalog owner; add project entry and reciprocal UMF/Batten links with design-stage status. Intended project path `/lintel/`; no existing catalog payload is invented. |

## Bounded spikes before implementation contracts

1. **S-01: Python projection and dynamic schema.** Feed the pinned current-core
   task/commerce model through upstream public metadata. Build/query/export a
   dynamic Strawberry schema, including key collisions, absent/null and exact
   decimal/UUID scalars. Pin compatible Python/FastAPI/Strawberry/Pydantic wheels.
   Pass means deterministic SDL and faithful requests without code generation,
   engine duplication or private imports.
2. **S-02: Relay native reads.** Prove arbitrary-edge continuation, honest PageInfo,
   batching, missing targets, hidden rows and concurrent Node stability on native
   PostgreSQL 18. Decide the supported forward profile and required runtime API.
   No full in-memory connection slicing or page-token relabeling is accepted.
3. **S-03: Batten execution and mutation.** Mount through public host APIs and
   exercise deny/confirmation, app scope, person/service distinction, borrowed
   shutdown and uncertain command recovery. Publish exact public boundary changes.
4. **S-04: Relay TypeScript build.** Compile operation/fragments/refetch/pagination,
   custom scalar mappings and mutation against exported SDL under the supplied
   toolchain. Exercise real browser normalization and context switching. Bun
   compatibility is measured; do not assume a Node-oriented compiler works.
5. **S-05: Databricks Apps.** Verify app start configuration, interpreter, locked
   dependency packaging, proxy trust, user vs app identity, shutdown and permitted
   native connectivity. Local packaging checks and actual workspace execution
   remain separate results.

The target exposure/projection, runtime, GraphQL, client and host contracts are
now specified. These spikes qualify their realizability and exact upstream/tool
versions before implementation. A failed spike requires an explicit contract
revision; it cannot silently remove required behavior. Host diagnostic wire
mapping/version pins remain owned by the embedding cohort.
Their names are scope allocations, not fabricated completed work items.

## Delivery sequence and cut lines

- **M0 — interoperable contracts:** S-01–04; upstream U/R/B agreements and qualified
  cohort; source import/boundary checker scaffold; no production support claim.
- **M1 — one local embedded MVP:** all six FR pairs and stories on one fabricated
  two-record task board; native PostgreSQL plus compiled Relay browser journey.
  Relay forward pagination, one-hop relationship, Node refetch and one authoritative
  mutation/recovery path are all required; none may be silently dropped.
- **M2 — deployed host:** execute S-05 in the selected workspace and publish exact
  Databricks Apps support. No inherited Lakebase/Databricks SQL qualification.
- **Later:** broader scalar/graph bindings, depth, subscriptions, federation and
  optional protocols only with separately selected requirements and evidence.

No staffing, dates, capacity target or runtime release number is invented.
