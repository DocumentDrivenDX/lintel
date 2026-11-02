---
ddx:
  id: lintel.index
  type: index
  activity: frame
  authoring:
    home: repo
---

# Lintel HELIX packet

Lintel is a provisional project name. Owner-selected direction: Python/FastAPI,
GraphQL + Relay, TypeScript client builds and required Batten embedding.
The separate runtime is part of the UMF family. REST/OpenAPI is outside the MVP.

## Read in order

1. [Owner intent](00-discover/owner-intent.md) and [vision](00-discover/product-vision.md).
2. [PRD and bounded MVP](01-frame/prd.md), [concerns](01-frame/concerns.md).
3. [Architecture](02-design/architecture.md), [Python embedding decision](02-design/adr/ADR-001-embedded-python-runtime.md), [GraphQL/Relay decision](02-design/adr/ADR-002-graphql-relay-client.md).
4. [UMF/runtime/Batten changes and spikes](02-design/upstream-changes.md).
5. [Verification strategy](03-test/test-plan.md).
6. [Family membership/publication](05-deploy/family-integration.md).
7. [Source/evidence inventory](00-discover/source-inventory.md) and [framing validation](04-build/framing-validation.md).

## Scope map

| Feature | PRD requirements | Story |
| --- | --- | --- |
| [FEAT-001: Model projection](01-frame/features/FEAT-001-model-projection.md) | FR-1–2 | [US-001](01-frame/user-stories/US-001-model-projection.md) |
| [FEAT-002: Relay reads](01-frame/features/FEAT-002-relay-reads.md) | FR-3–4 | [US-002](01-frame/user-stories/US-002-relay-reads.md) |
| [FEAT-003: Commands](01-frame/features/FEAT-003-commands-outcomes.md) | FR-5–6 | [US-003](01-frame/user-stories/US-003-commands-outcomes.md) |
| [FEAT-004: TypeScript clients](01-frame/features/FEAT-004-typescript-clients.md) | FR-7–8 | [US-004](01-frame/user-stories/US-004-typescript-clients.md) |
| [FEAT-005: Batten embedding](01-frame/features/FEAT-005-batten-embedding.md) | FR-9–10 | [US-005](01-frame/user-stories/US-005-batten-embedding.md) |
| [FEAT-006: Delivery/family](01-frame/features/FEAT-006-delivery-family.md) | FR-11–12 | [US-006](01-frame/user-stories/US-006-delivery-family.md) |

## Delivery boundary

This packet defines requirements and the target architecture. It implements no
API server, client compiler or upstream engine changes. Exact public contracts,
interoperability spikes and real boundary checks precede product implementation.
No native/browser/deployed support follows from document validation.

HELIX catalog: installed plugin 0.20.0 `workflows/graph.yml`. No methodology
catalog is copied into Lintel. Existing UMF and Batten implementation work remains
separate; the linked Batten integration note records only this planning direction.
