---
ddx:
  id: TD-004
  type: technical-design
  activity: design
  authoring:
    home: repo
  links:
    - id: US-004
      kind: informed_by
    - id: SD-004
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
    - id: CONTRACT-004
      kind: informed_by
---

# TD-004-typescript-clients: TypeScript Relay client builds

**User Story**: [[US-004-typescript-clients]] | **Feature**: [[FEAT-004]] | **Solution Design**: [[SD-004-typescript-clients]]

## Scope

One vertical story slice, applying CONTRACT-003, CONTRACT-004. Source implementation is not supplied.
Existing upstream semantics and Batten's public boundary remain authoritative.

## Technical Approach

Use exported SDL and selected documents with Relay public tooling; produce exact manifests and scope browser stores to the active host context.

Use the qualified public seam rather than the rejected alternative in SD-004.
The tradeoff is explicit capability/spike work before dependent implementation.

## Component Changes

Affected owning modules: `tools/relay/`, `packages/client/`. They are proposed paths in the Architecture map,
not existing implementation. Add minimal public exports from the Contracts;
keep concrete providers and framework types out of pure projection/ports.
Batten's adapter changes belong to Batten, not this repository.

Before dependent source, implement and negatively exercise the real project
boundary commands named in Architecture. The presence of this map is not a pass.

### Planned file ownership

| File / package | Story responsibility |
| --- | --- |
| `tools/relay/compiler.ts` | Invoke only supplied public Relay tooling; collect artifact/scalar-validation integration evidence. |
| `tools/relay/inventory.ts` | Build/check exact byte inventory and refuse edited/unowned outputs. |
| `packages/client/network.ts` | Use the injected authenticated transport and expected API identity; retain post-dispatch uncertainty. |
| `packages/client/scalars.ts` | Validated string-carrier brands; no float/number conversion. |
| `packages/client/environment.ts` | Scope stores and suppress old in-flight response publication after context disposal. |

These are proposed files, not source already created. Integration-specific
representations stay at the named boundary; no helper becomes a second UMF or SQL engine.

## API/Interface Design

CONTRACT-003, CONTRACT-004 owns shared signatures, schemas, controls, errors and compatibility.
This TD only applies those surfaces to US-004; no alternate API is introduced.

## Data Model Changes

Reuse current UMF 0.10 references and the task-board example. No Lintel-owned
business tables, RLS emitter or migration engine. Any needed native fixture/schema
changes are upstream and explicit, never a side effect of constructing the API.

## Security

Use trusted host context, exact admitted application/API identity, current
permission/confirmation and policy-filtered data. Protect internal keys/cursors,
never log variables/credentials, and keep caches/resources request-scoped.
Negative cases in STP-004 must fail through the real public boundary.

## Performance

Apply CONTRACT-005 finite limits; make cost/dispatch evidence observable rather
than infer it from mocks. No throughput/latency SLO is claimed for this unbuilt slice.

## Testing

[STP-004](../../03-test/test-plans/STP-004-typescript-clients.md) allocates all four criteria:
- US-004-AC1: `relay_artifacts_compile` at `tests/client/build.test.ts`; asserted behavior is owned by the STP.
- US-004-AC2: `client_drift_refuses` at `tests/client/build.test.ts`; asserted behavior is owned by the STP.
- US-004-AC3: `browser_uses_generated_relay_artifacts` at `tests/client/journey.spec.ts`; asserted behavior is owned by the STP.
- US-004-AC4: `client_scalars_and_actor_transition_are_safe` at `tests/client/isolation.spec.ts`; asserted behavior is owned by the STP.

Tests must cite their exact `@covers US-004-AC<number>` IDs and exercise the
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

CONTRACT-003, CONTRACT-004 and their local authoritative schema/example sources define the selected
shapes. Upstream model/constraint/value semantics are reused; no semantic engine
is recreated in a Python wrapper or client build step.
