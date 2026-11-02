---
ddx:
  id: STP-003
  type: story-test-plan
  activity: test
  authoring:
    home: repo
  links:
    - id: US-003
      kind: informed_by
    - id: TD-003
      kind: informed_by
    - id: TP-001
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
---

# STP-003-commands-outcomes: Declared commands and exact outcomes

## Story Reference

**User Story**: [[US-003-commands-outcomes]]
**Technical Design**: [[TD-003-commands-outcomes]]
**Related Solution Design**: [[SD-003-commands-outcomes]]
**Project Test Plan**: [TP-001](../test-plan.md)

## Scope and Objective

Prove the four existing US-003 criteria at their primary allocated boundaries.
Exact shared behavior is CONTRACT-002, CONTRACT-003. Out of scope: adjacent stories, wider backends,
REST/OpenAPI and unsupported graph/temporal semantics.

## Acceptance Criteria Test Mapping

Every row is planned, absent and unrun. A name/citation in this document is not
coverage. Product tests must implement the named assertion and include the literal
citation. A public-boundary fake never establishes native execution.

| AC ID | Acceptance Criterion | Test | Asserted Behavior | Citation | Primary Layer | File | Setup | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-003-AC1 | [Story criterion](../../01-frame/user-stories/US-003-commands-outcomes.md) | `test_mutation_respects_host_gates` (new, planned) | no business effect occurs and the refusal is safe and attributable | `@covers US-003-AC1` (required, not yet present) | Native E2E | `tests/native/test_commands.py` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-003-AC2 | [Story criterion](../../01-frame/user-stories/US-003-commands-outcomes.md) | `test_lost_response_does_not_repeat_mutation` (new, planned) | the authoritative outcome is recovered without another effect | `@covers US-003-AC2` (required, not yet present) | Native E2E | `tests/native/test_commands.py` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-003-AC3 | [Story criterion](../../01-frame/user-stories/US-003-commands-outcomes.md) | `test_exact_values_and_presence_survive` (new, planned) | exact values and distinct input presence survive or an unsupported meaning refuses | `@covers US-003-AC3` (required, not yet present) | Native E2E | `tests/native/test_commands.py` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-003-AC4 | [Story criterion](../../01-frame/user-stories/US-003-commands-outcomes.md) | `test_mutation_fields_do_not_invent_atomicity` (new, planned) | outcomes retain per-command commit facts without asserting operation-wide atomicity | `@covers US-003-AC4` (required, not yet present) | Integration | `tests/graphql/test_commands.py` | Task-board cases and controlled failure/concurrency history | Unrun |

## Executable Proof

Planned primary command: `uv run pytest tests/native`. Also run each listed build/browser/packaging
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
