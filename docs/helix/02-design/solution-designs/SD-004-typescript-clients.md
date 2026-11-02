---
ddx:
  id: SD-004
  type: solution-design
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-004
      kind: informed_by
    - id: lintel.architecture
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
    - id: CONTRACT-004
      kind: informed_by
---

# SD-004-typescript-clients: TypeScript Relay client builds

**Feature**: [[FEAT-004]]; target design, not implementation evidence.

## Scope

Apply FR-7, FR-8 to the selected MVP. Shared wire/library surfaces are owned by CONTRACT-003, CONTRACT-004.

## Requirements Mapping

| Requirement | Component | Technical capability | Priority |
| --- | --- | --- | --- |
| FR-7, FR-8 | `tools/relay/`, `packages/client/` | Use exported SDL and selected documents with Relay public tooling; produce exact manifests and scope browser stores to the active host context. | P0 |

## Solution Approaches

Select the public protocol/projection approach: Use exported SDL and selected documents with Relay public tooling; produce exact manifests and scope browser stores to the active host context.

A second query/type compiler or global browser cache is rejected because it duplicates semantics or merges authority domains. The selected approach adds explicit capability admission and
qualification work in return for one semantic owner and inspectable failures.

## Domain Model

Reuse UMF-qualified Record/Field/Key/relationship/operation identities and safe
host capabilities. API/artifact projections do not become a storage or policy model.
Exact shapes live in CONTRACT-003, CONTRACT-004 and their authoritative example/schema sources.

### Business Rules

- **BR-7** — Client artifacts belong to the admitted API contract and supplied toolchain.
- **BR-8** — Cached data cannot cross application or principal-context transitions.

## System Decomposition

Owning modules: `tools/relay/`, `packages/client/`. Follow Architecture's allowed/forbidden imports.
The embedding composition root injects external capabilities; no global registry,
implicit provider creation or native engine code enters a pure module.
The corresponding TD-004 applies these owners to the story slice.

## Traceability

FR pair FR-7, FR-8 -> FEAT-004 -> US-004 -> TD-004/STP-004.
The four existing acceptance IDs remain authoritative in the story. STP-004
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

Reuse core 0.10 model references and CONTRACT-003, CONTRACT-004. The example UMF is logical-only;
its exposure/host/manifest schemas and SDL have explicit consumer authority.
No additional schema or native database mutation is introduced here.
