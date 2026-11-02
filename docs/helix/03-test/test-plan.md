---
ddx:
  id: TP-001
  type: test-plan
  activity: test
  authoring:
    home: repo
  links:
    - id: lintel.prd
      kind: informed_by
    - id: lintel.architecture
      kind: informed_by
---

# Lintel project test plan

## Strategy

Verify one complete admitted Batten application through the real GraphQL endpoint,
compiled Relay client and native PostgreSQL 18. Use focused contract/integration
cases to isolate projection, identity, cursor, exact-value and authorization faults.
A fake runtime supports adapter tests only; it never establishes native support.
All tests are planned and unrun. Framing checks are separate from product checks.

## Framework Selection & Cost

| Layer | Framework | Rationale | CI time impact | Maintenance cost |
| --- | --- | --- | --- | --- |
| Pure contract | pytest + Hypothesis | Exact projection/codec/boundary cases | Unmeasured; measure first suite | Low if input tables share behavior assertions |
| ASGI/host | pytest + HTTPX ASGI transport | Real schema/resolver/host boundary | Unmeasured; no database process for fast gate | Moderate; public interfaces only |
| Native | pytest + existing PostgreSQL 18 harness | Native RLS, cursors, transactions/outcomes | Unmeasured; separate database job | High enough to justify one shared fabricated corpus |
| Client build | Relay compiler + TypeScript, Bun driver | Actual operation/fragment types and drift | Unmeasured; pinned cohort | Reuse compiler; no custom generator |
| Browser | Playwright/Chromium | Actual Relay store/network/scalar behavior | Unmeasured; whole-path job | Small representative journey rather than copied unit suites |
| Packaging/docs | Installed wheels + link/schema manifest checks | Distribution and honest published claims | Unmeasured | Reuse Batten cohort and family publication tooling |

No coverage percentage, timing or test-count baseline is invented. Record first
measured costs; add a layer only for a distinct observable boundary.

## Critical Paths (P0)

1. US-001: deterministic schema and unsupported selected-meaning refusal.
2. US-002: Node refetch, per-edge continuation, batching and request consistency.
3. US-003: current command gates, exact values and uncertain outcome recovery.
4. US-004: real Relay compile/typecheck and browser normalization/isolation.
5. US-005: public Batten lifecycle, admission/custody and no startup effects.
6. US-006: complete installed cohort, artifacts and qualified family claims.

## Acceptance Criteria Layer Allocation

The concrete acceptance IDs, test names, assertions and required citations live
in each linked story's Test Scenarios. Future story test plans retain those IDs
and allocate actual files after Technical Designs; they must not claim nonexistent
tests as coverage. All 24 P0 criteria currently have planned primary layers.

| Criterion class / source | Primary Layer | Why this layer |
| --- | --- | --- |
| Projection/unknown/naming: US-001 | Contract, except dependency capability at Integration | Deterministic metadata plus public host boundary |
| Cursors/Node/relationships: US-002 | Native integration/E2E; store scope at Browser E2E | Native policy/order/consistency and actual normalization |
| Commands: US-003 | Native E2E; multi-field semantics at Integration | Actual commit/recovery and GraphQL execution behavior |
| Client artifacts: US-004 | Build integration then Browser E2E | Compiler and actual browser prove different boundaries |
| Host custody: US-005 | Integration/Installed integration; cancellation at Native integration | Public lifecycle plus real session ownership |
| Delivery: US-006 | Installed/Packaging/Docs integration | Installation and publication claims, not source import success |

## Secondary Paths (P1-P2)

Actual Databricks Apps execution (P1), broader semantic/backends (P1), then optional
live schema changes/subscriptions/federation (P2). These do not weaken M1 gates.

## Test Data Strategy

Fabricated task-board model: Task/Person with stable keys, one task-assignee
relationship, declared complete-task command and explicit native policies.
Include empty results, 1/50 parents, tied ordering values, missing/denied targets,
two apps with identical native keys, two principals, Unicode, exact large integers,
Decimal, UUID, absent/null and committed/lost mutation outcomes. Seed only through
explicit upstream administration. Use deterministic scenario inputs and a pinned
semantic faker for broader generated data; never fetch or copy business datasets.

## Known Gaps

No product implementation, frozen dependency lock, executed spikes, Technical
Designs or exact integration contracts exist yet. These block implementation
readiness and support claims, not the framing deliverable. Databricks workspace
and family catalog are unavailable in this session. Full backward paging,
subscription delivery and distributed/fleet capacity are outside the MVP.

## Build Commands

Planned project gates after scaffolding: `uv run pytest`, `uv run pyright`,
`uv run ruff check`, `uv run ruff format --check`,
`uv run python scripts/check_boundaries.py`, `bun run check:client-boundaries`,
`bun run build:relay`, `bun run check:relay`, and the selected browser job.
These commands are design targets; no pyproject/package scripts are supplied yet.

**Blocking gate:** before source handoff, establish actual commands, public
contracts and allowed/forbidden/cycle/private-import negative controls. Before
M1 delivery, every P0 criterion must be exercised, pass and carry its literal
`@covers US-<number>-AC<number>` citation. A populated document is not enforcement.

## Diagnostic Test Strategy (when applicable)

Use real instrumentation through a local OpenTelemetry receiver for request,
source/app/cohort context, native invocation and safe outcome correlation. Verify
pre-sink redaction, duplicate ingestion prevention, bounded export outage/shutdown
and unauthenticated lookup refusal. No arbitrary business values, IDs containing
secret keys or tokens enter telemetry. Pin protocol/convention versions in a
future diagnostic Contract. A framing run has no runtime trace to fabricate.
An implementation diagnostic pilot uses the known denied/stale/lost-response
scenarios and records diagnosis accuracy, time/calls and safe evidence references;
no unsupported performance budget is claimed.
