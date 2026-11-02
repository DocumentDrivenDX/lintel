---
ddx:
  id: STP-002
  type: story-test-plan
  activity: test
  authoring:
    home: repo
  links:
    - id: US-002
      kind: informed_by
    - id: TD-002
      kind: informed_by
    - id: TP-001
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
---

# STP-002-relay-reads: Relay reads and identity

## Story Reference

**User Story**: [[US-002-relay-reads]]
**Technical Design**: [[TD-002-relay-reads]]
**Related Solution Design**: [[SD-002-relay-reads]]
**Project Test Plan**: [TP-001](../test-plan.md)

## Scope and Objective

Prove the four existing US-002 criteria at their primary allocated boundaries.
Exact shared behavior is CONTRACT-002, CONTRACT-003. Out of scope: adjacent stories, wider backends,
REST/OpenAPI and unsupported graph/temporal semantics.

## Acceptance Criteria Test Mapping

Every row is planned, absent and unrun. A name/citation in this document is not
coverage. Product tests must implement the named assertion and include the literal
citation. A public-boundary fake never establishes native execution.

| AC ID | Acceptance Criterion | Test | Asserted Behavior | Citation | Primary Layer | File | Setup | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-002-AC1 | [Story criterion](../../01-frame/user-stories/US-002-relay-reads.md) | `test_connection_resumes_from_any_edge` (new, planned) | the returned sequence has the declared stable order without duplicates or skipped authorized tasks | `@covers US-002-AC1` (required, not yet present) | Native E2E | `tests/native/test_relay_reads.py` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-002-AC2 | [Story criterion](../../01-frame/user-stories/US-002-relay-reads.md) | `node_and_store_scopes_are_isolated` (new, planned) | no cross-app or cross-principal data appears | `@covers US-002-AC2` (required, not yet present) | Browser E2E | `tests/client/isolation.spec.ts` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-002-AC3 | [Story criterion](../../01-frame/user-stories/US-002-relay-reads.md) | `test_relationships_are_batched` (new, planned) | native read count is bounded by relationship batches rather than parent count | `@covers US-002-AC3` (required, not yet present) | Native integration | `tests/native/test_relay_reads.py` | Task-board cases and controlled failure/concurrency history | Unrun |
| US-002-AC4 | [Story criterion](../../01-frame/user-stories/US-002-relay-reads.md) | `test_node_fields_are_stable_within_request` (new, planned) | shared selected fields satisfy the declared request consistency profile | `@covers US-002-AC4` (required, not yet present) | Native integration | `tests/native/test_relay_reads.py` | Task-board cases and controlled failure/concurrency history | Unrun |

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
