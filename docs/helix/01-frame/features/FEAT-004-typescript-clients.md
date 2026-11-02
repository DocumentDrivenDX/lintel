---
ddx:
  id: FEAT-004
  type: feature-specification
  activity: frame
  authoring:
    home: repo
  links:
    - id: lintel.prd
      kind: informed_by
---

# FEAT-004: TypeScript Relay client builds

**Feature ID**: FEAT-004
**Priority**: P0
**Owner**: Lintel maintainers; named implementation assignee unassigned
**Covered PRD Subsystem(s)**: TypeScript client builds
**Covered PRD Requirements**: FR-7, FR-8
**Cross-Subsystem Rationale**: None — single subsystem.

## Overview

TypeScript Relay client builds lets the batten application author compile and run TypeScript operations and fragments. It realizes FR-7, FR-8
within the selected GraphQL/Relay and Batten profile.

## Ideal Future State

The author can compile and run TypeScript operations and fragments and use the exact API without duplicate handwritten types. Every supported behavior
has explicit schema/runtime capability and observed consumer evidence.

## Problem Statement

Current upstream model and runtime foundations do not establish this Lintel
capability. The outcome is one coherent supported path rather than per-app glue.

## Requirements

### Functional Requirements by Area

The implementation must satisfy each requirement below.

**CLIENT-01** — Export the admitted schema and compile selected operations/fragments through the pinned Relay toolchain with deterministic artifact manifests.
**CLIENT-02** — Provide host-configured network/scalar integration, drift refusal and application/actor-scoped normalized cache lifecycle.

### Non-Functional Requirements

Zero silent semantic coercions or cross-context authority leaks in the scoped
corpus. Mandatory finite host bounds. No passing implementation evidence is claimed.

## Detailed Behavior

Use exported SDL and selected documents with Relay public tooling; produce exact manifests and scope browser stores to the active host context.

Export the admitted SDL/api manifest and author the TaskRow fragment plus BoardQuery. Build through the supplied Relay toolchain and typecheck its generated TypeScript artifacts. Run the actual browser environment against Batten, page/refetch/complete and reconcile the result. Remove a selected field or switch actor/app context; stale builds fail and old store data is unavailable.

See [SD-004](../../02-design/solution-designs/SD-004-typescript-clients.md)
for the selected approach and business rules BR-7, BR-8.
Shared shapes and failure rules live in CONTRACT-003, CONTRACT-004.

## User Stories

- [US-004: Compile and run typescript operations and fragments](../user-stories/US-004-typescript-clients.md).

## Edge Cases and Error Handling

Unsupported selected meaning, foreign identities, changed sources and capability
mismatch refuse explicitly. Unknown mutation commitment is preserved for recovery.
Only applicable cases are exercised by this feature's story.

## Constraints and Assumptions

Python/FastAPI, GraphQL/Relay and Batten are selected. Architecture and upstream
change inventory govern ownership. Exact target surfaces are specified in CONTRACT-003, CONTRACT-004.
The corresponding solution/story designs apply them. Framework/native/toolchain
compatibility still requires the named interoperability proofs.

## Dependencies

FR-7, FR-8; [architecture](../../02-design/architecture.md);
[upstream changes](../../02-design/upstream-changes.md).

## Out of Scope

REST/OpenAPI product API, a new data compiler, and broader unsupported backend profiles.
