---
ddx:
  id: SD-005
  type: solution-design
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-005
      kind: informed_by
    - id: lintel.architecture
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-005
      kind: informed_by
---

# SD-005-batten-embedding: Batten embedding and lifecycle

**Feature**: [[FEAT-005]]; target design, not implementation evidence.

## Scope

Apply FR-9, FR-10 to the selected MVP. Shared wire/library surfaces are owned by CONTRACT-002, CONTRACT-005.

## Requirements Mapping

| Requirement | Component | Technical capability | Priority |
| --- | --- | --- | --- |
| FR-9, FR-10 | `src/lintel/ports.py`, `src/lintel/asgi/`, `src/lintel/hosting/` | Supply neutral Python protocols and pure router factories; Batten owns its optional adapter and embedding composition owns trusted context and borrowed resources. | P0 |

## Solution Approaches

Select the public protocol/projection approach: Supply neutral Python protocols and pure router factories; Batten owns its optional adapter and embedding composition owns trusted context and borrowed resources.

Importing Batten into Lintel or GraphQL into Batten core is rejected because it creates mutual package coupling. The selected approach adds explicit capability admission and
qualification work in return for one semantic owner and inspectable failures.

## Domain Model

Reuse UMF-qualified Record/Field/Key/relationship/operation identities and safe
host capabilities. API/artifact projections do not become a storage or policy model.
Exact shapes live in CONTRACT-002, CONTRACT-005 and their authoritative example/schema sources.

### Business Rules

- **BR-9** — The host remains the authority and lifecycle owner of borrowed capabilities.
- **BR-10** — Runtime startup never installs dependencies or deploys native schemas.

## System Decomposition

Owning modules: `src/lintel/ports.py`, `src/lintel/asgi/`, `src/lintel/hosting/`. Follow Architecture's allowed/forbidden imports.
The embedding composition root injects external capabilities; no global registry,
implicit provider creation or native engine code enters a pure module.
The corresponding TD-005 applies these owners to the story slice.

## Traceability

FR pair FR-9, FR-10 -> FEAT-005 -> US-005 -> TD-005/STP-005.
The four existing acceptance IDs remain authoritative in the story. STP-005
names fixtures, primary assertion layers, commands and required citations.

## Concern Alignment

Respect neutral ports, Python/uv and TypeScript/Bun tooling boundaries, exact values,
finite limits, deny-by-default host authority and observable verification. No UI
framework or dependency is installed by this design. Diagnostics inherit the host
sink and safe context policy; actual receiver/privacy proof remains required.

## Constraints & Assumptions

The task-board example specifies required native operations without implementing
them. Interoperability spikes select framework/compiler versions and qualify
upstream seams. This design freezes target behavior, not an existing provider ABI.

## Risks

The owning public seam may need a versioned upstream addition. Refuse unavailable
capabilities; do not hide the gap behind private imports, weaker guarantees or a
parallel engine. Exact upstream release intersections remain to be qualified.

## Schema Basis

Reuse core 0.10 model references and CONTRACT-002, CONTRACT-005. The example UMF is logical-only;
its exposure/host/manifest schemas and SDL have explicit consumer authority.
No additional schema or native database mutation is introduced here.
