---
ddx:
  id: SD-006
  type: solution-design
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-006
      kind: informed_by
    - id: lintel.architecture
      kind: informed_by
    - id: CONTRACT-004
      kind: informed_by
    - id: CONTRACT-005
      kind: informed_by
---

# SD-006-delivery-family: Cohort delivery and family integration

**Feature**: [[FEAT-006]]; target design, not implementation evidence.

## Scope

Apply FR-11, FR-12 to the selected MVP. Shared wire/library surfaces are owned by CONTRACT-004, CONTRACT-005.

## Requirements Mapping

| Requirement | Component | Technical capability | Priority |
| --- | --- | --- | --- |
| FR-11, FR-12 | `src/lintel/hosting/`, `tools/relay/`, `docs/helix/05-deploy/` | Package installed server and supplied client/tool assets as one qualified cohort; keep static family documentation separate from executable hosting. | P0 |

## Solution Approaches

Select the public protocol/projection approach: Package installed server and supplied client/tool assets as one qualified cohort; keep static family documentation separate from executable hosting.

Claiming a Databricks or native feature from package installation/static publication is rejected because its execution boundary remains untested. The selected approach adds explicit capability admission and
qualification work in return for one semantic owner and inspectable failures.

## Domain Model

Reuse UMF-qualified Record/Field/Key/relationship/operation identities and safe
host capabilities. API/artifact projections do not become a storage or policy model.
Exact shapes live in CONTRACT-004, CONTRACT-005 and their authoritative example/schema sources.

### Business Rules

- **BR-11** — Platform artifacts, rather than application startup, supply dependencies.
- **BR-12** — Published support describes only version/subset/evidence-qualified behavior.

## System Decomposition

Owning modules: `src/lintel/hosting/`, `tools/relay/`, `docs/helix/05-deploy/`. Follow Architecture's allowed/forbidden imports.
The embedding composition root injects external capabilities; no global registry,
implicit provider creation or native engine code enters a pure module.
The corresponding TD-006 applies these owners to the story slice.

## Traceability

FR pair FR-11, FR-12 -> FEAT-006 -> US-006 -> TD-006/STP-006.
The four existing acceptance IDs remain authoritative in the story. STP-006
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

Reuse core 0.10 model references and CONTRACT-004, CONTRACT-005. The example UMF is logical-only;
its exposure/host/manifest schemas and SDL have explicit consumer authority.
No additional schema or native database mutation is introduced here.
