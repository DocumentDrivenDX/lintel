---
ddx:
  id: TD-002
  type: technical-design
  activity: design
  authoring:
    home: repo
  links:
    - id: US-002
      kind: informed_by
    - id: SD-002
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
---

# TD-002-relay-reads: Relay reads and identity

**User Story**: [[US-002-relay-reads]] | **Feature**: [[FEAT-002]] | **Solution Design**: [[SD-002-relay-reads]]

## Scope

One vertical story slice, applying CONTRACT-002, CONTRACT-003. Source implementation is not supplied.
Existing upstream semantics and Batten's public boundary remain authoritative.

## Technical Approach

Collect qualified field selections, use a request-consistent session and batch related/key reads; map runtime positions into Relay connections without offset emulation.

Use the qualified public seam rather than the rejected alternative in SD-002.
The tradeoff is explicit capability/spike work before dependent implementation.

## Component Changes

Affected owning modules: `src/lintel/relay/`, `src/lintel/graphql/`. They are proposed paths in the Architecture map,
not existing implementation. Add minimal public exports from the Contracts;
keep concrete providers and framework types out of pure projection/ports.
Batten's adapter changes belong to Batten, not this repository.

Before dependent source, implement and negatively exercise the real project
boundary commands named in Architecture. The presence of this map is not a pass.

### Planned file ownership

| File / package | Story responsibility |
| --- | --- |
| `src/lintel/relay/nodes.py` | Validate exposed decoded key/type and group authorized keyed lookups; preserve slot order. |
| `src/lintel/relay/connections.py` | Map runtime edge positions and exact PageInfo; never substitute offset or page-next cursors. |
| `src/lintel/relay/loaders.py` | Request-only qualified key batching and selection reuse under the supplied snapshot. |
| `src/lintel/graphql/queries.py` | Collect selections/fragments and enforce field/expansion/resource preflight before dispatch. |

These are proposed files, not source already created. Integration-specific
representations stay at the named boundary; no helper becomes a second UMF or SQL engine.

## API/Interface Design

CONTRACT-002, CONTRACT-003 owns shared signatures, schemas, controls, errors and compatibility.
This TD only applies those surfaces to US-002; no alternate API is introduced.

## Data Model Changes

Reuse current UMF 0.10 references and the task-board example. No Lintel-owned
business tables, RLS emitter or migration engine. Any needed native fixture/schema
changes are upstream and explicit, never a side effect of constructing the API.

## Security

Use trusted host context, exact admitted application/API identity, current
permission/confirmation and policy-filtered data. Protect internal keys/cursors,
never log variables/credentials, and keep caches/resources request-scoped.
Negative cases in STP-002 must fail through the real public boundary.

## Performance

Apply CONTRACT-005 finite limits; make cost/dispatch evidence observable rather
than infer it from mocks. No throughput/latency SLO is claimed for this unbuilt slice.

## Testing

[STP-002](../../03-test/test-plans/STP-002-relay-reads.md) allocates all four criteria:
- US-002-AC1: `connection_resumes_from_any_edge` at `tests/native/test_relay_reads.py`; asserted behavior is owned by the STP.
- US-002-AC2: `node_and_store_scopes_are_isolated` at `tests/client/isolation.spec.ts`; asserted behavior is owned by the STP.
- US-002-AC3: `relationships_are_batched` at `tests/native/test_relay_reads.py`; asserted behavior is owned by the STP.
- US-002-AC4: `node_fields_are_stable_within_request` at `tests/native/test_relay_reads.py`; asserted behavior is owned by the STP.

Tests must cite their exact `@covers US-002-AC<number>` IDs and exercise the
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
