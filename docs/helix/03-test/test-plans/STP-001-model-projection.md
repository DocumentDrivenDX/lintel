---
ddx:
  id: STP-001
  type: story-test-plan
  activity: test
  authoring:
    home: repo
  links:
    - id: US-001
      kind: informed_by
    - id: TD-001
      kind: informed_by
    - id: TP-001
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
    - id: CONTRACT-005
      kind: informed_by
---

# STP-001-model-projection: Model admission and API projection

## Story Reference

**User Story**: [[US-001-model-projection]]
**Technical Design**: [[TD-001-model-projection]]
**Related Solution Design**: [[SD-001-model-projection]]
**Project Test Plan**: [TP-001](../test-plan.md)

## Scope and Objective

Prove the four existing US-001 criteria at their primary allocated boundaries.
Exact shared behavior is CONTRACT-001, CONTRACT-005. Out of scope: adjacent stories, wider backends,
REST/OpenAPI and unsupported graph/temporal semantics.

## Acceptance Criteria Test Mapping

Every row is planned, absent and unrun. A name/citation in this document is not
coverage. Product tests must implement the named assertion and include the literal
citation. A public-boundary fake never establishes native execution.

| AC ID | Acceptance Criterion | Test | Asserted Behavior | Citation | Primary Layer | File | Setup | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-001-AC1 | [Story criterion](../../01-frame/user-stories/US-001-model-projection.md) | `test_schema_is_deterministic` (new, planned) | the exported schema and semantic projection identity agree | `@covers US-001-AC1` (required, not yet present) | Contract | `tests/model_projection/test_model_projection.py` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-001-AC2 | [Story criterion](../../01-frame/user-stories/US-001-model-projection.md) | `test_unknown_selected_meaning_refuses` (new, planned) | activation refuses without discarding the extension | `@covers US-001-AC2` (required, not yet present) | Contract | `tests/model_projection/test_model_projection.py` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-001-AC3 | [Story criterion](../../01-frame/user-stories/US-001-model-projection.md) | `test_dependency_type_grants_no_access` (new, planned) | the dependency acquires no query capability | `@covers US-001-AC3` (required, not yet present) | Integration | `tests/model_projection/test_model_projection.py` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-001-AC4 | [Story criterion](../../01-frame/user-stories/US-001-model-projection.md) | `test_relay_name_collision_is_explicit` (new, planned) | a deterministic explicit mapping or collision diagnostic preserves both meanings | `@covers US-001-AC4` (required, not yet present) | Contract | `tests/model_projection/test_model_projection.py` | Task-board cases and controlled failure/concurrency history | Unrun |

## Executable Proof

Planned primary command: `uv run pytest tests/model_projection`. Also run each listed build/browser/packaging
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
