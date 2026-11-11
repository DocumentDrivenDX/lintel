---
ddx:
  id: US-003
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: FEAT-003
      kind: informed_by
---

# US-003: Invoke a declared task command

**Feature**: [FEAT-003: Declared commands and exact outcomes](../features/FEAT-003-commands-outcomes.md)
**Feature Requirements**: CMD-01, CMD-02
**PRD Requirements**: FR-5, FR-6
**Priority**: P0

## Story

**As a** Batten application author, **I want** to invoke a declared task command, **So that** I can preserve host authorization and recover uncertain effects.

## Context

The selected requirement pair forms one end-to-end capability: declared commands and exact outcomes.
Its behavioral meaning remains owned by UMF, Batten and the execution runtime.
These criteria govern future implementation; they are not passed tests.

## Walkthrough

1. Retain a new invocation key and the exact task/note arguments before completing t-001.
2. Pass the current host permission and any required confirmation; unauthorized attempts produce no effect.
3. Lose a response after native commit and use the observation query with the original inputs/key.
4. Recover the effect receipt and refetch current status; a second field failure never rewrites the first field's commit fact.

## Acceptance Criteria

- [ ] **US-003-AC1** — Given an actor without command permission or required confirmation, when a mutation is submitted, then no business effect occurs and the refusal is safe and attributable.
- [ ] **US-003-AC2** — Given a committed command whose response is lost, when the client observes its retained invocation identity, then the authoritative outcome is recovered without another effect.
- [ ] **US-003-AC3** — Given a decimal beyond binary64 precision and absent/null inputs, when a mutation crosses GraphQL and native execution, then exact values and distinct input presence survive or an unsupported meaning refuses.
- [ ] **US-003-AC4** — Given multiple top-level mutation fields and a later failure, when the operation runs, then outcomes retain per-command commit facts without asserting operation-wide atomicity.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

STP-003 owns the detailed
AC/test/assertion/citation mapping. Concrete fabricated inputs are in the
[task-board cases](../../02-design/examples/task-board.cases.json).
All product tests remain planned, absent and unrun.

## Dependencies

FEAT-003; CMD-01, CMD-02; FR-5, FR-6; upstream changes and architecture.
Target surfaces are governed by CONTRACT-002, CONTRACT-003;
[TD-003](../../02-design/technical-designs/TD-003-commands-outcomes.md) applies them.
Upstream compatibility, real boundary checks and native/browser proof remain
required; specification detail does not claim delivered support.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
