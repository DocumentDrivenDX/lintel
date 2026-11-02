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

1. The author or maintainer supplies the approved task-board model and runtime context.
2. They page tasks and expand their assignees through the public application boundary.
3. The system checks declared meaning, capabilities and authority.
4. The user obtains the expected result or an explicit unsupported/refusal outcome.

## Acceptance Criteria

- [ ] **US-002-AC1** — Given authorized tasks with tied ordering values, when a compiled Relay operation continues after an interior edge, then the returned sequence has the declared stable order without duplicates or skipped authorized tasks.
- [ ] **US-002-AC2** — Given two apps and two principals with the same native keys, when nodes are refetched and stores reused under allowed transitions, then no cross-app or cross-principal data appears.
- [ ] **US-002-AC3** — Given fifty tasks sharing assignees, when one-hop relationships are selected, then native read count is bounded by relationship batches rather than parent count.
- [ ] **US-002-AC4** — Given the same Node appears twice during concurrent native changes, when one operation resolves it, then shared selected fields satisfy the declared request consistency profile.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

All tests below are planned, absent and unrun. The case preconditions above are
concrete fixture requirements. Add the listed citation to each exercising test.
Story Test Plans and exact protocol contracts precede implementation handoff.

| AC ID | Planned Test | Primary Layer | Asserted Behavior | Required Citation |
| --- | --- | --- | --- | --- |
| US-002-AC1 | `connection_resumes_from_any_edge` | Native E2E | the returned sequence has the declared stable order without duplicates or skipped authorized tasks | Planned `@covers US-002-AC1` |
| US-002-AC2 | `node_and_store_scopes_are_isolated` | Browser E2E | no cross-app or cross-principal data appears | Planned `@covers US-002-AC2` |
| US-002-AC3 | `relationships_are_batched` | Native integration | native read count is bounded by relationship batches rather than parent count | Planned `@covers US-002-AC3` |
| US-002-AC4 | `node_fields_are_stable_within_request` | Native integration | shared selected fields satisfy the declared request consistency profile | Planned `@covers US-002-AC4` |

Proposed test module: `tests/relay_reads/test_relay_reads.py`;
client/browser build tests may live in `tests/client/` instead. The test owner
must choose one primary executable assertion location and avoid duplicate suites.

## Dependencies

FEAT-002; READ-01, READ-02; FR-3, FR-4; upstream changes and architecture.
Exact GraphQL, exposure, host and client contract work is explicitly pending;
no absent Contract or Technical Design is represented as an implemented interface.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
