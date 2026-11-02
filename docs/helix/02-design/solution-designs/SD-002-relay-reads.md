---
ddx:
  id: SD-002
  type: solution-design
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-002
      kind: informed_by
    - id: lintel.architecture
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
---

# SD-002-relay-reads: Relay reads and identity

**Feature**: [[FEAT-002]]; target design, not implementation evidence.

## Scope

Apply FR-3, FR-4 to the selected MVP. Shared wire/library surfaces are owned by CONTRACT-002, CONTRACT-003.

## Requirements Mapping

| Requirement | Component | Technical capability | Priority |
| --- | --- | --- | --- |
| FR-3, FR-4 | `src/lintel/relay/`, `src/lintel/graphql/` | Collect qualified field selections, use a request-consistent session and batch related/key reads; map runtime positions into Relay connections without offset emulation. | P0 |

## Solution Approaches

Select the public protocol/projection approach: Collect qualified field selections, use a request-consistent session and batch related/key reads; map runtime positions into Relay connections without offset emulation.

Materializing all rows then slicing in GraphQL is rejected because it defeats policy-first bounded execution. The selected approach adds explicit capability admission and
qualification work in return for one semantic owner and inspectable failures.

## Domain Model

Reuse UMF-qualified Record/Field/Key/relationship/operation identities and safe
host capabilities. API/artifact projections do not become a storage or policy model.
Exact shapes live in CONTRACT-002, CONTRACT-003 and their authoritative example/schema sources.

### Business Rules

- **BR-3** — Logical Node identity remains stable within its explicit identity domain.
- **BR-4** — Visibility is applied before connection slicing and target expansion.

## System Decomposition

Owning modules: `src/lintel/relay/`, `src/lintel/graphql/`. Follow Architecture's allowed/forbidden imports.
The embedding composition root injects external capabilities; no global registry,
implicit provider creation or native engine code enters a pure module.
The corresponding TD-002 applies these owners to the story slice.

## Traceability

FR pair FR-3, FR-4 -> FEAT-002 -> US-002 -> TD-002/STP-002.
The four existing acceptance IDs remain authoritative in the story. STP-002
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

Reuse core 0.10 model references and CONTRACT-002, CONTRACT-003. The example UMF is logical-only;
its exposure/host/manifest schemas and SDL have explicit consumer authority.
No additional schema or native database mutation is introduced here.
