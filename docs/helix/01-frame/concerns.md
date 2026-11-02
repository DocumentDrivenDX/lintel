---
ddx:
  id: lintel.concerns
  type: concerns
  activity: frame
  authoring:
    home: repo
  links:
    - id: lintel.product-vision
      kind: informed_by
---

# Project concerns

## Active Concerns

Selection follows the owner's Python, Batten and GraphQL/Relay direction.
The installed HELIX catalog is authoritative; no catalog files are copied here.

| Concern | Source | Areas | Why Active | Key Practices |
| --- | --- | --- | --- | --- |
| python-uv | library; operator-override for language-runtime, assumption for uv | all | Embeddable Python host | uv locks, Python 3.11 floor, Ruff, Pyright, pytest; typed settings at composition |
| modularity-and-encapsulation | library; shipped-default | all | Planned handwritten service and adapters | Minimal public surfaces, permitted imports and real negative boundary checks |
| code-shape-ceilings | library; shipped-default | all | Greenfield handwritten software | Strict library defaults; no widening ceilings to hide coupling |
| testing | library; shipped-default | all | Runtime and client behavior | Fewest tests proving distinct public behaviors; case tables |
| verification | library; shipped-default | all | Claims span installed/native/browser/deployed layers | Evidence at each claimed boundary; no fake-to-native inference |
| security-owasp | library; assumption | api, infra | Network boundary | Bounded input, parameter binding, no payloads/secrets in diagnostics |
| authorization-model | library; assumption | api, data | Nodes, relationships and mutations expose data | Batten central authority plus native policies; deny by default |
| hexagonal-architecture | library; assumption | all | Pure projection with explicit adapters | Core has no framework, driver or host internals |
| api-style | library; operator direction | api | GraphQL + Relay only | One schema, async resolvers, request-local batch loaders, typed outcomes |
| o11y-otel | library; shipped-default | all | Running API and agent development diagnostics | Correlated service/run evidence; safe attributes; real receiver proof |
| relational-data-modeling | library; shipped-default | data | PostgreSQL 18 reference binding | Upstream owns schema/DDL/integrity; Lintel tests native behavior |
| sample-data | library; assumption | data | Shared task-board demonstration | Fabricated governed records, boundary/null/empty/large cases; deterministic inputs |

## Project Overrides

| Concern | Practice | Override | Authority |
| --- | --- | --- | --- |
| api-style | Avoid two protocols for the same client | GraphQL + Relay is the sole product surface; FastAPI health endpoints do not add REST data APIs. | Owner intent |
| python-uv | Environment-oriented configuration defaults | Typed files and injected host settings; no new application environment variables. Existing Databricks-provided process variables stay in the hosting adapter. | Batten CONTRACT-001 and ADR-006; architecture |
| python-uv | No requirements.txt source | A generated locked deployment export may be required by the selected Databricks Apps packaging path; pyproject/uv.lock remain source authority. | Deployment qualification spike |

## Area Labels

- `area:api`: schema construction, Relay semantics and GraphQL hosting.
- `area:data`: runtime adapters, exact values and fabricated corpus.
- `area:client`: TypeScript artifacts, Relay environment and browser behavior.
- `area:infra`: packaged cohorts, Databricks Apps and family publication.
- `area:cli`: offline schema export and client build/check tooling.

## Concern Conflicts

| Conflict | Resolution |
| --- | --- |
| Python server vs TypeScript clients | language-runtime slot is python-uv (operator direction); TypeScript/Bun is client build tooling, not a second backend. |
| Library vs datastore/deploy selection | PostgreSQL 18 is the first execution binding, not a Lintel-owned database. Local ASGI is the first environment; Databricks Apps is a separately qualified host. |
| Account product vs host identity | No signup/session UI or owned IdP. Authentication and grants are injected by Batten; no auth-provider slot filler is selected. |

No frontend-framework slot is selected: Lintel does not own a UI framework.
Relay artifact/browser tests use Batten's chosen application stack; Playwright
is the proposed browser evidence tool, not a new application dependency.
Architecture-style is hexagonal-architecture (assumption): pure schema projection
and explicit runtime/host adapters. No persistence engine is introduced.

## Observability Applicability

Service traces, request failures, admission diagnostics and agent-run evidence
apply. Model/GenAI telemetry does not: Lintel runs no model calls. Source-free
framing is verified structurally; implementation must prove privacy, correlation,
bounded exporter failure and receiver ingestion before OTel integration claims.
