---
ddx:
  id: FEAT-003
  type: feature-specification
  activity: frame
  authoring:
    home: repo
  links:
    - id: lintel.prd
      kind: informed_by
---

# FEAT-003: Declared commands and exact outcomes

**Feature ID**: FEAT-003
**Priority**: P0
**Owner**: Lintel maintainers; named implementation assignee unassigned
**Covered PRD Subsystem(s)**: Commands and outcomes
**Covered PRD Requirements**: FR-5, FR-6
**Cross-Subsystem Rationale**: None — single subsystem.

## Overview

Declared commands and exact outcomes lets the batten application author invoke a declared task command. It realizes FR-5, FR-6
within the selected GraphQL/Relay and Batten profile.

## Ideal Future State

The author can invoke a declared task command and preserve host authorization and recover uncertain effects. Every supported behavior
has explicit schema/runtime capability and observed consumer evidence.

## Problem Statement

Current upstream model and runtime foundations do not establish this Lintel
capability. The outcome is one coherent supported path rather than per-app glue.

## Requirements

### Functional Requirements by Area

The implementation must satisfy each requirement below.

**CMD-01** — Route every mutation through the declared Batten host command with current authority, required confirmation and attribution.
**CMD-02** — Preserve exact inputs/results, business failures and authoritative applied/recovered/unknown outcomes without automatic retries.

### Non-Functional Requirements

Zero silent semantic coercions or cross-context authority leaks in the scoped
corpus. Mandatory finite host bounds. No passing implementation evidence is claimed.

## User Stories

- [US-003: Invoke a declared task command](../user-stories/US-003-commands-outcomes.md).

## Edge Cases and Error Handling

Unsupported selected meaning, foreign identities, changed sources and capability
mismatch refuse explicitly. Unknown mutation commitment is preserved for recovery.
Only applicable cases are exercised by this feature's story.

## Constraints and Assumptions

Python/FastAPI, GraphQL/Relay and Batten are selected. Architecture and upstream
change inventory govern ownership. Exact interface details require contracts
following their named spikes; this feature does not freeze those signatures.

## Dependencies

FR-5, FR-6; [architecture](../../02-design/architecture.md);
[upstream changes](../../02-design/upstream-changes.md).

## Out of Scope

REST/OpenAPI product API, a new data compiler, and broader unsupported backend profiles.
