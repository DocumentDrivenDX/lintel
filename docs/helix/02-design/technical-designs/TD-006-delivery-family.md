---
ddx:
  id: TD-006
  type: technical-design
  activity: design
  authoring:
    home: repo
  links:
    - id: US-006
      kind: informed_by
    - id: SD-006
      kind: informed_by
    - id: CONTRACT-004
      kind: informed_by
    - id: CONTRACT-005
      kind: informed_by
---

# TD-006-delivery-family: Cohort delivery and family integration

**User Story**: [[US-006-delivery-family]] | **Feature**: [[FEAT-006]] | **Solution Design**: [[SD-006-delivery-family]]

## Scope

One vertical story slice, applying CONTRACT-004, CONTRACT-005. Source implementation is not supplied.
Existing upstream semantics and Batten's public boundary remain authoritative.

## Technical Approach

Package installed server and supplied client/tool assets as one qualified cohort; keep static family documentation separate from executable hosting.

Use the qualified public seam rather than the rejected alternative in SD-006.
The tradeoff is explicit capability/spike work before dependent implementation.

## Component Changes

Affected owning modules: `src/lintel/hosting/`, `tools/relay/`, `docs/helix/05-deploy/`. They are proposed paths in the Architecture map,
not existing implementation. Add minimal public exports from the Contracts;
keep concrete providers and framework types out of pure projection/ports.
Batten's adapter changes belong to Batten, not this repository.

Before dependent source, implement and negatively exercise the real project
boundary commands named in Architecture. The presence of this map is not a pass.

### Planned file ownership

| File / package | Story responsibility |
| --- | --- |
| `pyproject.toml` | Package the independent Python API with only qualified locked platform dependencies. |
| `tools/relay/` | Include deterministic build/client inputs in the platform cohort. |
| `docs/helix/05-deploy/` | Separate local, installed, browser, Databricks and public family claims with replayable evidence. |

These are proposed files, not source already created. Integration-specific
representations stay at the named boundary; no helper becomes a second UMF or SQL engine.

## API/Interface Design

CONTRACT-004, CONTRACT-005 owns shared signatures, schemas, controls, errors and compatibility.
This TD only applies those surfaces to US-006; no alternate API is introduced.

## Data Model Changes

Reuse current UMF 0.10 references and the task-board example. No Lintel-owned
business tables, RLS emitter or migration engine. Any needed native fixture/schema
changes are upstream and explicit, never a side effect of constructing the API.

## Security

Use trusted host context, exact admitted application/API identity, current
permission/confirmation and policy-filtered data. Protect internal keys/cursors,
never log variables/credentials, and keep caches/resources request-scoped.
Negative cases in STP-006 must fail through the real public boundary.

## Performance

Apply CONTRACT-005 finite limits; make cost/dispatch evidence observable rather
than infer it from mocks. No throughput/latency SLO is claimed for this unbuilt slice.

## Testing

STP-006 allocates all four criteria:
- US-006-AC1: `cohort_is_complete_offline` at `tests/installed/test_cohort.py`; asserted behavior is owned by the STP.
- US-006-AC2: `databricks_profile_is_explicit` at `tests/packaging/test_databricks_profile.py`; asserted behavior is owned by the STP.
- US-006-AC3: `family_entry_and_claims_are_consistent` at `tests/docs/test_family_claims.py`; asserted behavior is owned by the STP.
- US-006-AC4: `cohort_artifacts_cannot_be_mixed` at `tests/installed/test_cohort.py`; asserted behavior is owned by the STP.

Tests must cite their exact `@covers US-006-AC<number>` IDs and exercise the
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

CONTRACT-004, CONTRACT-005 and their local authoritative schema/example sources define the selected
shapes. Upstream model/constraint/value semantics are reused; no semantic engine
is recreated in a Python wrapper or client build step.
