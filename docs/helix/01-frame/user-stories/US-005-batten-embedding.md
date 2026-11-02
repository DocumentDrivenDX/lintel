---
ddx:
  id: US-005
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: FEAT-005
      kind: informed_by
---

# US-005: Include lintel in the supplied runtime

**Feature**: [FEAT-005: Batten embedding and lifecycle](../features/FEAT-005-batten-embedding.md)
**Feature Requirements**: HOST-01, HOST-02
**PRD Requirements**: FR-9, FR-10
**Priority**: P0

## Story

**As a** Batten platform maintainer, **I want** to include Lintel in the supplied runtime, **So that** I can give applications one admitted API without per-app infrastructure wiring.

## Context

The selected requirement pair forms one end-to-end capability: batten embedding and lifecycle.
Its behavioral meaning remains owned by UMF, Batten and the execution runtime.
These criteria govern future implementation; they are not passed tests.

## Walkthrough

1. The author or maintainer supplies the approved task-board model and runtime context.
2. They include Lintel in the supplied runtime through the public application boundary.
3. The system checks declared meaning, capabilities and authority.
4. The user obtains the expected result or an explicit unsupported/refusal outcome.

## Acceptance Criteria

- [ ] **US-005-AC1** — Given two admitted Batten applications, when Lintel is mounted and calls are dispatched, then only declared app capabilities execute with current actor attribution.
- [ ] **US-005-AC2** — Given a borrowed provider used by another application, when one Lintel binding closes, then the borrowed provider and other app remain usable.
- [ ] **US-005-AC3** — Given an unsupported runtime capability or installed-cohort mismatch, when the API starts, then readiness refuses with no schema migration or package download.
- [ ] **US-005-AC4** — Given a canceled read and a dispatched canceled mutation, when the host cancels requests, then resources return and the mutation retains possible-commit semantics.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

All tests below are planned, absent and unrun. The case preconditions above are
concrete fixture requirements. Add the listed citation to each exercising test.
Story Test Plans and exact protocol contracts precede implementation handoff.

| AC ID | Planned Test | Primary Layer | Asserted Behavior | Required Citation |
| --- | --- | --- | --- | --- |
| US-005-AC1 | `batten_admission_is_not_bypassed` | Integration | only declared app capabilities execute with current actor attribution | Planned `@covers US-005-AC1` |
| US-005-AC2 | `shutdown_preserves_borrowed_provider` | Integration | the borrowed provider and other app remain usable | Planned `@covers US-005-AC2` |
| US-005-AC3 | `startup_is_effect_free_and_fails_closed` | Installed integration | readiness refuses with no schema migration or package download | Planned `@covers US-005-AC3` |
| US-005-AC4 | `cancellation_preserves_custody_and_outcome` | Native integration | resources return and the mutation retains possible-commit semantics | Planned `@covers US-005-AC4` |

Proposed test module: `tests/batten_embedding/test_batten_embedding.py`;
client/browser build tests may live in `tests/client/` instead. The test owner
must choose one primary executable assertion location and avoid duplicate suites.

## Dependencies

FEAT-005; HOST-01, HOST-02; FR-9, FR-10; upstream changes and architecture.
Exact GraphQL, exposure, host and client contract work is explicitly pending;
no absent Contract or Technical Design is represented as an implemented interface.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
