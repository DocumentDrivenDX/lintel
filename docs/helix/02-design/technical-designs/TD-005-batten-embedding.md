---
ddx:
  id: TD-005
  type: technical-design
  activity: design
  authoring:
    home: repo
  links:
    - id: US-005
      kind: informed_by
    - id: SD-005
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-005
      kind: informed_by
---

# TD-005-batten-embedding: Batten embedding and lifecycle

**User Story**: [[US-005-batten-embedding]] | **Feature**: [[FEAT-005]] | **Solution Design**: [[SD-005-batten-embedding]]

## Scope

One vertical story slice, applying CONTRACT-002, CONTRACT-005. Source implementation is not supplied.
Existing upstream semantics and Batten's public boundary remain authoritative.

## Technical Approach

Supply neutral Python protocols and pure router factories; Batten owns its optional adapter and embedding composition owns trusted context and borrowed resources.

Use the qualified public seam rather than the rejected alternative in SD-005.
The tradeoff is explicit capability/spike work before dependent implementation.

## Component Changes

Affected owning modules: `src/lintel/ports.py`, `src/lintel/asgi/`, `src/lintel/hosting/`. They are proposed paths in the Architecture map,
not existing implementation. Add minimal public exports from the Contracts;
keep concrete providers and framework types out of pure projection/ports.
Batten's adapter changes belong to Batten, not this repository.

Before dependent source, implement and negatively exercise the real project
boundary commands named in Architecture. The presence of this map is not a pass.

### Planned file ownership

| File / package | Story responsibility |
| --- | --- |
| `src/lintel/asgi/router.py` | Mount only the prepared schema and supplied execution boundary. |
| `src/lintel/asgi/context.py` | Resolve trusted host scope and refuse app/API/codec mismatch before data access. |
| `src/lintel/hosting/lifecycle.py` | Seal/drain request admission and invoke only explicit owned closers. |
| `src/lintel/hosting/settings.py` | Resolve typed file settings once; no implicit environment reads. |

These are proposed files, not source already created. Integration-specific
representations stay at the named boundary; no helper becomes a second UMF or SQL engine.

## API/Interface Design

CONTRACT-002, CONTRACT-005 owns shared signatures, schemas, controls, errors and compatibility.
This TD only applies those surfaces to US-005; no alternate API is introduced.

## Data Model Changes

Reuse current UMF 0.10 references and the task-board example. No Lintel-owned
business tables, RLS emitter or migration engine. Any needed native fixture/schema
changes are upstream and explicit, never a side effect of constructing the API.

## Security

Use trusted host context, exact admitted application/API identity, current
permission/confirmation and policy-filtered data. Protect internal keys/cursors,
never log variables/credentials, and keep caches/resources request-scoped.
Negative cases in STP-005 must fail through the real public boundary.

## Performance

Apply CONTRACT-005 finite limits; make cost/dispatch evidence observable rather
than infer it from mocks. No throughput/latency SLO is claimed for this unbuilt slice.

## Testing

[STP-005](../../03-test/test-plans/STP-005-batten-embedding.md) allocates all four criteria:
- US-005-AC1: `batten_admission_is_not_bypassed` at `tests/hosting/test_batten_embedding.py`; asserted behavior is owned by the STP.
- US-005-AC2: `shutdown_preserves_borrowed_provider` at `tests/hosting/test_batten_embedding.py`; asserted behavior is owned by the STP.
- US-005-AC3: `startup_is_effect_free_and_fails_closed` at `tests/installed/test_embedding.py`; asserted behavior is owned by the STP.
- US-005-AC4: `cancellation_preserves_custody_and_outcome` at `tests/native/test_lifecycle.py`; asserted behavior is owned by the STP.

Tests must cite their exact `@covers US-005-AC<number>` IDs and exercise the
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

CONTRACT-002, CONTRACT-005 and their local authoritative schema/example sources define the selected
shapes. Upstream model/constraint/value semantics are reused; no semantic engine
is recreated in a Python wrapper or client build step.
