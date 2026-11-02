---
ddx:
  id: SD-003
  type: solution-design
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-003
      kind: informed_by
    - id: lintel.architecture
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
---

# SD-003-commands-outcomes: Declared commands and exact outcomes

**Feature**: [[FEAT-003]]; target design, not implementation evidence.

## Scope

Apply FR-5, FR-6 to the selected MVP. Shared wire/library surfaces are owned by CONTRACT-002, CONTRACT-003.

## Requirements Mapping

| Requirement | Component | Technical capability | Priority |
| --- | --- | --- | --- |
| FR-5, FR-6 | `src/lintel/graphql/`, `src/lintel/ports.py` | Derive command arguments from upstream metadata, preserve omission/null, dispatch through the host and expose authoritative uncertainty/recovery outcomes. | P0 |

## Solution Approaches

Select the public protocol/projection approach: Derive command arguments from upstream metadata, preserve omission/null, dispatch through the host and expose authoritative uncertainty/recovery outcomes.

Generic save and transport retry are rejected because they invent mutation authority or commitment. The selected approach adds explicit capability admission and
qualification work in return for one semantic owner and inspectable failures.

## Domain Model

Reuse UMF-qualified Record/Field/Key/relationship/operation identities and safe
host capabilities. API/artifact projections do not become a storage or policy model.
Exact shapes live in CONTRACT-002, CONTRACT-003 and their authoritative example/schema sources.

### Business Rules

- **BR-5** — Only a declared host-authorized command may change business state.
- **BR-6** — Observation reports an attempt; it never executes an unobserved command.

## System Decomposition

Owning modules: `src/lintel/graphql/`, `src/lintel/ports.py`. Follow Architecture's allowed/forbidden imports.
The embedding composition root injects external capabilities; no global registry,
implicit provider creation or native engine code enters a pure module.
The corresponding TD-003 applies these owners to the story slice.

## Traceability

FR pair FR-5, FR-6 -> FEAT-003 -> US-003 -> TD-003/STP-003.
The four existing acceptance IDs remain authoritative in the story. STP-003
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
