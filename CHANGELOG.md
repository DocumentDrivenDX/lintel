# Changelog

## 0.1.0a6 - 2026-11-11

First release that goes from a UMF document to a served GraphQL API.
Versions 0.1.0a2 to 0.1.0a5 were never published; their changes ship here.

- `lintel example | prepare | serve` command line and an in-memory execution port
  (`lintel.memory`), `lintel.trust.pin_for`, `lintel.app`.
- The prepared-API build tool, previously the never-published `lintel-api-build`
  package, is now `lintel.build` in this wheel (extra `build`).
- Prepared APIs v1 to v5 (v5 adds task-board commands and relationships) with runtime admission, Relay-style Node IDs and
  connection preflight (v2 to v4 builders need the unpublished
  `umf_access_generated_executor` and raise `UNSUPPORTED` without it).
- The build extra can derive OpenAPI 3.1 and named-operation contracts from an
  admitted prepared API v5 for scalar Record reads, forward pages and declared
  commands. The projection refuses selected relationships and supplies contracts
  for client generation. The served runtime remains GraphQL.
- `lintel.experimental` is now shipped in the wheel (extra `experimental`).
- Example inputs ship inside the package.
- Dependencies: `umf-core>=0.10.0,<0.11` (tested on 0.10.10), `fastapi>=0.135,<1`,
  `graphql-core>=3.3,<3.4`. Removed `weft-sql`, `umf-codegen`, `umf-access`,
  `pgserver-pg18` and URL-based dependencies. `strawberry-graphql` is now only
  needed by the `experimental` extra.
- The README quickstart is run against the built wheel in a fresh venv in CI and in the release workflow.
- Removed the evidence packets and native-read spikes from the tree.

## 0.1.0a1

Experimental alpha: bounded UMF projection laboratory.
