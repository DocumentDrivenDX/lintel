---
ddx:
  id: TD-003
  type: technical-design
  activity: design
  authoring:
    home: repo
  links:
    - id: US-003
      kind: informed_by
    - id: SD-003
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
---

# TD-003-commands-outcomes: Declared commands and exact outcomes

**User Story**: [[US-003-commands-outcomes]] | **Feature**: [[FEAT-003]] | **Solution Design**: [[SD-003-commands-outcomes]]

## Scope

One vertical story slice, applying CONTRACT-002, CONTRACT-003. Source implementation is not supplied.
Existing upstream semantics and Batten's public boundary remain authoritative.

## Technical Approach

Derive command arguments from upstream metadata, preserve omission/null, dispatch through the host and expose authoritative uncertainty/recovery outcomes.

Use the qualified public seam rather than the rejected alternative in SD-003.
The tradeoff is explicit capability/spike work before dependent implementation.

## Component Changes

Affected owning modules: `src/lintel/graphql/`, `src/lintel/ports.py`. They are proposed paths in the Architecture map,
not existing implementation. Add minimal public exports from the Contracts;
keep concrete providers and framework types out of pure projection/ports.
Batten's adapter changes belong to Batten, not this repository.

Before dependent source, implement and negatively exercise the real project
boundary commands named in Architecture. The presence of this map is not a pass.

### Planned file ownership

| File / package | Story responsibility |
| --- | --- |
| `src/lintel/graphql/inputs.py` | Bridge framework omission sentinels into upstream presence; preserve explicit null and native default ownership. |
| `src/lintel/graphql/commands.py` | Dispatch declared command/control metadata separately; never retry or execute from an observation. |
| `src/lintel/graphql/outcomes.py` | Preserve receipt, durability, pending commit and unknown statuses; return IDs rather than mutable Node snapshots. |

These are proposed files, not source already created. Integration-specific
representations stay at the named boundary; no helper becomes a second UMF or SQL engine.

## API/Interface Design

CONTRACT-002, CONTRACT-003 owns shared signatures, schemas, controls, errors and compatibility.
This TD only applies those surfaces to US-003; no alternate API is introduced.

## Data Model Changes

Reuse current UMF 0.10 references and the task-board example. No Lintel-owned
business tables, RLS emitter or migration engine. Any needed native fixture/schema
changes are upstream and explicit, never a side effect of constructing the API.

A Strawberry implementation must explicitly preserve its unset sentinel at the
input adapter; using Python None as both omitted and null is a defect. Framework
sentinels stay inside graphql/inputs.py and never cross the neutral port.

## Security

Use trusted host context, exact admitted application/API identity, current
permission/confirmation and policy-filtered data. Protect internal keys/cursors,
never log variables/credentials, and keep caches/resources request-scoped.
Negative cases in STP-003 must fail through the real public boundary.

## Performance

Apply CONTRACT-005 finite limits; make cost/dispatch evidence observable rather
than infer it from mocks. No throughput/latency SLO is claimed for this unbuilt slice.

## Testing

[STP-003](../../03-test/test-plans/STP-003-commands-outcomes.md) allocates all four criteria:
- US-003-AC1: `mutation_respects_host_gates` at `tests/native/test_commands.py`; asserted behavior is owned by the STP.
- US-003-AC2: `lost_response_does_not_repeat_mutation` at `tests/native/test_commands.py`; asserted behavior is owned by the STP.
- US-003-AC3: `exact_values_and_presence_survive` at `tests/native/test_commands.py`; asserted behavior is owned by the STP.
- US-003-AC4: `mutation_fields_do_not_invent_atomicity` at `tests/graphql/test_commands.py`; asserted behavior is owned by the STP.

Tests must cite their exact `@covers US-003-AC<number>` IDs and exercise the
observable outcome. They do not exist yet. Installed/native/browser/deployed
claims require separate real-path results at the allocated primary layer.

## Migration & Rollback

No business-data migration is performed by Lintel. Replace the prepared app/cohort
through host admission and drain the old one. Code rollback does not reverse an
upstream data/schema change or a dispatched command. Preserve original keys,
receipts and explicit durability/uncertainty during recovery.

## Risks

An unqualified public runtime/compiler seam can invalidate an implementation
choice. Keep target behavior; update the public contract explicitly if the spike
shows it cannot be supported, rather than silently weaken an acceptance criterion.

## Diagnostic Wiring

The host owns authoritative audit and the OpenTelemetry sink. Carry safe request,
app/API/operation context and outcomes; do not record instance inputs. Plan real
receiver/privacy/cancellation evidence in the owning STP. No new diagnostic wire
schema or exporter dependency is selected here.

## Schema Basis

CONTRACT-002, CONTRACT-003 and their local authoritative schema/example sources define the selected
shapes. Upstream model/constraint/value semantics are reused; no semantic engine
is recreated in a Python wrapper or client build step.
