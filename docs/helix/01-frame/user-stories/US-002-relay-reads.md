---
ddx:
  id: US-002
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: FEAT-002
      kind: informed_by
---

# US-002: Page tasks and expand their assignees

**Feature**: [FEAT-002: Relay reads and identity](../features/FEAT-002-relay-reads.md)
**Feature Requirements**: READ-01, READ-02
**PRD Requirements**: FR-3, FR-4
**Priority**: P0

## Story

**As a** Batten application author, **I want** to page tasks and expand their assignees, **So that** I can reuse Relay refetch and connection behavior.

## Context

The selected requirement pair forms one end-to-end capability: relay reads and identity.
Its behavioral meaning remains owned by UMF, Batten and the execution runtime.
These criteria govern future implementation; they are not passed tests.

## Walkthrough

1. Compile the task list query and request Alice's first two visible tasks.
2. Resume after the first returned edge and inspect t-002/t-003 and exact PageInfo.
3. Expand assignees: p-1 is visible and shared; p-2 remains unavailable even from a visible task.
4. Refetch the same Node through fragments/aliases during a concurrent update and verify one request view.

## Acceptance Criteria

- [ ] **US-002-AC1** — Given authorized tasks with tied ordering values, when a compiled Relay operation continues after an interior edge, then the returned sequence has the declared stable order without duplicates or skipped authorized tasks.
- [ ] **US-002-AC2** — Given two apps and two principals with the same native keys, when nodes are refetched and stores reused under allowed transitions, then no cross-app or cross-principal data appears.
- [ ] **US-002-AC3** — Given fifty tasks sharing assignees, when one-hop relationships are selected, then native read count is bounded by relationship batches rather than parent count.
- [ ] **US-002-AC4** — Given the same Node appears twice during concurrent native changes, when one operation resolves it, then shared selected fields satisfy the declared request consistency profile.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

[STP-002](../../03-test/test-plans/STP-002-relay-reads.md) owns the detailed
AC/test/assertion/citation mapping. Concrete fabricated inputs are in the
[task-board cases](../../02-design/examples/task-board.cases.json).
All product tests remain planned, absent and unrun.

## Dependencies

FEAT-002; READ-01, READ-02; FR-3, FR-4; upstream changes and architecture.
Target surfaces are governed by CONTRACT-002, CONTRACT-003;
[TD-002](../../02-design/technical-designs/TD-002-relay-reads.md) applies them.
Upstream compatibility, real boundary checks and native/browser proof remain
required; specification detail does not claim delivered support.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
