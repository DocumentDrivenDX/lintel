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

1. Build the platform server/client cohort with exact versions and source/artifact inventories.
2. Admit the fabricated app with package-registry access disabled and start local ASGI without installation.
3. Check the separate Databricks packaging profile without claiming unexecuted workspace behavior.
4. Publish checked family/source links and support limits; mismatched schema/client/runtime artifacts refuse admission.

## Acceptance Criteria

- [ ] **US-006-AC1** — Given the built Batten cohort and network-disabled app admission, when a fabricated app starts and builds its supplied client, then no application dependency installation or undeclared provider occurs.
- [ ] **US-006-AC2** — Given the Databricks Apps deployment configuration, when the host packaging smoke check runs, then framework/interpreter/dependency and actor mapping requirements are explicit; unqualified workspace execution remains labeled.
- [ ] **US-006-AC3** — Given the proposed Lintel family entry and documentation, when publication checks run, then links, parent family, intended status and qualified claims agree without invented live deployment.
- [ ] **US-006-AC4** — Given exported schema/client manifests from different cohorts, when the consumer admission/build check runs, then the mismatch refuses before affected effects.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

STP-006 owns the detailed
AC/test/assertion/citation mapping. Concrete fabricated inputs are in the
[task-board cases](../../02-design/examples/task-board.cases.json).
All product tests remain planned, absent and unrun.

## Dependencies

FEAT-006; DELIV-01, DELIV-02; FR-11, FR-12; upstream changes and architecture.
Target surfaces are governed by CONTRACT-004, CONTRACT-005;
[TD-006](../../02-design/technical-designs/TD-006-delivery-family.md) applies them.
Upstream compatibility, real boundary checks and native/browser proof remain
required; specification detail does not claim delivered support.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
