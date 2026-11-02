---
ddx:
  id: FEAT-001
  type: feature-specification
  activity: frame
  authoring:
    home: repo
  links:
    - id: lintel.prd
      kind: informed_by
---

# FEAT-001: Model admission and API projection

**Feature ID**: FEAT-001
**Priority**: P0
**Owner**: Lintel maintainers; named implementation assignee unassigned
**Covered PRD Subsystem(s)**: Model admission and API projection
**Covered PRD Requirements**: FR-1, FR-2
**Cross-Subsystem Rationale**: None — single subsystem.

## Overview

Model admission and API projection lets the batten application author expose a selected UMF model. It realizes FR-1, FR-2
within the selected GraphQL/Relay and Batten profile.

## Ideal Future State

The author can expose a selected UMF model and avoid separate handwritten GraphQL types. Every supported behavior
has explicit schema/runtime capability and observed consumer evidence.

## Problem Statement

Current upstream model and runtime foundations do not establish this Lintel
capability. The outcome is one coherent supported path rather than per-app glue.

## Requirements

### Functional Requirements by Area

The implementation must satisfy each requirement below.

**PROJ-01** — Derive a deterministic API plan from approved current UMF source, retaining original identities and source provenance.
**PROJ-02** — Expose only selected, understood capabilities; diagnose collisions and unsupported selected meanings before activation.

### Non-Functional Requirements

Zero silent semantic coercions or cross-context authority leaks in the scoped
corpus. Mandatory finite host bounds. No passing implementation evidence is claimed.

## Detailed Behavior

Resolve explicit model identities through the supported upstream description; build one immutable exposure plan and deterministic schema without interpreting unknown rules.

Supply the approved task-board logical source, exact description/capability profile and explicit exposure. Prepare the API and inspect the sorted SDL, identity digests and safe diagnostics. Repeat preparation with identical bytes, then select an unknown constraint or a colliding Relay name. Receive byte-identical output or a non-mutating preparation refusal; no dependency record gains an implicit list.

See [SD-001](../../02-design/solution-designs/SD-001-model-projection.md)
for the selected approach and business rules BR-1, BR-2.
Shared shapes and failure rules live in CONTRACT-001, CONTRACT-005.

## User Stories

- [US-001: Expose a selected umf model](../user-stories/US-001-model-projection.md).

## Edge Cases and Error Handling

Unsupported selected meaning, foreign identities, changed sources and capability
mismatch refuse explicitly. Unknown mutation commitment is preserved for recovery.
Only applicable cases are exercised by this feature's story.

## Constraints and Assumptions

Python/FastAPI, GraphQL/Relay and Batten are selected. Architecture and upstream
change inventory govern ownership. Exact target surfaces are specified in CONTRACT-001, CONTRACT-005.
The corresponding solution/story designs apply them. Framework/native/toolchain
compatibility still requires the named interoperability proofs.

## Dependencies

FR-1, FR-2; [architecture](../../02-design/architecture.md);
[upstream changes](../../02-design/upstream-changes.md).

## Out of Scope

REST/OpenAPI product API, a new data compiler, and broader unsupported backend profiles.
