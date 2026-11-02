---
ddx:
  id: SD-001
  type: solution-design
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-001
      kind: informed_by
    - id: lintel.architecture
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
    - id: CONTRACT-005
      kind: informed_by
---

# SD-001-model-projection: Model admission and API projection

**Feature**: [[FEAT-001]]; target design, not implementation evidence.

## Scope

Apply FR-1, FR-2 to the selected MVP. Shared wire/library surfaces are owned by CONTRACT-001, CONTRACT-005.

## Requirements Mapping

| Requirement | Component | Technical capability | Priority |
| --- | --- | --- | --- |
| FR-1, FR-2 | `src/lintel/projection/`, `src/lintel/graphql/` | Resolve explicit model identities directly in admitted UMF JSON through public UMF parsing/validation; build one immutable exposure plan and deterministic schema without interpreting unknown rules. | P0 |

## Solution Approaches

Select the public protocol/projection approach: Resolve explicit model identities directly in admitted UMF JSON through public UMF parsing/validation; build one immutable exposure plan and deterministic schema without interpreting unknown rules.

Generating a schema from raw Python attributes is rejected because it bypasses qualified UMF meaning. The selected approach adds explicit capability admission and
qualification work in return for one semantic owner and inspectable failures.

## Domain Model

Reuse UMF-qualified Record/Field/Key/relationship/operation identities and safe
host capabilities. API/artifact projections do not become a storage or policy model.
Exact shapes live in CONTRACT-001, CONTRACT-005 and their authoritative example/schema sources.

### Business Rules

- **BR-1** — Exposure selects presentation and operations; it grants no authority.
- **BR-2** — Unsupported selected meaning prevents activation rather than shrinking the API.

## System Decomposition

Owning modules: `src/lintel/projection/`, `src/lintel/graphql/`. Follow Architecture's allowed/forbidden imports.
The embedding composition root injects external capabilities; no global registry,
implicit provider creation or native engine code enters a pure module.
The corresponding TD-001 applies these owners to the story slice.

## Traceability

FR pair FR-1, FR-2 -> FEAT-001 -> US-001 -> TD-001/STP-001.
The four existing acceptance IDs remain authoritative in the story. STP-001
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

Reuse core 0.10 model references and CONTRACT-001, CONTRACT-005. The example UMF is logical-only;
its exposure/host/manifest schemas and SDL have explicit consumer authority.
No additional schema or native database mutation is introduced here.
