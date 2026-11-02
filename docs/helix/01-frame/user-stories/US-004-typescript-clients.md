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

1. The author or maintainer supplies the approved task-board model and runtime context.
2. They compile and run TypeScript operations and fragments through the public application boundary.
3. The system checks declared meaning, capabilities and authority.
4. The user obtains the expected result or an explicit unsupported/refusal outcome.

## Acceptance Criteria

- [ ] **US-004-AC1** — Given the exported schema and a refetchable paginated task fragment, when the client build runs, then Relay emits valid TypeScript operation/fragment artifacts that typecheck.
- [ ] **US-004-AC2** — Given a referenced field removed from the schema, when build/check runs, then the stale operation fails without rewriting approved artifacts.
- [ ] **US-004-AC3** — Given a built client and live Batten endpoint, when a browser pages and refetches a node then mutates, then the actual results update the intended normalized records.
- [ ] **US-004-AC4** — Given exact scalar carriers and a principal change, when the browser reads values and switches context, then values remain exact and prior actor data is unavailable.

## Edge Cases

Changed source, unknown selected meaning, missing authority and finite-limit
exhaustion fail explicitly. The command path preserves possible commitment.

## Test Scenarios

All tests below are planned, absent and unrun. The case preconditions above are
concrete fixture requirements. Add the listed citation to each exercising test.
Story Test Plans and exact protocol contracts precede implementation handoff.

| AC ID | Planned Test | Primary Layer | Asserted Behavior | Required Citation |
| --- | --- | --- | --- | --- |
| US-004-AC1 | `relay_artifacts_compile` | Build integration | Relay emits valid TypeScript operation/fragment artifacts that typecheck | Planned `@covers US-004-AC1` |
| US-004-AC2 | `client_drift_refuses` | Build integration | the stale operation fails without rewriting approved artifacts | Planned `@covers US-004-AC2` |
| US-004-AC3 | `browser_uses_generated_relay_artifacts` | Browser E2E | the actual results update the intended normalized records | Planned `@covers US-004-AC3` |
| US-004-AC4 | `client_scalars_and_actor_transition_are_safe` | Browser E2E | values remain exact and prior actor data is unavailable | Planned `@covers US-004-AC4` |

Proposed test module: `tests/typescript_clients/test_typescript_clients.py`;
client/browser build tests may live in `tests/client/` instead. The test owner
must choose one primary executable assertion location and avoid duplicate suites.

## Dependencies

FEAT-004; CLIENT-01, CLIENT-02; FR-7, FR-8; upstream changes and architecture.
Exact GraphQL, exposure, host and client contract work is explicitly pending;
no absent Contract or Technical Design is represented as an implemented interface.

## Out of Scope

Adjacent stories' behaviors, REST/OpenAPI and unqualified backend expansion.
