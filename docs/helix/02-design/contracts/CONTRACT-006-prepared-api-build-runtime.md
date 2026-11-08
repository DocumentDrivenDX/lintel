---
ddx:
  id: CONTRACT-006
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: CONTRACT-001
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
    - id: CONTRACT-005
      kind: informed_by
    - id: SD-002
      kind: informed_by
  schemas:
    - id: lintel.prepared-api
      version: "1"
      title: Build-issued prepared API inventory
      path: docs/helix/02-design/schemas/prepared-api.schema.json
      schemaFormat: json-schema
    - id: lintel.prepared-api
      version: "2"
      title: Build-issued generated Record-root API inventory
      path: docs/helix/02-design/schemas/prepared-api-v2.schema.json
      schemaFormat: json-schema
    - id: lintel.exposure
      version: "2"
      title: Generated Record-root exposure selection
      path: docs/helix/02-design/schemas/exposure-v2.schema.json
      schemaFormat: json-schema
---

# CONTRACT-006: Prepared API build and runtime admission

**Version:** `lintel.prepared-api/1`. This contract defines a build artifact,
not a second UMF model or a native execution program.

## Boundary

`lintel-api-build` owns `lintel_build.prepare_api`. Its dependency closure may
contain `umf-core` and source validators. It takes exact original UMF source and
dependency bytes, explicit exposure bytes, and host-qualified capability,
binding, scalar codec and limit facts. It validates the selected meaning through
the public UMF validator, resolves all selected Record/Field/Key/operation
references, and emits deterministic SDL and one canonical
`lintel.prepared-api/1` file. It preserves original source and unknown unselected
content. Unknown selected meaning refuses. The build issuer never supplies an
actor or provider authority.

`lintel-api` owns `lintel.projection.load_prepared_api` and
`lintel.graphql.create_router`. Its ordinary dependency closure and import graph
exclude `umf-core`, UMF source parsing, Weft, UMF codegen, a generator CLI and a
remote compiler client. Runtime GraphQL document parsing and execution are
allowed. `lintel.experimental` remains an explicit spike or optional extra and
is not imported by production modules. A source-first UMF upload may run the
build issuer separately and readmit the resulting bytes; production routing
never falls back to that issuer.

The [closed inventory schema](../schemas/prepared-api.schema.json) fixes exact
members. It contains canonical exposure bytes as base64, sorted exact source
identity/digest pairs, sorted capability/host-limit pairs, one explicit scalar
codec profile, closed selected Record/Key/Field/lookup mappings, SDL,
`schemaDigest`, `apiDigest`, and `artifactDigest`. `schemaDigest` hashes exact
UTF-8 SDL bytes. `apiDigest` uses CONTRACT-001's length-framed preimage:
domain, exact exposure bytes, sorted source identity/digest frames, canonical
capability profile including all effective limits, scalar codec profile, and
SDL. `artifactDigest` hashes canonical JSON with that member omitted. Canonical
JSON is UTF-8, sorted object keys, compact separators, exact integers and no
NaN/Infinity; duplicate keys, noncanonical bytes and unknown members refuse.
The source/exposure bytes and dependency digests are build input evidence, not
runtime permission.

The host supplies an independently trusted `TrustedPreparedRef` from a verified
package inventory and receipt. It pins the exact prepared file SHA-256,
`artifactDigest`, application, `apiDigest`, exposure SHA-256, source closure,
capability/binding/scalar profiles, and effective limits. Runtime admission
compares every pin, recomputes artifact/schema/API digests from stored bytes,
checks the record map against the deterministic SDL, and returns an immutable
nominal `AdmittedPreparedApi`. A caller-created dict or `PreparedApi` dataclass
is not admission evidence. `create_router` accepts only that admitted value and
rechecks `ExecutionPort.capabilities()` and `NodeCodec.profile()` against its
host pins at mount. No request input can select a source, binding, operation,
identity namespace or scope authority.

The initially qualified subset is keyed Node refetch with exact required
scalar Fields and one selected Key. Connections, related reads, commands,
request snapshot and Relay capabilities activate only when each selected
operation/profile has independent native and Host evidence. A generic fake-port
GraphQL test proves schema mechanics, not a Batten/native capability. The Lintel
router refuses an absent or unknown selected profile before serving traffic.

The runtime wheel and build wheel have disjoint file ownership. The build
distribution uses its own `lintel_build` import namespace and depends on the
exact runtime candidate. Building both wheel and sdist, installing the runtime
wheel alone in an isolated interpreter, and blocking `umf`/build imports during
router construction and a real ASGI request are required packaging gates. No
historical `lintel-api 0.1.0a1` wheel is overwritten; new candidate versions
and host receipt identity remain to be qualified.

## Additive generated Record-root profile

`lintel.exposure/2` and `lintel.prepared-api/2` add a qualified Record root to
the existing keyed Node shape. A `/2` Record's `lookup` is exactly
`{module:<source Record module>,id:<source Record ID>,kind:"record"}`. It does
not assert an UMF source table/action command. `/1` artifacts and their
table/action references remain byte-compatible and do not acquire a Record
route by changing a string. The `/2` structural envelope is
[prepared-api-v2.schema.json](../schemas/prepared-api-v2.schema.json).
The [exposure `/2` schema](../schemas/exposure-v2.schema.json) retains the
same closed top-level keys as `/1`: `format`, `application`,
`identityNamespace`, `records`, `connections`, `mutations`. Only `format`
becomes `lintel.exposure/2`; each selected Record retains exactly
`record`, `key`, `typeName`, `lookup`, `fields`, `relationships`. The first
`/2` cut requires nonempty `records`, exact `record` lookup kind and identity,
and empty `relationships`, `connections` and `mutations`; it does not imply
Relay connection or command support.

The build-only `prepare_api_v2` accepts the `/1` source, dependency, exposure,
capability, host and scalar inputs plus exact `GeneratedManifest`,
`GeneratedFiles`, `TrustedArtifactRef` and `TargetBinding` values from UMF's
generated executor package. It calls
`prepare_generated(manifest, files, trusted, target)` and requires the
verifier-issued executor's `read_profile` to be
`weft.generated-read-algebra/4`. It compares original UMF source bytes to the
manifest/trusted source SHA-256, and resolves each exposed Record, primary Key,
ordered Key Fields and selected Fields against both original UMF source and
the issued algebra root/native catalog. No caller-created root mapping or
capability string is proof. The build package may depend on UMF source and
generated-executor libraries; ordinary `lintel-api` may not.

Each `/2` artifact adds sorted, duplicate-free `generatedRoots` entries with
exact members `{lookup,sourceDigest,artifactDigest,receiptDigest,bindingDigest,
algebraSha256,primaryKeyId}`. `lookup` is the `record` reference above;
`sourceDigest` matches the original UMF source and admitted native projection,
`artifactDigest` and `receiptDigest` come from the independently trusted UMF
artifact reference, `bindingDigest` matches the admitted target, and
`algebraSha256` hashes exact inventoried `algebra/read.json` bytes. The
`primaryKeyId` is the original source Key ID issued in that algebra root.
Selected Field and Key codec identities remain in the existing closed Record
mapping and must join the same root. This first runtime cut supports only the
already qualified `string`, `boolean` and `decimal` scalar codecs; integer,
UUID, date and timestamp mappings require a later scalar codec profile and are
not accepted by this schema version. A `/2` `TrustedPreparedRef` additionally
pins `generated_roots_sha256`, the SHA-256 of canonical `generatedRoots` JSON
bytes; it is absent for `/1`. Runtime admission checks that pin and the exact
`record` lookup/Record map join without loading UMF source or Weft.

The `/2` API digest uses the same length-framed algorithm as `/1`, changing
the domain to `lintel.api/2` and inserting canonical `generatedRoots` JSON
after the scalar codec profile and before SDL. The `/1` preimage remains
unchanged. A Host composition root independently joins each prepared root
pin to its already admitted UMF executor/receipt and configured Batten
Record-root route at mount. The capability key is
`operation.binding/<escaped module>/<escaped Record ID>/record`, where each
component uses JSON Pointer `~0`/`~1` escaping. The binding value equals the
host's selected `binding.profile`. The selected adapter advertises
`node.refetch=1` and `read.consistency=request-snapshot-1` only after native
two-lease request and ordered `get_many` evidence for its exact target driver.
An issued scope's `consistency` string alone supplies no capability.

The neutral `RequestSession.get_many`, `NodeValue`, GraphQL `node`/`nodes`,
opaque Node codec and per-request ASGI scope shapes do not change. The
`OperationRef.kind="record"` is an additive versioned value used only for
this qualified profile. Unknown kinds, unverified root pins, mismatched
source/binding/Key, absent snapshot capability or a fabricated source command
refuse before serving requests. Missing and denied rows remain
indistinguishable null slots, preserving key order and duplicates.

For this `/2` slice, `identity.codec` is exactly `lintel.node-id.string-key/1`.
The build issuer refuses an original primary Key containing any non-string or
nullable Field. Runtime admission checks the same pinned capability profile. The
codec transports qualified Record/Key routing identity only and never grants
authority; host authorization still gates every lookup.

Host composition supplies an exact per-Record/Key validator registry to the
runtime codec. Each callback is bound to the admitted generated executor's
`validate_get_many_key` method and the exact generated root pins; the set must
cover every prepared `/2` root with no extras. This shared issued-codec validator
ensures an invalid ID becomes a null slot before `get_many` batches the remaining
keys. A generated SDK model alone is not the validation oracle because its
validation parity with the issued native codec is not established.

The build issuer reads core Record/Field/Key meaning through UMF's public reader
and validator. It may continue when validation is otherwise valid but incomplete
solely because exact extension versions are unknown at the two qualified fixture
locations `/vocabularies/umf.tables` and `/vocabularies/umf.access`, leaving that
content opaque and retaining the exact source digest. Unknown extension paths,
errors and other incomplete states still refuse. Extension semantics do not
affect the generated-root join.

## Prepared API `/3` root connections

Lintel defines the closed `lintel.exposure/3` and
`lintel.prepared-api/3` formats for generated Record-root forward connections.
They do not change the admitted `/4` generated root, `lintel.prepared-api/2`
bytes or existing node/batch behavior. `/3` is build-issued only after joining
the matched Record exposure, strict Weft read algebra `/5`, verifier-issued
native connection profile and selected scalar codec. The native profile pins
`connection.forward=edge-cursor-1`; caller capabilities or SDL alone cannot
activate it.

Each `/3` `generatedConnections` row is closed to `{lookup, fieldRefs,
primaryKeyField, profile}`. `lookup` is the existing Record-kind `OperationRef`
and must join the exact generated Record root. `fieldRefs` is the sorted public
selectable Field set. The internal primary Key Field is separately pinned and
must also appear in the allowed profile. The profile closes
`connectionProfile`, `readProfile` and `allowedFieldProfile`; the latter carries
the canonical `umf.allowed-connection-fields/1` body and digest. Its output
descriptors preserve the verifier-issued native carrier, native type, OID and
nullability exactly. The API digest covers the connection rows and SDL but
does not include a self-referential digest field. `/3` requires at least one
declared eligible connection; `/2` serialization and admission remain
version-gated.

SDL uses the prepared Record type with `{Record}Edge`, `{Record}Connection`,
and shared `PageInfo` types. Name collisions with existing types, fields,
`PageInfo`, `*Edge`, or `*Connection` refuse preparation.

The selected `connection` port requires one authenticated cursor per returned
edge, keyed to app/API, actor authority, operation, arguments, order, source
and that edge's exact keyset position. `first=n` returns at most n authorized
edges and uses the issuer's bounded `n+1` lookahead plus an exact prior probe
for honest flags. `first=0` returns no edges but still probes both flags.
The byte guard includes all fetched rows and both probes execute on the held
request snapshot with current authority checks. A later GraphQL operation
opens a new snapshot and may observe changes; cross-page snapshot consistency
is not promised.

### Operation-wide connection preflight

Prepared API `/3` activates eligible root forward connections after `/5`
native qualification. It pins the eligible generated root, allowed Field
profile, issued operation and scalar codec joins independently of caller
input. It does not change prepared API `/2` bytes or existing Node/batch
behavior.

The first connection profile declares no filter or order arguments. Batten
maps the prepared Record lookup to its independently configured opaque Host
operation; Lintel artifacts carry no Host route IDs. Batten stages exact empty
`OperationCall.inputs`, with only `Selection.first`,
`Selection.after` and selected Fields carrying caller choices; UMF receives
`where=None` and the issued C-ascending Key order. A nonempty argument map
refuses before native leases. A future filter profile requires separate
closed argument admission and evidence.

After GraphQL parse, validation, operation selection, variable coercion and
budget checks, the router collects every root connection across aliases,
fragments and active directives. The collector uses the same effective
selection logic as resolvers and freezes each response key, issued operation,
coerced arguments, `first`, `after` and selected Fields. Conflicting calls for
one response key refuse. The first profile refuses nested or related
connections whose parent rows are unknown before execution. The optional `session_planned(scope, intents)` port takes that complete
immutable tuple. On context entry, Batten's Host invokes its selected
provider's pure preflight for every cursor before acquiring a native lease;
a missing planned-session port on a connection-capable API refuses before
any native lease.

The opaque plan is tied to the exact request scope and complete call tuple. A
planned session may serve `node`/`nodes` and all root connections on the same
held request snapshot. The first plan stages connection calls only; existing
validated Node/Key batches remain available through the ordinary selected
Host gate on that held request. Each connection resolver consumes only its
matching planned intent once; a changed argument, selection, response key or
replay refuses.
The neutral port carries the prepared root field name, alias/response key,
lookup, first/after and selected qualified Fields, but no native binding,
provider connection, SQL or compiler object. Batten translates staged intents into generic immutable
selected call specs and passes them through the public Host selected session.
The Host owns pure cursor authentication before opening the selected native
resource and retains per-call authority checks. An internal generated primary
Key Field used to form a Node ID or edge cursor must be present in the
independently admitted allowed Field profile and is not exposed as an
unselected GraphQL scalar. Public SDL type names and the `/3` schema are
defined by the separate closed schemas in `schemas/`; Lintel build/runtime,
upstream native and Batten qualification remain separate.

### Selected result and response accounting

Three byte checks have separate scopes. UMF's native frame guard remains
8 MiB per native result frame, including lookahead and probe rows. Batten's
adapter charges serialized selected outcomes from every `Node`/`getMany` and
connection dispatch against the one pinned `responseBytes` allowance, and
latches an overrun for the whole request. Lintel independently counts UTF-8
bytes while encoding the final GraphQL response and refuses before joining the
output or releasing the request session when the same pinned allowance is
exceeded. These checks bound native frames, retained selected outcomes and
final response bytes separately; they do not establish an 8 MiB peak-process-
memory bound.

## Proposed prepared API `/4` for combined read algebra `/7`

Prepared API `/3` records the outer Weft algebra profile in
`generatedConnections[].profile.readProfile`; its closed schema and runtime
require exactly `weft.generated-read-algebra/5`. An unchanged forward descriptor
inside a `/7` root does not make that outer artifact `/5`. A new explicit
`lintel_build.prepare_api_v4` accepts the existing `lintel.exposure/3` authored
selection, verifies one trusted combined `/7` UMF artifact and its eligible
forward descriptors, and emits `lintel.prepared-api/4`. The exposure format
needs no new version because it carries no Weft profile. Existing
`prepare_api_v3` and its default behavior, API `/2` and `/3` canonical bytes,
trust receipts and strict `/4`/`/5` joins remain unchanged.

Prepared `/4` has the same exact top-level members and `generatedConnections`
row structure as `/3`, but each `profile.readProfile` is exactly
`weft.generated-read-algebra/7`. Its new closed
`schemas/prepared-api-v4.schema.json` differs from the `/3` schema in the
prepared version and this profile constant. Build admission must obtain the
outer profile from the verified generated executor, match the inventoried
algebra and native/target/source/receipt pins, and recheck the existing
connection/Key/Field/native output/allowed-profile joins. It must refuse a
missing or unsupported forward descriptor, a `/5`-labeled `/7` artifact, a
`/7`-labeled `/5` artifact, mixed profile rows and unsupported roots. It does
not expose ordinary Page as GraphQL or add filter/order arguments.

API `/4` uses the existing canonical artifact and trust-reference shapes with
new `lintel.api/4` digest framing over the exact exposure bytes, source and
capability pairs, host limits, scalar profile, generated roots, generated
connection rows and SDL. Its `apiDigest`, `artifactDigest`, artifact SHA,
`generatedConnectionsSha256` and `generatedRootsSha256` must be recomputed;
there is no borrowed `/3` digest. Runtime admission registers `/4` alongside
`/1`–`/3`, requires the exact `/4` schema and `/7` readProfile, verifies
canonical bytes, digest/trust pins and generated metadata, and renders the
same connection SDL from those rows. `StringKeyNodeCodec` retains
`lintel.node-id.string-key/1` and gains `/4` as an admitted prepared version
with the same exact generated-root validator coverage. The GraphQL router,
preflight, resolvers and planned neutral `ConnectionIntent`/session ports admit
`/4` by version gate; their first=0, cursor, scalar, request snapshot, result
and response-byte semantics do not change. Runtime imports no UMF/Weft
compiler, SQL issuer, native driver or build package.

The TypeScript Relay client uses the `/4` SDL and newly derived `apiDigest` and
`schemaDigest` in the existing `lintel.client/1` manifest. That manifest has
no prepared-version member; adding one or changing generated operation
semantics is outside this slice. Acceptance includes `/2` and `/3` byte and
runtime regression, explicit v3-builder refusal of `/7`, v4-builder refusal of
`/5` or mislabeled rows, `/4` schema and trust mutation refusals, exact Node
codec registry, and installed compiler-free GraphQL/Relay first=0 and interior
connection proof over the same `/7` artifact and Host as ordinary SDK Page.
This is a proposed compatibility target until build/runtime/native evidence is
accepted; it is not a claim about the installed API `/3` cohort.
