---
ddx:
  id: FEAT-002
  type: feature-specification
  activity: frame
  authoring:
    home: repo
  links:
    - id: lintel.prd
      kind: informed_by
---

# FEAT-002: Relay reads and identity

**Feature ID**: FEAT-002
**Priority**: P0
**Owner**: Lintel maintainers; named implementation assignee unassigned
**Covered PRD Subsystem(s)**: Relay reads and identity
**Covered PRD Requirements**: FR-3, FR-4
**Cross-Subsystem Rationale**: None — single subsystem.

## Overview

Relay reads and identity lets the batten application author page tasks and expand their assignees. It realizes FR-3, FR-4
within the selected GraphQL/Relay and Batten profile.

## Ideal Future State

The author can page tasks and expand their assignees and reuse Relay refetch and connection behavior. Every supported behavior
has explicit schema/runtime capability and observed consumer evidence.

## Problem Statement

Current upstream model and runtime foundations do not establish this Lintel
capability. The outcome is one coherent supported path rather than per-app glue.

## Requirements

### Functional Requirements by Area

The implementation must satisfy each requirement below.

**READ-01** — Offer stable authorized Node refetch and bounded forward connections with honest per-edge cursors and PageInfo.
**READ-02** — Resolve selected one-hop relationships using bounded request-local batching and explicit consistency; refuse unsupported traversal.

### Non-Functional Requirements

Zero silent semantic coercions or cross-context authority leaks in the scoped
corpus. Mandatory finite host bounds. No passing implementation evidence is claimed.

## Detailed Behavior

Collect qualified field selections, use a request-consistent session and batch related/key reads; map runtime positions into Relay connections without offset emulation.

Compile the task list query and request Alice's first two visible tasks. Resume after the first returned edge and inspect t-002/t-003 and exact PageInfo. Expand assignees: p-1 is visible and shared; p-2 remains unavailable even from a visible task. Refetch the same Node through fragments/aliases during a concurrent update and verify one request view.

See [SD-002](../../02-design/solution-designs/SD-002-relay-reads.md)
for the selected approach and business rules BR-3, BR-4.
Shared shapes and failure rules live in CONTRACT-002, CONTRACT-003.

## User Stories

- [US-002: Page tasks and expand their assignees](../user-stories/US-002-relay-reads.md).

## Edge Cases and Error Handling

Unsupported selected meaning, foreign identities, changed sources and capability
mismatch refuse explicitly. Unknown mutation commitment is preserved for recovery.
Only applicable cases are exercised by this feature's story.

## Constraints and Assumptions

Python/FastAPI, GraphQL/Relay and Batten are selected. Architecture and upstream
change inventory govern ownership. Exact target surfaces are specified in CONTRACT-002, CONTRACT-003.
The corresponding solution/story designs apply them. Framework/native/toolchain
compatibility still requires the named interoperability proofs.

## Dependencies

FR-3, FR-4; [architecture](../../02-design/architecture.md);
[upstream changes](../../02-design/upstream-changes.md).

## Out of Scope

REST/OpenAPI product API, a new data compiler, and broader unsupported backend profiles.
