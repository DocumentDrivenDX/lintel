---
ddx:
  id: lintel.prd
  type: prd
  activity: frame
  authoring:
    home: repo
  links:
    - id: lintel.product-vision
      kind: informed_by
    - id: lintel.concerns
      kind: informed_by
---

# Lintel product requirements

## Summary

Lintel is a separately packaged Python API runtime embedded in Batten.
JSON:API reads and named commands are the default for the bounded task-board profile. It constructs an executable schema from current UMF declarations,
explicit exposure choices and qualified runtime capabilities. The admitted UMF
JSON document is the model input; Lintel requires no intermediate schema or
access-description API. An ORM may expose its underlying UMF unchanged through
a JSON accessor or transport when needed. Build tooling generates OpenAPI and
named operation descriptions from the admitted prepared API. GraphQL and Relay
remain available for existing consumers of the same prepared artifact.
The MVP is one complete fabricated task-board journey over PostgreSQL 18:
list/page, refetch, expand an assignee, execute a declared command, reconcile
an uncertain response and continue under Batten authority.

## Problem and Goals

### Problem

Handwritten API schemas/resolvers and TypeScript types can disagree with UMF
identity, constraints and declared mutations. Schema-only generation does not
prove executable access, correct pagination or host authorization.

### Goals

1. Authors expose selected reads and named commands from one admitted model and capability inventory.
2. Batten supplies Lintel in its complete qualified runtime cohort.
3. Browser clients compile against the exact published schema and preserve values.

### Success Metrics

Measure duplicate definitions removed, time to connect the reference app, and
client/server mismatches encountered during upgrades. Baselines and targets are
unknown; these are learning measures, not release gates.

### Non-Goals

A new ORM/compiler/policy engine; automatic unrestricted
CRUD; subscriptions/federation; arbitrary nested analytics; live schema hot swaps;
an admin UI; a new UI framework; production capacity or hostile-plugin isolation.
Databricks hosting does not imply Databricks SQL/Lakebase support.

## Users and Scope

### Primary Persona: Batten application author

Defines native UMF models, declared commands and TypeScript browser operations.
Needs a typed endpoint without maintaining duplicate resolvers and interfaces.

### Secondary Persona: Batten platform maintainer

Builds/adopts runtime cohorts and verifies application authority, lifecycle and
upgrades. Needs explicit capability limits and installed/native/browser evidence.

## Requirements

### Must Have (P0)

All FR-1–FR-12 below form the bounded MVP. Both server runtime and TypeScript
client artifacts are required. Local Batten integration is required.

### Should Have (P1)

Actual Databricks Apps deployment qualification, additional exact scalar profiles,
and broader qualified graph bindings after the local MVP. Configuration and
packaging for Databricks Apps are P0 under FR-11; a live workspace is a separate gate.

### Nice to Have (P2)

Live schema replacement, persisted-operation distribution, subscriptions,
federation and optional future API protocols.

## Functional Requirements

### Subsystem: Model admission and API projection

- **FR-1** — Derive a deterministic executable API from selected UMF declarations, with source/projection identity and explicit unknown-meaning diagnostics.
- **FR-2** — Activate only explicitly exposed, runtime-supported fields/relationships/operations; prevent dependency types from acquiring access rights.

### Subsystem: Reads and identity

- **FR-3** — Support authorized resource refetch and bounded forward cursor pagination with stable identity and declared consistency.
- **FR-4** — Expand selected one-hop relationships through bounded batched reads without cross-principal cache reuse or concealed endpoint leakage.

### Subsystem: Commands and outcomes

- **FR-5** — Invoke named, declared commands through Batten and the authoritative runtime, retaining validation, confirmation and current authorization.
- **FR-6** — Preserve exact values, typed business failures, replay and uncertain-write outcomes. Provide a separate observation operation and never automatically retry commands.

### Subsystem: TypeScript client builds

- **FR-7** — Generate OpenAPI and named operation descriptions from the admitted inventory. Generate a typed browser client with host-configured network integration.
- **FR-8** — Detect stale/breaking schema-client combinations and preserve exact custom scalar values and actor/application cache isolation.

### Subsystem: Batten embedding

- **FR-9** — Embed Lintel through public asynchronous Batten composition/lifecycle APIs, including per-application admission, authority and attribution.
- **FR-10** — Preserve borrowed resources, cancellation, scoped limits and deterministic startup refusal without runtime dependency installation or schema deployment.

### Subsystem: Delivery and family integration

- **FR-11** — Package the Python runtime and client build assets for the qualified Batten cohort, with local FastAPI and Databricks Apps hosting configuration.
- **FR-12** — Publish version/subset/evidence-qualified documentation and register Lintel in the DocumentDrivenDX family alongside UMF and Batten.

## Acceptance Test Sketches

| Journey | Observable outcome | Story |
| --- | --- | --- |
| Admit task-board model | Unsupported selected policy blocks activation; hidden fields stay absent | US-001 |
| Read tasks and assignee | Resource refetch agrees; page continuation and batched expansion retain authorized scope | US-002 |
| Complete a task | Host checks command authority; lost response remains uncertain until observation | US-003 |
| Build browser operations | The generated client build rejects a removed field; exact Decimal survives transport | US-004 |
| Mount in Batten | Same actor/app admission path; borrowed runtime survives API shutdown | US-005 |
| Deliver cohort and family entry | Installed artifacts and schema/client hashes match; public claims state limits | US-006 |

## Technical Context

Python/FastAPI is owner-selected. JSON:API and named commands share the
Batten execution ports with GraphQL. Relay tooling remains available for
GraphQL consumers. UMF models,
Weft compilation and existing access runtimes remain upstream authorities.
Architecture owns module/deployment choices; target shared surfaces are specified in CONTRACT-001–005. Native/library
interoperability still requires the bounded spikes before implementation claims.

## Constraints, Assumptions, Dependencies

Python 3.11 consumer floor and PostgreSQL 18 match Batten. Exact Databricks Apps
Python/framework versions require qualification. Runtime dependencies are supplied
at platform build time. Typed file settings are resolved once; no new environment
variables. No credentials, private application material or actual business data.
The initial profile covers two keyed records, scalar fields, one monomorphic
relationship and a declared task command. Broader meaning refuses explicitly.

## Risks

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Existing page API only returns a next-page cursor | Page continuation may lose authorization or ordering semantics | Runtime-owned cursor capability and explicit continuation links |
| A client reuses results across authority boundaries | A previous actor's data can become visible | Application-scoped identity, isolated stores, and stale-response rejection |
| Python introspection diverges from upstream semantics | Misleading API | Read UMF directly using its public reader/validator; no independent semantic engine |
| Relationship omission or scalar conversion weakens meaning | Wrong client results | Explicit projection rules and browser exact-value tests |
| Runtime query snapshots disagree within a request | Node field stability fails | Request-scoped consistency/reuse capability; qualify before claim |

## Open Questions

Qualify the installed distribution cohort and Batten/Databricks identity and
resource ownership. Broader relationship and write profiles require separate
qualification.
Family landing-page/catalog source and final project name remain unconfirmed.

## Success Criteria

The six stories have passing observed evidence at their allocated layers. One
installed Batten app exercises the generated HTTP client and named commands
in Chromium, backed by PostgreSQL 18, with denial, exact values,
paging, refetch, expansion and uncertain-mutation recovery. Documentation names
the exact qualified cohort and limits. Framing completion does not claim these
implementation gates have passed. Live Databricks qualification remains explicit.
