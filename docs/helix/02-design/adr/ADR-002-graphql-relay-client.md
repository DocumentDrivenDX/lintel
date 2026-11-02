---
ddx:
  id: ADR-002
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: lintel.prd
      kind: informed_by
---

# ADR-002: Use GraphQL and Relay as the shared API/client surface

## Problem

The owner wants standardized type descriptions, pagination and node expansion,
plus TypeScript clients for the API included with Batten. Dual REST/GraphQL
surfaces add protocol work without a stated need.

## Decision

Build one GraphQL API with a bounded Relay server profile: stable Node refetch,
forward connections, fragments, selected relationship expansion and declared
mutations. Export its exact schema and use Relay's compiler for TypeScript
operation/fragment artifacts and its runtime for normalized client access.
REST/OpenAPI product API generation is outside the MVP.

## Why We Chose This

### Over REST plus OpenAPI

The owner selected GraphQL/Relay's shared conventions and client model. Keeping
a second product protocol would add mappings and parity obligations without
serving a named additional consumer.

### Over a custom TypeScript query generator

Relay already compiles selected operations/fragments. Lintel owns schema export,
scalar mappings, network wiring and reproducible build/check integration rather
than a second client compiler or normalized cache.

## Consequences

Node identity, per-edge cursor semantics, request-local consistency and fragment
compilation are required behavior. Generic GraphQL schema validity does not
establish Relay compatibility. No implicit subscriptions or federation are added.

Drift signals: next-page tokens called edge cursors, source-hash-churned IDs,
unauthorized refetch, unbounded in-memory connection slicing or hand-maintained
TypeScript schema types.

## Assumptions

Provisional risk: Strawberry's dynamic type construction and Relay compiler
integration must pass the selected exact-value and async profile. Candidate
libraries are reversible; GraphQL/Relay and TypeScript client outcomes are required.

## Validation

Result: not tested. Official Relay identification/connections/type-emission
references support the approach; no Lintel conformance or browser execution exists.
