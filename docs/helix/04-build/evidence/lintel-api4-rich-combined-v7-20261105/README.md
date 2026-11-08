# Rich Lintel API4 fixture for combined Weft `/7`

## Scope

This is a build and Relay compiler fixture for a single source-generated UMF
artifact with `demo.Note` and `demo.Task` Record roots. Both connections use the
same selected Weft `/7` algebra and host capability profile. The prepared API
keeps their primary Keys internal to the Relay `Node` codec.

The fixture exposes these GraphQL fields:

- `Note.owner: String!`, `enabled: Boolean!`, `amount: Decimal!`, and
  `payload: String!`; hidden primary key `demo.id` is a required string.
- `Task.taskValue: String!`; hidden primary key `demo.taskId` is a required
  string. The original storage column for `taskValue` is `task_value`.
- `Query.notes`, `Query.tasks`, `Query.node`, and `Query.nodes`.

It does not claim native Host execution, browser execution, deployment, external
trust issuance, or a production identity source. The included prepared trust
reference is a task-local artifact pin for build/runtime admission tests.

## Provenance and selected packages

The final upstream fixture is under
`/private/tmp/batten-profile7-native-20261105/umf-rich-source-final/`. Exact
source UMF bytes have SHA-256
`76d0ecb0697900a0ed3ec8170f21dedc414349e0d38c40ecedaf8bfdefb8d7f7`. The
installation reference records digest `e12879e7944f3bfc9f8dba6238b4d551a091414bbae3c0e3cdb09820c6636ab5`
and head `53ad0c237af26b8ffcd79e70c66b7bbbbe11e84a0f3f2c3cd8e2317a15b777a5`.
The corrected artifact manifest SHA is
`325bdfed4db8d8b5b15912fed70c3ae6b66d7cf0152d59a2a54869b4b033a90a`, its
artifact digest is
`ac137c89d2b30ba26a09e183140bba01f7301499efa0fb11926c47e220ec53cb`, and its
local receipt digest is
`327afbccd4287fa5ce52c2090833e42d29ffcb9f6543b949a2b18b789142bb2e`.

The corrected provenance file is preserved beside this README. Its defined
Codegen package inventory SHA is
`8c01f37b5b28a17cacf632cbb6f0cd83a1c99120f3d1926924be2396f9664fdb`; the
Weft build-source inventory SHA is
`b0655f857be2aa81754cc549917b1f90dd9b63f5ed59b998a6802104558592e7`. Those
inventory definitions cover package payloads and declared build-source scopes,
not the full upstream repositories. Weft is 0.4.66.dev1; its wheel SHA is
`1214a26beb73b351dcf7c684baf0465562e512798afe5138dce39d5ac1588660`.

The builder used CPython 3.11.17 in
`/private/tmp/lintel-api4-a5-a4-ex9-recheck-20261105/env`, Lintel API runtime
a5 wheel SHA
`e90e5109d219c70c1a8f796572531d849f80705e7a23316923aa2d7f7e169aae`, build
a4 wheel SHA
`4bd311e67bece28123746ee5e6f750d5912bee6c6baee7b3d415ce97814ccfcb`, and
updated executor a9 wheel SHA
`ee5e63e01b1d48518645467cb64749622da574a1feff51dd7a281e8d25d863a2`. The
builder probe blocked UMF runtime imports and Weft imports. Runtime admission
loaded the emitted artifact via Lintel's public `load_prepared_api` API.

## Prepared API

- Artifact: `tests/fixtures/prepared-api-v4-rich-weft7-proof.json`
- Trust reference: `tests/fixtures/prepared-api-v4-rich-weft7-trust.json`
- Artifact SHA-256:
  `f13945c7e8fcb1b981a8c3d3a2977c3f85589825373e3992d8481ec371f5d084`
- API digest:
  `86281b7304b6bdbd64c15a858d72187bc2615696a4bbc50934294975761de59b`
- Schema digest:
  `73a79839011d5d249ef399b51a431d475fa8bb4e22befd33597feaabf122aa3c`
- All prepared generated connection rows are exactly
  `weft.generated-read-algebra/7`.
- `prepare_api_v3` refuses the same fixture with `UNSUPPORTED` at
  `generated read algebra profile`.
- Note allowed-field profile: `demo.owner` string, `demo.enabled` boolean,
  `demo.amount` decimal with native `numeric(8,2)` / OID 1700, and
  `demo.payload` string; hidden Key `demo.id` string.
- Task allowed-field profile: `demo.taskValue` string; hidden Key
  `demo.taskId` string.

The schema bytes are in `schema.graphql`; their hash equals `schemaDigest`.
`exposure.json` is the exact canonical `/3` exposure bytes stored in the
prepared artifact.

## Relay compiler output

Relay Compiler 21.0.1 compiled against this exact API4 SDL using Bun 1.4.3 and
TypeScript 6.0.3. The generated operation set contains:

- `RichCollectionsQuery` for the Note and Task connections together.
- `RichNotesPaginationQuery` and `RichTasksPaginationQuery`, generated from
  `@refetchable` connection fragments.
- `RichNodeLookupQuery` and `RichNodesLookupQuery` for the prepared global ID
  roots.

The TypeScript mapping uses branded `DecimalString`. Generated wire operation
text has no Relay-only `@connection`, `@refetchable`, `@argumentDefinitions`, or
`@arguments` directives. `relay-client/client-manifest.json` validates against
the governed `lintel.client/1` schema; it includes the exact API and SDL digests,
all 12 owned schema/source/compiler artifacts, and five operation entries. Its
SHA-256 is
`01abebabb36e527200452f88b6eeda4ec51083bc6c2980e40b08d5e904bda038`.

The Relay compiler output was generated in a temporary build directory and
copied unchanged here. The client-manifest assembly is a task-local recipe
following CONTRACT-004; the repository does not yet expose a general client
artifact build command. The Relay output establishes compilation only and is
not a browser or Host behavior qualification.

## Evidence files

`issue-rich-api4.py.txt` and its stdout preserve builder admission and runtime
loading. `relay-compile.stdout.txt` preserves the compiler run. The local
provenance JSON and `relay-client/` preserve the source inventory, exact SDL,
authored operation document, Relay config, generated TypeScript artifacts, and
client manifest. No database was accessed or changed by this Lintel build.
