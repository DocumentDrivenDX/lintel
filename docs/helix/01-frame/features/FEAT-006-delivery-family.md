---
ddx:
  id: FEAT-006
  type: feature-specification
  activity: frame
  authoring:
    home: repo
  links:
    - id: lintel.prd
      kind: informed_by
---

# FEAT-006: Cohort delivery and family integration

**Feature ID**: FEAT-006
**Priority**: P0
**Owner**: Lintel maintainers; named implementation assignee unassigned
**Covered PRD Subsystem(s)**: Delivery and family integration
**Covered PRD Requirements**: FR-11, FR-12
**Cross-Subsystem Rationale**: None — single subsystem.

## Overview

Cohort delivery and family integration lets the batten platform maintainer distribute Lintel with qualified documentation. It realizes FR-11, FR-12
within the selected GraphQL/Relay and Batten profile.

## Ideal Future State

The author can distribute Lintel with qualified documentation and adopt a reproducible platform component with visible support limits. Every supported behavior
has explicit schema/runtime capability and observed consumer evidence.

## Problem Statement

Current upstream model and runtime foundations do not establish this Lintel
capability. The outcome is one coherent supported path rather than per-app glue.

## Requirements

### Functional Requirements by Area

The implementation must satisfy each requirement below.

**DELIV-01** — Provide installed Python/client artifacts and local FastAPI plus Databricks Apps deployment configuration in Batten platform builds.
**DELIV-02** — Register project/family navigation and publish capability/cohort/evidence-qualified documentation without equating static docs with a running service.

### Non-Functional Requirements

Zero silent semantic coercions or cross-context authority leaks in the scoped
corpus. Mandatory finite host bounds. No passing implementation evidence is claimed.

## Detailed Behavior

Package installed server and supplied client/tool assets as one qualified cohort; keep static family documentation separate from executable hosting.

Build the platform server/client cohort with exact versions and source/artifact inventories. Admit the fabricated app with package-registry access disabled and start local ASGI without installation. Check the separate Databricks packaging profile without claiming unexecuted workspace behavior. Publish checked family/source links and support limits; mismatched schema/client/runtime artifacts refuse admission.

See [SD-006](../../02-design/solution-designs/SD-006-delivery-family.md)
for the selected approach and business rules BR-11, BR-12.
Shared shapes and failure rules live in CONTRACT-004, CONTRACT-005.

## User Stories

- [US-006: Distribute lintel with qualified documentation](../user-stories/US-006-delivery-family.md).

## Edge Cases and Error Handling

Unsupported selected meaning, foreign identities, changed sources and capability
mismatch refuse explicitly. Unknown mutation commitment is preserved for recovery.
Only applicable cases are exercised by this feature's story.

## Constraints and Assumptions

Python/FastAPI, GraphQL/Relay and Batten are selected. Architecture and upstream
change inventory govern ownership. Exact target surfaces are specified in CONTRACT-004, CONTRACT-005.
The corresponding solution/story designs apply them. Framework/native/toolchain
compatibility still requires the named interoperability proofs.

## Dependencies

FR-11, FR-12; [architecture](../../02-design/architecture.md);
[upstream changes](../../02-design/upstream-changes.md).

## Out of Scope

REST/OpenAPI product API, a new data compiler, and broader unsupported backend profiles.
