---
ddx:
  id: US-001
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: FEAT-001
      kind: informed_by
---

# US-001: Expose a selected umf model

**Feature**: [FEAT-001: Model admission and API projection](../features/FEAT-001-model-projection.md)
**Feature Requirements**: PROJ-01, PROJ-02
**PRD Requirements**: FR-1, FR-2
**Priority**: P0

## Story

**As a** Batten application author, **I want** to expose a selected UMF model, **So that** I can avoid separate handwritten GraphQL types.

## Context

The selected requirement pair forms one end-to-end capability: model admission and api projection.
Its behavioral meaning remains owned by UMF, Batten and the execution runtime.
These criteria govern future implementation; they are not passed tests.

## Walkthrough

1. Supply the approved task-board logical source, exact source/dependency closure and execution capability profile and explicit exposure.
2. Prepare the API and inspect the sorted SDL, identity digests and safe diagnostics.
3. Repeat preparation with identical bytes, then select an unknown constraint or a colliding Relay name.
4. Receive byte-identical output or a non-mutating preparation refusal; no dependency record gains an implicit list.

## Acceptance Criteria

- [ ] **US-001-AC1** — Given an approved two-record task board, when the API is constructed twice, then the exported schema and semantic projection identity agree.
- [ ] **US-001-AC2** — Given a selected unknown policy extension, when the app is prepared, then activation refuses without discarding the extension.
- [ ] **US-001-AC3** — Given a dependency record whose query is not exposed, when its key type is needed, then the dependency acquires no query capability.
- [ ] **US-001-AC4** — Given native fields that collide with Relay identity names, when projection is requested, then a deterministic explicit mapping or collision diagnostic preserves both meanings.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

STP-001 owns the detailed
AC/test/assertion/citation mapping. Concrete fabricated inputs are in the
[task-board cases](../../02-design/examples/task-board.cases.json).
All product tests remain planned, absent and unrun.

## Dependencies

FEAT-001; PROJ-01, PROJ-02; FR-1, FR-2; upstream changes and architecture.
Target surfaces are governed by CONTRACT-001, CONTRACT-005;
[TD-001](../../02-design/technical-designs/TD-001-model-projection.md) applies them.
Upstream compatibility, real boundary checks and native/browser proof remain
required; specification detail does not claim delivered support.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
