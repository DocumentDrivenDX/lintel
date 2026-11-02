---
ddx:
  id: US-004
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: FEAT-004
      kind: informed_by
---

# US-004: Compile and run typescript operations and fragments

**Feature**: [FEAT-004: TypeScript Relay client builds](../features/FEAT-004-typescript-clients.md)
**Feature Requirements**: CLIENT-01, CLIENT-02
**PRD Requirements**: FR-7, FR-8
**Priority**: P0

## Story

**As a** Batten application author, **I want** to compile and run TypeScript operations and fragments, **So that** I can use the exact API without duplicate handwritten types.

## Context

The selected requirement pair forms one end-to-end capability: typescript relay client builds.
Its behavioral meaning remains owned by UMF, Batten and the execution runtime.
These criteria govern future implementation; they are not passed tests.

## Walkthrough

1. Export the admitted SDL/api manifest and author the TaskRow fragment plus BoardQuery.
2. Build through the supplied Relay toolchain and typecheck its generated TypeScript artifacts.
3. Run the actual browser environment against Batten, page/refetch/complete and reconcile the result.
4. Remove a selected field or switch actor/app context; stale builds fail and old store data is unavailable.

## Acceptance Criteria

- [ ] **US-004-AC1** — Given the exported schema and a refetchable paginated task fragment, when the client build runs, then Relay emits valid TypeScript operation/fragment artifacts that typecheck.
- [ ] **US-004-AC2** — Given a referenced field removed from the schema, when build/check runs, then the stale operation fails without rewriting approved artifacts.
- [ ] **US-004-AC3** — Given a built client and live Batten endpoint, when a browser pages and refetches a node then mutates, then the actual results update the intended normalized records.
- [ ] **US-004-AC4** — Given exact scalar carriers and a principal change, when the browser reads values and switches context, then values remain exact and prior actor data is unavailable.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

[STP-004](../../03-test/test-plans/STP-004-typescript-clients.md) owns the detailed
AC/test/assertion/citation mapping. Concrete fabricated inputs are in the
[task-board cases](../../02-design/examples/task-board.cases.json).
All product tests remain planned, absent and unrun.

## Dependencies

FEAT-004; CLIENT-01, CLIENT-02; FR-7, FR-8; upstream changes and architecture.
Target surfaces are governed by CONTRACT-003, CONTRACT-004;
[TD-004](../../02-design/technical-designs/TD-004-typescript-clients.md) applies them.
Upstream compatibility, real boundary checks and native/browser proof remain
required; specification detail does not claim delivered support.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
