---
ddx:
  id: ADR-001
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: lintel.prd
      kind: informed_by
---

# ADR-001: Embed a separate Python API runtime in Batten

## Problem

Batten needs a GraphQL surface over UMF without a second execution engine or
application-specific API implementation. The owner prefers Python/FastAPI and
requires inclusion in Batten's runtime.

## Decision

Own the API projection and GraphQL runtime in Lintel. Package it independently
and embed it through Batten's public async host and ASGI composition boundaries.
Batten supplies admission, actor authority, confirmation, attribution and resources.
Lintel defines a framework-neutral execution port; Batten owns the adapter that
implements it through public host operations. Lintel has no Batten dependency,
and generic Batten core has no Lintel/GraphQL dependency. Native execution stays
in existing providers.
Use Python 3.11 as the initial library floor; qualify the actual deployed interpreter.

## Why We Chose This

### Over implementing the API inside UMF

HTTP hosting and Relay client behavior are consumer responsibilities. A separate
package keeps UMF's model and engine independent of a framework and host lifecycle.

### Over a TypeScript gateway and Python sidecar

Python directly fits the owner's FastAPI host and existing access runtime. A second
process adds identity, cancellation and protocol boundaries without an MVP need.

### Over placing all implementation in Batten

A public independent package can serve other embedders while Batten owns its thin
binding and qualified runtime composition. Independence does not permit bypassing
Batten's host when embedded.

## Consequences

Batten's cohort must carry Lintel and its selected Python dependencies; applications
install nothing at startup. Demonstrated upstream document-access or execution gaps must be solved
upstream or explicitly adapted, never by importing private modules.

Drift signals: Lintel emits SQL or policies; pure Batten core imports GraphQL;
resolvers call raw providers around host gates; application schemas install code.

## Assumptions

Provisional risk: the public Batten read/provider seam must express the selected
Relay profile. Current source has a minimal operation port, not full connection
or batching evidence. A bounded public-boundary spike precedes interface freeze.

## Validation

Result: not tested. This decision follows owner direction and inspected public
source boundaries. Dynamic-schema and installed-cohort proof remain required.
