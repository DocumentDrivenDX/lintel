---
ddx:
  id: lintel.owner-intent
  type: input
  activity: discover
  authoring:
    home: repo
---

# Owner intent and scope decisions

Source: this Codex conversation, 2026-11-02, America/New_York.

1. Frame a separate sibling project with HELIX: scope, architecture, MVP and
   changes needed in UMF and the runtime.
2. Include it in the UMF family on DocumentDrivenDX.github.io.
3. Use Lintel provisionally as the project name.
4. Prefer a Python backend to fit the Databricks Apps FastAPI backend standard.
5. Include this runtime in Batten and comprehend building TypeScript clients
   for the same API.
6. Prefer GraphQL + Relay; both GraphQL and OpenAPI are unnecessary. Relay's
   type descriptions, pagination and node expansion motivate the selection.

The latest choices replace the earlier dual REST/GraphQL and TypeScript-server
suggestions. FastAPI is the HTTP host; it does not imply a generated REST product API.
A standalone app factory remains useful for testing and other embedders; Batten
is the required first consumer. Batten integration is a deliverable, not optional.

Planning assumptions: PostgreSQL 18 first; one-hop relationships; startup schema
construction; request-local cache; no admin UI. These are reversible design
choices, not additional owner statements. No delivery date, staffing, budget,
production workspace, IdP or family-catalog source repository was specified.

## Direct UMF input

Owner clarification: consume UMF directly. UMF is already the model/schema; do
not invent an intermediate schema-description API. An ORM may expose its existing
UMF as JSON if needed. Update the specs and execute the first direct-input spike;
make only UMF/runtime changes that its evidence demonstrates are necessary.
