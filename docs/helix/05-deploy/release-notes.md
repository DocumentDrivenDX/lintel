---
ddx:
  id: lintel.release-0.1.0a1
  type: release-notes
  activity: deploy
  authoring:
    home: repo
  links:
    - id: TD-006
      kind: informed_by
---

# Lintel 0.1.0a1

## Release Scope

First experimental Python distribution: `lintel-api==0.1.0a1`, tag `v0.1.0a1`,
prepared on 2026-11-03 for PyPI and GitHub. The import namespace is `lintel`.
This alpha packages the tested direct-UMF scalar projection; it is not the
complete GraphQL/Relay runtime described by the product specifications.

## Audience and Channels

Developers exploring UMF-to-GraphQL projection can install the wheel from PyPI.
The GitHub release supplies archives and these notes. Native runtime contributors
can use the source archive's qualification harnesses and governed specifications.

## Highlights

- Direct UMF JSON validation and bounded scalar projection are importable from
  `lintel.experimental.projection`.
- `lintel.experimental.schema` builds the dynamic Strawberry laboratory schema
  and exports deterministic GraphQL SDL.
- Exact decimal text, canonical UUID, optional-field omission and explicit null
  retain the existing probe behavior.

## Required Actions Summary

Install `lintel-api==0.1.0a1` with Python 3.11 for the qualified initial profile.
Experimental APIs may change in later alphas. No business-data migration is needed.

## Changes and Fixes

The S-01 projection and schema modules move from the source-only spike into the
installed `lintel.experimental` namespace. Spike harnesses and tests consume those
same modules; the implementation is not duplicated. The source archive includes
S-02 and request-read qualification probes. Native tools are not wheel dependencies.

Release checks pass 47 tests, strict typing, lint, formatting and import boundaries.
A wheel built through the source archive passes an isolated installed query using
`9007199254740993.01` without losing decimal precision. Package metadata passes
Twine 7.0.0. These checks do not establish complete product conformance.

## Breaking Changes and Required Actions

This is the first published alpha. Source users should replace imports from
`spikes.direct_umf.projection` and `spikes.direct_umf.schema` with the corresponding
`lintel.experimental` modules. No stable public API or prior published migration
is claimed.

## Migration or Rollback Guidance

Install the exact alpha version in an isolated environment and follow the
[README example](../../../README.md). To hold adoption, remove the alpha from that
environment and continue using the prior application environment. Uninstalling
Lintel does not change databases or reverse operations performed by other software.

## Known Issues and Support

The `probe` query and `echo` mutation are laboratory roots and must not be mounted
as a production API. The wheel does not implement native execution or admission,
Relay identity/pagination, TypeScript client builds, Batten embedding, or managed
Databricks deployment. The separately qualified upstream request-read primitives
are not integrated into a Lintel product API by this release.

Only the recorded scalar subset and Python 3.11 installed profile are qualified.
FastAPI transport and disposable PostgreSQL qualification remain source harnesses.
Report issues at [DocumentDrivenDX/lintel](https://github.com/DocumentDrivenDX/lintel/issues).

## References

- [Direct UMF evidence](../04-build/direct-umf-spike.md)
- [Native read evidence](../04-build/native-read-spike.md)
- [Upstream request-read evidence](../04-build/request-read-implementation.md)
- [Delivery design](../02-design/technical-designs/TD-006-delivery-family.md)
