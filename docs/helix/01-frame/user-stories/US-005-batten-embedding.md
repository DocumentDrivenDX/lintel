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

1. The Batten composition root prepares public providers and constructs Batten's optional Lintel adapter.
2. Supply its neutral execution port, Node codec and trusted asynchronous context resolver to Lintel.
3. Mount the router and invoke through the public host gates under two applications.
4. Cancel requests and close one binding; scoped leases return while the other app's borrowed provider remains usable.

## Acceptance Criteria

- [ ] **US-005-AC1** — Given two admitted Batten applications, when Lintel is mounted and calls are dispatched, then only declared app capabilities execute with current actor attribution.
- [ ] **US-005-AC2** — Given a borrowed provider used by another application, when one Lintel binding closes, then the borrowed provider and other app remain usable.
- [ ] **US-005-AC3** — Given an unsupported runtime capability or installed-cohort mismatch, when the API starts, then readiness refuses with no schema migration or package download.
- [ ] **US-005-AC4** — Given a canceled read and a dispatched canceled mutation, when the host cancels requests, then resources return and the mutation retains possible-commit semantics.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

STP-005 owns the detailed
AC/test/assertion/citation mapping. Concrete fabricated inputs are in the
[task-board cases](../../02-design/examples/task-board.cases.json).
All product tests remain planned, absent and unrun.

## Dependencies

FEAT-005; HOST-01, HOST-02; FR-9, FR-10; upstream changes and architecture.
Target surfaces are governed by CONTRACT-002, CONTRACT-005;
[TD-005](../../02-design/technical-designs/TD-005-batten-embedding.md) applies them.
Upstream compatibility, real boundary checks and native/browser proof remain
required; specification detail does not claim delivered support.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
