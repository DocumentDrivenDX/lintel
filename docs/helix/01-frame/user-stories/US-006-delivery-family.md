---
ddx:
  id: US-006
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: FEAT-006
      kind: informed_by
---

# US-006: Distribute lintel with qualified documentation

**Feature**: [FEAT-006: Cohort delivery and family integration](../features/FEAT-006-delivery-family.md)
**Feature Requirements**: DELIV-01, DELIV-02
**PRD Requirements**: FR-11, FR-12
**Priority**: P0

## Story

**As a** Batten platform maintainer, **I want** to distribute Lintel with qualified documentation, **So that** I can adopt a reproducible platform component with visible support limits.

## Context

The selected requirement pair forms one end-to-end capability: cohort delivery and family integration.
Its behavioral meaning remains owned by UMF, Batten and the execution runtime.
These criteria govern future implementation; they are not passed tests.

## Walkthrough

1. The author or maintainer supplies the approved task-board model and runtime context.
2. They distribute Lintel with qualified documentation through the public application boundary.
3. The system checks declared meaning, capabilities and authority.
4. The user obtains the expected result or an explicit unsupported/refusal outcome.

## Acceptance Criteria

- [ ] **US-006-AC1** — Given the built Batten cohort and network-disabled app admission, when a fabricated app starts and builds its supplied client, then no application dependency installation or undeclared provider occurs.
- [ ] **US-006-AC2** — Given the Databricks Apps deployment configuration, when the host packaging smoke check runs, then framework/interpreter/dependency and actor mapping requirements are explicit; unqualified workspace execution remains labeled.
- [ ] **US-006-AC3** — Given the proposed Lintel family entry and documentation, when publication checks run, then links, parent family, intended status and qualified claims agree without invented live deployment.
- [ ] **US-006-AC4** — Given exported schema/client manifests from different cohorts, when the consumer admission/build check runs, then the mismatch refuses before affected effects.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

All tests below are planned, absent and unrun. The case preconditions above are
concrete fixture requirements. Add the listed citation to each exercising test.
Story Test Plans and exact protocol contracts precede implementation handoff.

| AC ID | Planned Test | Primary Layer | Asserted Behavior | Required Citation |
| --- | --- | --- | --- | --- |
| US-006-AC1 | `cohort_is_complete_offline` | Installed integration | no application dependency installation or undeclared provider occurs | Planned `@covers US-006-AC1` |
| US-006-AC2 | `databricks_profile_is_explicit` | Packaging integration | framework/interpreter/dependency and actor mapping requirements are explicit; unqualified workspace execution remains labeled | Planned `@covers US-006-AC2` |
| US-006-AC3 | `family_entry_and_claims_are_consistent` | Docs integration | links, parent family, intended status and qualified claims agree without invented live deployment | Planned `@covers US-006-AC3` |
| US-006-AC4 | `cohort_artifacts_cannot_be_mixed` | Installed integration | the mismatch refuses before affected effects | Planned `@covers US-006-AC4` |

Proposed test module: `tests/delivery_family/test_delivery_family.py`;
client/browser build tests may live in `tests/client/` instead. The test owner
must choose one primary executable assertion location and avoid duplicate suites.

## Dependencies

FEAT-006; DELIV-01, DELIV-02; FR-11, FR-12; upstream changes and architecture.
Exact GraphQL, exposure, host and client contract work is explicitly pending;
no absent Contract or Technical Design is represented as an implemented interface.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
