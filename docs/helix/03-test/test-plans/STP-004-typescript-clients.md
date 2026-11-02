---
ddx:
  id: STP-004
  type: story-test-plan
  activity: test
  authoring:
    home: repo
  links:
    - id: US-004
      kind: informed_by
    - id: TD-004
      kind: informed_by
    - id: TP-001
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
    - id: CONTRACT-004
      kind: informed_by
---

# STP-004-typescript-clients: TypeScript Relay client builds

## Story Reference

**User Story**: [[US-004-typescript-clients]]
**Technical Design**: [[TD-004-typescript-clients]]
**Related Solution Design**: [[SD-004-typescript-clients]]
**Project Test Plan**: [TP-001](../test-plan.md)

## Scope and Objective

Prove the four existing US-004 criteria at their primary allocated boundaries.
Exact shared behavior is CONTRACT-003, CONTRACT-004. Out of scope: adjacent stories, wider backends,
REST/OpenAPI and unsupported graph/temporal semantics.

## Acceptance Criteria Test Mapping

Every row is planned, absent and unrun. A name/citation in this document is not
coverage. Product tests must implement the named assertion and include the literal
citation. A public-boundary fake never establishes native execution.

| AC ID | Acceptance Criterion | Test | Asserted Behavior | Citation | Primary Layer | File | Setup | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-004-AC1 | [Story criterion](../../01-frame/user-stories/US-004-typescript-clients.md) | `relay_artifacts_compile` (new, planned) | Relay emits valid TypeScript operation/fragment artifacts that typecheck | `@covers US-004-AC1` (required, not yet present) | Build integration | `tests/client/build.test.ts` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-004-AC2 | [Story criterion](../../01-frame/user-stories/US-004-typescript-clients.md) | `client_drift_refuses` (new, planned) | the stale operation fails without rewriting approved artifacts | `@covers US-004-AC2` (required, not yet present) | Build integration | `tests/client/build.test.ts` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-004-AC3 | [Story criterion](../../01-frame/user-stories/US-004-typescript-clients.md) | `browser_uses_generated_relay_artifacts` (new, planned) | the actual results update the intended normalized records | `@covers US-004-AC3` (required, not yet present) | Browser E2E | `tests/client/journey.spec.ts` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-004-AC4 | [Story criterion](../../01-frame/user-stories/US-004-typescript-clients.md) | `client_scalars_and_actor_transition_are_safe` (new, planned) | values remain exact and prior actor data is unavailable | `@covers US-004-AC4` (required, not yet present) | Browser E2E | `tests/client/isolation.spec.ts` | Task-board cases and controlled failure/concurrency history | Unrun |

## Executable Proof

Planned primary command: `bun run test:client`. Also run each listed build/browser/packaging
file at its allocated layer; a Python subset alone cannot qualify this story.
Scaffolding must make the actual commands available before implementation handoff.
Retain command, exact source/cohort, fixture/replay inputs and observed outcome
under `docs/helix/04-build/evidence/`. There is no passing product result yet.

## Data and Setup

Use [task-board cases](../../02-design/examples/task-board.cases.json) and the
[host obligations](../../02-design/examples/README.md). Alice sees t-001/2/3;
Bob sees t-004. The hidden p-2 target, tied titles, exact Decimal and tri-state
note support negative assertions. Generate the 50-parent matrix deterministically.
Native tests require explicit PostgreSQL 18 setup through the owning runtime;
installed tests build wheels; browser tests use compiled Relay and actual Chromium.

## Edge Cases and Failure Modes

Foreign identity/API/cursor, oversized requests, missing authority, native drift,
invalid scalar output, cancellation and lost-after-commit histories are controlled
inputs. Assert the applicable observable refusal/recovery, not private call order.
Do not claim a false empty page or a known rollback for an uncertain command.

## Build Handoff

Prerequisites: required interoperability spikes, exact upstream cohort, actual
boundary checks and the referenced shared contracts. Implement this story through
its TD and consolidate data variants into the fewest meaningful behavioral tests.
Done means all four criteria are exercised, cited and passing at the named primary
layers; documents, mocks and test names alone are insufficient.

## Diagnostic Proof

For the changed path, exercise host-injected diagnostic correlation, pre-sink
privacy and bounded cancellation/export failure with a real receiver where claimed.
Do not count a fake exporter or JSON parsing as an OpenTelemetry integration.
No GenAI/model telemetry is applicable to this API runtime.
