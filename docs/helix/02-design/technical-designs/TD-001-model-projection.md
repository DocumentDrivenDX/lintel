---
ddx:
  id: TD-001
  type: technical-design
  activity: design
  authoring:
    home: repo
  links:
    - id: US-001
      kind: informed_by
    - id: SD-001
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
    - id: CONTRACT-005
      kind: informed_by
---

# TD-001-model-projection: Model admission and API projection

**User Story**: [[US-001-model-projection]] | **Feature**: [[FEAT-001]] | **Solution Design**: [[SD-001-model-projection]]

## Scope

One vertical story slice, applying CONTRACT-001, CONTRACT-005. Source implementation is not supplied.
Existing upstream semantics and Batten's public boundary remain authoritative.

## Technical Approach

Resolve explicit model identities directly in admitted UMF JSON through public UMF parsing/validation; build one immutable exposure plan and deterministic schema without interpreting unknown rules.

Use the qualified public seam rather than the rejected alternative in SD-001.
The tradeoff is explicit capability/spike work before dependent implementation.

## Component Changes

Affected owning modules: `src/lintel/projection/`, `src/lintel/graphql/`. They are proposed paths in the Architecture map,
not existing implementation. Add minimal public exports from the Contracts;
keep concrete providers and framework types out of pure projection/ports.
Batten's adapter changes belong to Batten, not this repository.

Before dependent source, implement and negatively exercise the real project
boundary commands named in Architecture. The presence of this map is not a pass.

### Planned file ownership

| File / package | Story responsibility |
| --- | --- |
| `src/lintel/projection/prepare.py` | Resolve qualified metadata and exposure; reject incomplete selected meanings before output. |
| `src/lintel/projection/names.py` | Maintain injective GraphQL/source identity mapping and generated-name collision checks. |
| `src/lintel/projection/identity.py` | Deterministic SDL/source/capability digest framing; no actor or credential inputs. |

These are proposed files, not source already created. Integration-specific
representations stay at the named boundary; no helper becomes a second UMF or SQL engine.

## API/Interface Design

CONTRACT-001, CONTRACT-005 owns shared signatures, schemas, controls, errors and compatibility.
This TD only applies those surfaces to US-001; no alternate API is introduced.

## Data Model Changes

Reuse current UMF 0.10 references and the task-board example. No Lintel-owned
business tables, RLS emitter or migration engine. Any needed native fixture/schema
changes are upstream and explicit, never a side effect of constructing the API.

## Security

Use trusted host context, exact admitted application/API identity, current
permission/confirmation and policy-filtered data. Protect internal keys/cursors,
never log variables/credentials, and keep caches/resources request-scoped.
Negative cases in STP-001 must fail through the real public boundary.

## Performance

Apply CONTRACT-005 finite limits; make cost/dispatch evidence observable rather
than infer it from mocks. No throughput/latency SLO is claimed for this unbuilt slice.

## Testing

STP-001 allocates all four criteria:
- US-001-AC1: `schema_is_deterministic` at `tests/model_projection/test_model_projection.py`; asserted behavior is owned by the STP.
- US-001-AC2: `unknown_selected_meaning_refuses` at `tests/model_projection/test_model_projection.py`; asserted behavior is owned by the STP.
- US-001-AC3: `dependency_type_grants_no_access` at `tests/model_projection/test_model_projection.py`; asserted behavior is owned by the STP.
- US-001-AC4: `relay_name_collision_is_explicit` at `tests/model_projection/test_model_projection.py`; asserted behavior is owned by the STP.

Tests must cite their exact `@covers US-001-AC<number>` IDs and exercise the
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

CONTRACT-001, CONTRACT-005 and their local authoritative schema/example sources define the selected
shapes. Upstream model/constraint/value semantics are reused; no semantic engine
is recreated in a Python wrapper or client build step.


## Bounded S-01 source gate

The direct-input spike lives in `spikes/direct_umf/`, separate from the proposed
product modules. `scripts/check_quality.py` is its quality entrypoint. Strict
Python ceilings are complexity 10, statements 40, returns 6, branches 12, public
methods 15; file caps are 500 source / 800 test lines. No ceiling exceptions.
Only `scripts/`, `spikes/` and `tests/` are handwritten executable source in this
probe. `docs/` contains specifications and illustrative protocol stubs, not runtime
code; environments, cached bytecode and generated evidence are excluded from
source lint/shape checks. This bounded probe installs no developer git hooks or
application runtime instrumentation. Product source/client gates remain separate.

Observed quality controls
include valid-source acceptance, over-complexity, oversize and ceiling-change
refusal. SPIKE-001 owns its qualification limits.
