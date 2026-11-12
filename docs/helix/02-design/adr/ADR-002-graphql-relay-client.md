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
# ADR-002 Use JSON:API reads and named commands for the bounded Batten profile

## Problem

Batten applications need typed browser reads, bounded relationship expansion,
and command execution and recovery under host authority. Agents need named
operations with explicit inputs and outcomes. The API must derive from UMF
exposure and preserve the same admitted execution semantics across clients.

## Decision

Default to JSON:API 1.1 resource documents and named command and observation
operations for new Batten consumers of the qualified prepared API /5
task-board profile. Generate OpenAPI 3.1 and named-operation descriptions
from the admitted artifact. Mount the routes through Batten's authenticated
scope ingress under a dedicated prefix. Retain GraphQL and Relay for existing
consumers and applications that need Relay fragments or GraphQL selection.

## Why We Chose This

The task-board browser journey needs one bounded forward collection, resource
refetch and one batched to-one relationship. JSON:API carries these through
resource identifiers, continuation links, linkage and included resources.
Named command operations expose invoke and observe separately while keeping
confirmation, current authorization and outcome ownership in Batten.

GraphQL and Relay supplied a working comparison with the same prepared
artifact and execution ports. Their selection and fragment composition
remain relevant when a consumer needs more than the qualified HTTP profile.

## Consequences

Both surfaces preserve the admitted identity namespace, native cursor scope,
request snapshots, exact Decimal strings and operation authority. An opaque
cursor remains provider-owned. A client must discard in-flight responses when
the actor changes. Unsupported exposure fails during preparation or mounting.

## Assumptions

The initial HTTP profile covers scalar Record fields, forward collection
paging, one selected to-one expansion per request and declared commands.
Databricks Apps, broader query composition and packaged deployment are
separate qualification targets.

## Validation

Chromium 153.0.8010.12 exercised generated OpenAPI TypeScript and Relay 21.0.1
against one local Batten host with PostgreSQL 18.6. The host used production
prepared API /5 admission, Weft generated-read algebra /8, native RLS and
a native recoverable command. The comparison observed matching identity and
paging, exact Decimal, one batch for two parent rows, hidden linkage, required
confirmation and recovery across transports after a lost HTTP response.
Both clients discarded an in-flight response after an actor switch. All 55
native leases closed. This result covers the local source-composed
task-board fixture. Earlier build checks also rejected a breaking field rename
in both the generated OpenAPI client and Relay operation.
