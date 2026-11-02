---
ddx:
  id: STP-005
  type: story-test-plan
  activity: test
  authoring:
    home: repo
  links:
    - id: US-005
      kind: informed_by
    - id: TD-005
      kind: informed_by
    - id: TP-001
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-005
      kind: informed_by
---

# STP-005-batten-embedding: Batten embedding and lifecycle

## Story Reference

**User Story**: [[US-005-batten-embedding]]
**Technical Design**: [[TD-005-batten-embedding]]
**Related Solution Design**: [[SD-005-batten-embedding]]
**Project Test Plan**: [TP-001](../test-plan.md)

## Scope and Objective

Prove the four existing US-005 criteria at their primary allocated boundaries.
Exact shared behavior is CONTRACT-002, CONTRACT-005. Out of scope: adjacent stories, wider backends,
REST/OpenAPI and unsupported graph/temporal semantics.

## Acceptance Criteria Test Mapping

Every row is planned, absent and unrun. A name/citation in this document is not
coverage. Product tests must implement the named assertion and include the literal
citation. A public-boundary fake never establishes native execution.

| AC ID | Acceptance Criterion | Test | Asserted Behavior | Citation | Primary Layer | File | Setup | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-005-AC1 | [Story criterion](../../01-frame/user-stories/US-005-batten-embedding.md) | `test_batten_admission_is_not_bypassed` (new, planned) | only declared app capabilities execute with current actor attribution | `@covers US-005-AC1` (required, not yet present) | Integration | `tests/hosting/test_batten_embedding.py` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-005-AC2 | [Story criterion](../../01-frame/user-stories/US-005-batten-embedding.md) | `test_shutdown_preserves_borrowed_provider` (new, planned) | the borrowed provider and other app remain usable | `@covers US-005-AC2` (required, not yet present) | Integration | `tests/hosting/test_batten_embedding.py` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-005-AC3 | [Story criterion](../../01-frame/user-stories/US-005-batten-embedding.md) | `test_startup_is_effect_free_and_fails_closed` (new, planned) | readiness refuses with no schema migration or package download | `@covers US-005-AC3` (required, not yet present) | Installed integration | `tests/installed/test_embedding.py` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-005-AC4 | [Story criterion](../../01-frame/user-stories/US-005-batten-embedding.md) | `test_cancellation_preserves_custody_and_outcome` (new, planned) | resources return and the mutation retains possible-commit semantics | `@covers US-005-AC4` (required, not yet present) | Native integration | `tests/native/test_lifecycle.py` | Task-board cases and controlled failure/concurrency history | Unrun |

## Executable Proof

Planned primary command: `uv run pytest tests/hosting`. Also run each listed build/browser/packaging
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
