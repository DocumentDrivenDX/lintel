---
ddx:
  id: CONTRACT-004
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-004
      kind: informed_by
    - id: FEAT-006
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
  schemas:
    - id: lintel.client-manifest
      version: "1"
      title: Relay client manifest
      path: docs/helix/02-design/schemas/client-manifest.schema.json
      schemaFormat: json-schema
---

# CONTRACT-004: TypeScript Relay client build and network boundary

**Type**: build/artifact/browser protocol. **Version**: `lintel.client/1` target.

## Purpose

Build typed operation/fragment artifacts against the exact API served by Lintel,
without a second client compiler or per-application dependency installation.

## Scope and Boundaries

Relay owns operation/fragment compilation, masking and normalized storage. Lintel
owns deterministic schema export, compiler/build integration, inventory/digests,
scalar wire helpers and the host-configured network boundary. Batten owns the
supplied compiler/runtime cohort and authenticated request transport. UI framework
selection is outside this contract. No Relay-compatible output is claimed until
the selected toolchain actually compiles the reference documents.

## Normative Surface

The [client manifest schema](../schemas/client-manifest.schema.json) owns artifact
inventory shape. It contains no credentials, live endpoints or actor identities.

### Inputs, outputs and integrity

Inputs are exact exported SDL bytes, the admitted API identity/profiles, UTF-8
GraphQL documents with unique operation/fragment names, a pinned Relay/TypeScript/
Bun toolchain, and a dedicated generated-output directory. Missing dependencies,
unknown directives or absent scalar mappings MUST fail before replacing output.
Build configuration cannot select code templates, run schema-supplied code, fetch
arbitrary URLs or install npm packages. The host/platform supplies all tools.

Output includes Relay-generated operation/fragment TypeScript artifacts, the
exact exported `schema.graphql`, selected source documents, generated scalar
mapping/import declarations and `manifest.json`. File paths are relative POSIX
paths within output; absolute/traversal/backslash/symlink and duplicate paths
refuse. Files are sorted lexicographically in the inventory. The manifest itself
is excluded from its own files list. Every other owned file is included with
SHA-256 of exact bytes. Every operation's artifact path must name an inventory
entry. `documentSha256` is exact original operation source file bytes; multiple
operations in one file may share that digest. Operation names remain unique.

`schemaDigest` and `apiDigest` come from CONTRACT-001. Exact tool versions, codec
profile and selected source closure are part of the platform qualification; a
version string does not by itself establish compatible artifacts. Changes to any
input invalidate check results. Compiler-only Relay directives are removed by
Relay; do not forward authoring documents unchanged to the endpoint.

Build stages a complete inventory and atomically replaces owned output. Existing
owned-file edits, unowned files, symlinks, conflicting concurrent build ownership
or restoration failure refuse safely. A failed replacement retains prior output
or a named recoverable backup. Check recomputes expected bytes read-only, reports
missing/extra/changed paths, and does not create locks/files in the output tree.
No timestamps, workstation paths or actor values enter deterministic output.

Library build operations are `build_client(inputs, output)` and
`check_client(inputs, output)` at the tooling boundary, with this behavior; exact
CLI flags are outside version 1 until the tooling spike selects a runner. This
is deliberately not a new query language, semantic compiler or package installer.

### Scalars and TypeScript values

The MVP uses string wire carriers for BigInt, Decimal, UUID, Date and
ExactTimestamp. Generated mappings import branded string aliases from the client
scalar helper; raw parsed numbers are never those types. `asBigIntString`,
`asDecimalString`, `asUUIDString`, `asDateString`, `asExactTimestampString` validate
supported lexical input and return the brand or fail. Helpers never round,
truncate, pick a timezone or evaluate domain/business constraints.

The selected compiler integration must supply operation-aware response scalar
validation before publishing data to Relay's Store. It rejects invalid wire types
or lexical values and preserves strings unchanged. How this metadata is obtained
from Relay's public compiler output is an explicit S-04 proof; importing private
compiler modules or implementing a parallel GraphQL compiler is forbidden.
A static custom-scalar type mapping alone does not satisfy this requirement.

### Browser network API

Target public entrypoint `lintel-client` exports
`createEnvironment({manifest, scopeId, execute})` and scalar helpers.
`execute` is a host-supplied async transport receiving GraphQL query text,
operation name, variables and the expected apiDigest; it returns an HTTP response
or throws a sanitized transport failure. It owns endpoint/credentials/CSRF and
trusted host authentication. No secret is embedded by generation. `scopeId` is
host-supplied cache context, not a credential; server authorization is independent.

The network sends only compiled executable operation text and includes
`X-Lintel-Api` with manifest apiDigest and Accept
application/graphql-response+json. A digest mismatch refuses before effects;
there is no transparent retry against a newer schema. Unsupported streaming,
uploadables, subscriptions or persisted-operation-only artifacts refuse rather
than changing transport semantics. GraphQL data+errors are retained as that protocol
requires; errors are never replaced by successful empty results.

The Environment/Store is bound to application, identity namespace, apiDigest and
scopeId. A login, impersonation or app/authority-context transition disposes the
old environment, cancels reads, discards old in-flight response writes and creates
a fresh store before rendering new-context data. No process-global RecordSource.
Node identity remains stable across compatible source changes; store migration
requires an explicit future policy, not silent reuse across a changed cohort.

For mutations the caller creates and retains invocationKey and exact original
arguments before invoking Relay. A post-dispatch transport error/timeout/abort is
reported as `MutationOutcomeUnknown` with original key, never as known rollback.
The client MUST NOT automatically retry, mint a replacement key or apply optimistic
success. Reconciliation calls the typed observation query under original current
authority. Recovered returns effect evidence; refetch obtains current business rows.
Pending-caller-commit is not durable success. NotObserved does not mean safe retry.
The host may resolve an uncertain outcome independently; no automatic browser loop
or privileged background job is introduced here.

## Precedence and Compatibility

Schema, manifest and runtime cohort must agree. TypeScript catches authored
operation mistakes; server validation/authorization remains mandatory for forged
requests. Exactly matching manifests are the conservative MVP admission policy;
additive compatibility analysis and live store migration are future features.
An unchanged SDL cannot override a changed binding/scalar/behavior profile.

## Error Semantics

| Condition | Outcome | Automatic retry | Recovery |
| --- | --- | --- | --- |
| Invalid operation/missing mapping | Build refusal; prior output retained | No | Fix document/profile |
| Generated output drift | Check failure with relative paths | No | Review/rebuild owned output |
| API mismatch | ClientSchemaMismatch | No | Admit new coherent artifacts |
| Invalid scalar response | ClientProtocolError; no affected store publish | No | Correct/qualify server/codec |
| Read transport failure | Sanitized read failure | No by default | Explicit caller decision |
| Mutation transport failure after dispatch | MutationOutcomeUnknown | Never | Observe original key/arguments |

## Examples

Compile [task-board.relay.graphql](../examples/task-board.relay.graphql) against
the exported SDL. The generated Task fragment must include masked typed data,
refetch operation and connection artifacts. The decimal `9007199254740993.01`
remains exactly that string in the response/store; callers can choose a separately
qualified decimal arithmetic library without changing the wire meaning.

## Schema Basis

Reuse CONTRACT-001 API identity and CONTRACT-003 GraphQL scalar/Node meanings.
The manifest is local build provenance; its JSON Schema does not validate server
semantics, authentication or Relay behavior. Native core source remains in UMF.

## Non-Normative Notes

Official [type emission](https://relay.dev/docs/guides/type-emission/) and
[network-layer](https://relay.dev/docs/guides/network-layer/) documentation inform
integration. S-04 selects and pins a compatible public compiler extension surface;
that interoperability uncertainty remains open without weakening the requirement.
