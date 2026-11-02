---
ddx:
  id: FEAT-005
  type: feature-specification
  activity: frame
  authoring:
    home: repo
  links:
    - id: lintel.prd
      kind: informed_by
---

# FEAT-005: Batten embedding and lifecycle

**Feature ID**: FEAT-005
**Priority**: P0
**Owner**: Lintel maintainers; named implementation assignee unassigned
**Covered PRD Subsystem(s)**: Batten embedding
**Covered PRD Requirements**: FR-9, FR-10
**Cross-Subsystem Rationale**: None — single subsystem.

## Overview

Batten embedding and lifecycle lets the batten platform maintainer include Lintel in the supplied runtime. It realizes FR-9, FR-10
within the selected GraphQL/Relay and Batten profile.

## Ideal Future State

The author can include Lintel in the supplied runtime and give applications one admitted API without per-app infrastructure wiring. Every supported behavior
has explicit schema/runtime capability and observed consumer evidence.

## Problem Statement

Current upstream model and runtime foundations do not establish this Lintel
capability. The outcome is one coherent supported path rather than per-app glue.

## Requirements

### Functional Requirements by Area

The implementation must satisfy each requirement below.

**HOST-01** — Integrate through public async Batten composition, actor/authority, confirmation and attribution boundaries.
**HOST-02** — Respect owned/borrowed resources, scoped bounds, cancellation and startup readiness without installing dependencies or applying data schemas.

### Non-Functional Requirements

Zero silent semantic coercions or cross-context authority leaks in the scoped
corpus. Mandatory finite host bounds. No passing implementation evidence is claimed.

## User Stories

- [US-005: Include lintel in the supplied runtime](../user-stories/US-005-batten-embedding.md).

## Edge Cases and Error Handling

Unsupported selected meaning, foreign identities, changed sources and capability
mismatch refuse explicitly. Unknown mutation commitment is preserved for recovery.
Only applicable cases are exercised by this feature's story.

## Constraints and Assumptions

Python/FastAPI, GraphQL/Relay and Batten are selected. Architecture and upstream
change inventory govern ownership. Exact interface details require contracts
following their named spikes; this feature does not freeze those signatures.

## Dependencies

FR-9, FR-10; [architecture](../../02-design/architecture.md);
[upstream changes](../../02-design/upstream-changes.md).

## Out of Scope

REST/OpenAPI product API, a new data compiler, and broader unsupported backend profiles.
