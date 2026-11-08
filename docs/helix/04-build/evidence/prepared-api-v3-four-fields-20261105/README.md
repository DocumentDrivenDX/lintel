# Prepared API `/3` four-field browser fixture

Captured 2026-11-05. This fixture extends the verified two-root strict `/5`
source with the exact public fields needed by the browser and adapter work. It
was issued by the installed Lintel build a3 wheel and admitted by the isolated
Lintel runtime a4 wheel. The fixture proves build issuance and runtime admission;
it does not prove Batten route registration, native execution, HTTP behavior, or
deployment.

## Prepared identity and roots

- `application`: `fixture-app`
- `identityNamespace`: `fixture.demo.v1` (artifact-owned)
- `notes`: Record `demo.Note`, public `owner`, `enabled`, `amount`, `payload`;
  internal required string Key `demo.id`.
- `tasks`: Record `demo.Task`, public `task_value`; internal required string
  Key `demo.task_id`.
- Both connection roots use the already-pinned Record lookups. The artifact
  contains no Batten Host operation ID and no synthetic source command.
- Host bounds retain `defaultPage=25`, `maxPage=100`, and
  `responseBytes=8388608`.

## SDL

```graphql
scalar Decimal

interface Node {
  id: ID!
}

type Note implements Node {
  amount: Decimal!
  enabled: Boolean!
  id: ID!
  owner: String!
  payload: String!
}

type NoteConnection {
  edges: [NoteEdge!]!
  pageInfo: PageInfo!
}

type NoteEdge {
  cursor: String!
  node: Note!
}

type PageInfo {
  endCursor: String
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
}

type Query {
  node(id: ID!): Node
  nodes(ids: [ID!]!): [Node]!
  notes(after: String, first: Int = 25): NoteConnection!
  tasks(after: String, first: Int = 25): TaskConnection!
}

type Task implements Node {
  id: ID!
  task_value: String!
}

type TaskConnection {
  edges: [TaskEdge!]!
  pageInfo: PageInfo!
}

type TaskEdge {
  cursor: String!
  node: Task!
}
```

The exact generated SDL is preserved in [schema.graphql](schema.graphql); its
SHA-256 and schema digest are `927a32ca59a8abe64c69afbc1e6658ef8c47b7b2ce6786d2702e3d4a4186cf9b`. This rendering shows the names, scalar mappings, and page defaults for review. Node `id` remains the public
Relay identity. The source Key fields are present in the allowed native profile
for internal key binding and are absent from selected Record scalar Fields.

## Inputs, hashes, and admission

[`receipt.json`](receipt.json) records the exact candidate wheel hashes and
versions, frozen source/artifact/target pins, all output file hashes, API and
artifact digests, and the compiler-free admission observations. The original
source sidecar and strict `/5` bundle remain in UMF's
[generated-execution-v5-two-roots-20261104 evidence](../../../../../../umf/docs/helix/04-build/evidence/generated-execution-v5-two-roots-20261104/README.md).
The fixture bytes are preserved both in the fresh temporary directory
`/private/tmp/lintel-api3-four-fields-20261105/` and in `tests/fixtures/` as
`prepared-api-v3-four-fields-{exposure,proof,trust}.json`.

The a3 build used the public generated-executor value constructors to load the
frozen manifest, inventory bytes, trust receipt, and target binding, then called
`lintel_build.prepare_api_v3`. It did not rebuild the source artifact or touch a
database. The output validated against the closed
[prepared API `/3` schema](../../../02-design/schemas/prepared-api-v3.schema.json)
with Draft 2020-12 and zero validation errors. The a4 runtime admitted that
exact byte artifact against the stored `TrustedPreparedRef`; registered
validators for both primary Keys allowed router construction. The isolated
runtime site did not contain UMF, Weft, executor, codegen, or Lintel build
modules.

## Limits

These checks qualify only artifact issuance, schema validation, and runtime
admission/router construction. The browser client's own compile/use tests and
the Batten adapter's preflight, held native-session, shared selected-result
charging, and HTTP checks are separate evidence. No live PostgreSQL request was
made for this receipt.
