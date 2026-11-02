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

1. The author or maintainer supplies the approved task-board model and runtime context.
2. They invoke a declared task command through the public application boundary.
3. The system checks declared meaning, capabilities and authority.
4. The user obtains the expected result or an explicit unsupported/refusal outcome.

## Acceptance Criteria

- [ ] **US-003-AC1** — Given an actor without command permission or required confirmation, when a mutation is submitted, then no business effect occurs and the refusal is safe and attributable.
- [ ] **US-003-AC2** — Given a committed command whose response is lost, when the client observes its retained invocation identity, then the authoritative outcome is recovered without another effect.
- [ ] **US-003-AC3** — Given a decimal beyond binary64 precision and absent/null inputs, when a mutation crosses GraphQL and native execution, then exact values and distinct input presence survive or an unsupported meaning refuses.
- [ ] **US-003-AC4** — Given multiple top-level mutation fields and a later failure, when the operation runs, then outcomes retain per-command commit facts without asserting operation-wide atomicity.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

All tests below are planned, absent and unrun. The case preconditions above are
concrete fixture requirements. Add the listed citation to each exercising test.
Story Test Plans and exact protocol contracts precede implementation handoff.

| AC ID | Planned Test | Primary Layer | Asserted Behavior | Required Citation |
| --- | --- | --- | --- | --- |
| US-003-AC1 | `mutation_respects_host_gates` | Native E2E | no business effect occurs and the refusal is safe and attributable | Planned `@covers US-003-AC1` |
| US-003-AC2 | `lost_response_does_not_repeat_mutation` | Native E2E | the authoritative outcome is recovered without another effect | Planned `@covers US-003-AC2` |
| US-003-AC3 | `exact_values_and_presence_survive` | Native E2E | exact values and distinct input presence survive or an unsupported meaning refuses | Planned `@covers US-003-AC3` |
| US-003-AC4 | `mutation_fields_do_not_invent_atomicity` | Integration | outcomes retain per-command commit facts without asserting operation-wide atomicity | Planned `@covers US-003-AC4` |

Proposed test module: `tests/commands_outcomes/test_commands_outcomes.py`;
client/browser build tests may live in `tests/client/` instead. The test owner
must choose one primary executable assertion location and avoid duplicate suites.

## Dependencies

FEAT-003; CMD-01, CMD-02; FR-5, FR-6; upstream changes and architecture.
Exact GraphQL, exposure, host and client contract work is explicitly pending;
no absent Contract or Technical Design is represented as an implemented interface.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
