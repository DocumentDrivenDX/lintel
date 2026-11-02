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

1. The author or maintainer supplies the approved task-board model and runtime context.
2. They expose a selected UMF model through the public application boundary.
3. The system checks declared meaning, capabilities and authority.
4. The user obtains the expected result or an explicit unsupported/refusal outcome.

## Acceptance Criteria

- [ ] **US-001-AC1** — Given an approved two-record task board, when the API is constructed twice, then the exported schema and semantic projection identity agree.
- [ ] **US-001-AC2** — Given a selected unknown policy extension, when the app is prepared, then activation refuses without discarding the extension.
- [ ] **US-001-AC3** — Given a dependency record whose query is not exposed, when its key type is needed, then the dependency acquires no query capability.
- [ ] **US-001-AC4** — Given native fields that collide with Relay identity names, when projection is requested, then a deterministic explicit mapping or collision diagnostic preserves both meanings.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

All tests below are planned, absent and unrun. The case preconditions above are
concrete fixture requirements. Add the listed citation to each exercising test.
Story Test Plans and exact protocol contracts precede implementation handoff.

| AC ID | Planned Test | Primary Layer | Asserted Behavior | Required Citation |
| --- | --- | --- | --- | --- |
| US-001-AC1 | `schema_is_deterministic` | Contract | the exported schema and semantic projection identity agree | Planned `@covers US-001-AC1` |
| US-001-AC2 | `unknown_selected_meaning_refuses` | Contract | activation refuses without discarding the extension | Planned `@covers US-001-AC2` |
| US-001-AC3 | `dependency_type_grants_no_access` | Integration | the dependency acquires no query capability | Planned `@covers US-001-AC3` |
| US-001-AC4 | `relay_name_collision_is_explicit` | Contract | a deterministic explicit mapping or collision diagnostic preserves both meanings | Planned `@covers US-001-AC4` |

Proposed test module: `tests/model_projection/test_model_projection.py`;
client/browser build tests may live in `tests/client/` instead. The test owner
must choose one primary executable assertion location and avoid duplicate suites.

## Dependencies

FEAT-001; PROJ-01, PROJ-02; FR-1, FR-2; upstream changes and architecture.
Exact GraphQL, exposure, host and client contract work is explicitly pending;
no absent Contract or Technical Design is represented as an implemented interface.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
