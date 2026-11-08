---
ddx:
  id: CONTRACT-002
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-002
      kind: informed_by
    - id: FEAT-003
      kind: informed_by
    - id: FEAT-005
      kind: informed_by
    - id: lintel.architecture
      kind: informed_by
---

# CONTRACT-002: Neutral asynchronous execution boundary

**Type**: Python library protocol. **Version**: `lintel.execution/1` target.

## Purpose

Let a host execute admitted Lintel requests without importing Batten into Lintel
or exposing a native provider, connection or authorization implementation.

## Scope and Boundaries

The normative Python surface is [ports.pyi](../interfaces/ports.pyi). It is a
specification artifact, not an implemented package. Lintel owns the protocol;
Batten owns its consumer adapter in Batten. Existing runtime APIs are not claimed
to implement these signatures. U/R/B changes and S-01–04 qualification still apply.

## Normative Surface

All I/O methods MUST be asynchronous. Factories/capability snapshots/Node codecs
are pure synchronous operations. Public import destination is `lintel.ports`.
Only immutable/copied values cross it. No native driver, Strawberry, FastAPI or
Batten type appears. `CoreLiteral` denotes the existing upstream `null` or exact
tagged literal meaning; this protocol never interprets an unknown
scalar/extension itself.

| Value / method | Required behavior |
| --- | --- |
| `OperationRef` | Exact declared module/ID/profile kind; no arbitrary query, SQL or client-authored effects. `/2` adds `kind=record` for a source Record root proven by CONTRACT-006's generated artifact; it is not a table/action command. |
| `NodeKey` | Exact Record/Key identity and authored ordered scalar components; no display-name lookup. |
| `NodeValue` | Exactly requested qualified selected Fields plus internal key; unknown/unrequested data never becomes a GraphQL property. |
| `RequestScope.authority` | Host-authenticated opaque handle, validated by the adapter; cannot be supplied by application variables or tracing headers. |
| `get_many` | Preserve order, duplicates and missing/denied slots; output length equals input length. Wrong returned type/key refuses the whole affected call. |
| `related_many` | One slot per parent; no target or denied target yields None with no distinguishable existence detail. Must enforce parent and target visibility. |
| `connection` | Enforce policy before slicing. Return at most first authorized edges, each with its own valid continuation cursor; exact previous/next evidence, including empty pages. |
| `invoke` | Recheck current capability, authorization and confirmation; apply only the declared command under upstream atomicity. |
| `observe` | Never execute a command. Recheck observation authority and bind original operation, arguments and invocation key. |

Required capability pairs for selected uses: `lintel.execution=1`,
`node.refetch=1`, a nonempty host-qualified `identity.codec` profile,
`read.consistency=request-snapshot-1`,
`connection.forward=edge-cursor-1`, `relationship.batch=to-one-1`,
`command.outcome=1`, `command.observe=1`. Unused command/relationship/connection
pairs need not be provided. Every selected capability must name its qualified
binding profile under `binding.profile`; the snapshot also includes all effective
`limit.*` values as decimal strings. Unknown applicable versions refuse activation;
a capability declaration alone is not evidence that its implementation passes.

Arguments are keyed by authored parameter ID and contain upstream exact scalar
literals or NodeKey for an explicitly declared entity/key parameter. Arbitrary
JSON objects are not accepted. A string-valued parameter that happens to look
like an ID is not automatically a Node reference. The host adapter lowers typed
keys through the qualified upstream binding, not a Lintel-built query. Omitted
parameters remain absent from the mapping; explicit null is the upstream
literal `null` (`None` on this Python port), distinct from an omitted parameter
key. No synthetic null wrapper is introduced. Unsupported structured/container
arguments refuse in this profile.

### Request sessions and consistency

RequestScope.kind is supplied from the validated GraphQL operation, not a user
authority claim. Query sessions MUST reject invoke; mutation sessions use separate
authoritative command transactions per root field. Native acquisition may be lazy;
opening a session does not start a write or commit an outer transaction.

The async context manager creates request-owned execution/caches, validates
source/current installed reference and releases owned leases on exit. It MUST
NOT close or reconfigure a borrowed provider/pool. No request session is reused
across actor, app or API digest. The host supplies finite monotonic deadline and
resource limits. Cancellation propagates after cleanup.

For a read operation all returned instances of the same Node must agree on shared
selected fields, including fragments/aliases and related/refetch paths under
concurrency. `request-snapshot-1` requires one consistent native read view plus
request-local object materialization. An adapter unable to supply that guarantee
MUST refuse the selected profile; per-call transactions alone do not qualify it.
Current host authority is checked on each dispatch. Access revocation must not
turn a previously materialized object into a grant on another invocation.
There is no cross-page snapshot guarantee: later GraphQL operations open new views.

Related lookups group by admitted operation/target and deduplicate keys only within
a request. Chunk size is at most 100 and may be tightened. With 50 parents and
one selected to-one relationship, the native call bound is one root read plus
one related batch for a profile able to handle 50 keys. No N-per-parent loop is a
fallback. A batch mismatch, unsupported shape or bound overflow refuses explicitly.

### Cursors and Node codecs

The runtime owns connection cursor authentication, scope and native position.
Each cursor binds app/API/authority scope, operation/arguments/order and exact
last-edge position. Tampering, stale/foreign scope or incompatible source returns
`INVALID_CURSOR`; a missing row at an otherwise valid position follows the
qualified live keyset profile. Lintel never manufactures offsets or relabels a
page-next token as every edge's cursor.

NodeCodec.profile() MUST match the identity.codec capability captured by the
prepared API; create_router refuses a mismatch. Codec/key rotation must retain
existing identity or perform an explicit namespace/version migration, not silently
change IDs. The profile is public metadata, never a hash/exposure of secret keys.

The host supplies a pure NodeCodec satisfying stable encode/decode for exact keys,
namespace, Record and Key version. IDs contain no secret material. An opaque ID
is not a grant; successful decode always goes through current authorized lookup.
Keys/types not in the prepared exposure are treated as unavailable. Renaming an
API type cannot change native key semantics; namespace/key version changes require
explicit client migration. Never include mutable source digests in every ID.

The portable `lintel.node-id.string-key/1` codec is the first concrete profile.
It encodes canonical UTF-8 JSON `[profile, namespace, module, record, keyId,
[componentStrings...]]` as unpadded base64url. Namespace and qualified references
are nonempty exact strings; there are 1–16 nonnull UMF `{string: ...}` Key
components. Input and output are each bounded to 2048 bytes, and decoding requires
the canonical alphabet, base64url round trip, exact JSON shape and canonical JSON
bytes. NUL is refused because the selected PostgreSQL text Key carrier cannot
represent it; other well-formed UTF-8 including line breaks is preserved. This
codec only transports lookup identity. `/2` build admission selects it
only when every original primary-Key Field is required `string`; other carriers
remain unsupported until UMF defines a canonical identity codec for them.

For `/2`, host composition injects a validator for every prepared Record/Key
pair. Each validator closes over that root's already admitted generated executor
and calls its pure issued `validate_get_many_key` API before a `NodeKey` can enter
batch dispatch. The validator registry carries and must exactly match the
prepared root's source, artifact, receipt, target binding, algebra and Key pins;
missing or extra entries refuse router construction. This check uses the same
issued codec as `get_many`, without opening a session or issuing SQL. It rejects
facet-invalid IDs as individual null slots so they cannot poison other valid IDs
in a GraphQL `nodes` batch. Lintel runtime performs no UMF source or facet parsing.

### Command results

`applied`: receipt and returned affected IDs; durability may be committed or
pending-caller-commit. `recovered`: authenticated existing receipt; no invented
historical business rows. `not-observed`: observation only, not proof that a still
running attempt cannot commit; durability unknown. `unknown`: dispatched command
commitment cannot be established. `rejected`: known pre-effect refusal, durability
none, no receipt/effects. `code` and `confirmation` are safe, optional host outcome
metadata; challenges confer no authority. Invalid combinations MUST refuse.

The adapter preserves caller transaction ownership and never commits the caller's
outer transaction. Lost response/cancellation after dispatch MUST NOT imply rollback.
No method or cleanup path automatically retries a mutation. Observing an occupied
key with changed arguments must refuse rather than execute another command.

## Precedence and Compatibility

Upstream native semantics and Batten host gates precede this adaptation. A
selected profile may impose stronger guarantees; it cannot erase weaker native
limits. Every semantic protocol/profile change is independently versioned.
This is a target contract, not an amendment silently applied to upstream APIs.

## Error Semantics

`ExecutionError.code` is one of INVALID, DENIED, CONFLICT, PRECONDITION_FAILED,
CONFIRMATION_REQUIRED, UNSUPPORTED, API_MISMATCH, INVALID_CURSOR, TOO_MANY_ROWS,
LIMIT_EXCEEDED, BUSY, NOT_YET_CURRENT. Messages are fixed code strings; raw native
exceptions remain host-private. Query errors cannot be converted into empty pages.
Dispatched command uncertainty becomes CommandResult unknown when a safe response
can be returned; loss of the entire HTTP response is handled by CONTRACT-004.

## Examples

Fifty Task keys containing duplicates return fifty get_many slots. A hidden Person
returns None, including when reached from a visible Task. Replaying completeTask
with its original key observes the upstream effect receipt, without another write.
A prepared next-page-only driver refuses `edge-cursor-1` at activation.

## Schema Basis

Reuse core 0.10 exact references, Keys/literals and existing table/action operation
identity. The prepared API `/2` Record-root binding adds the versioned
`OperationRef.kind=record` read identity; it does not change the `get_many`
signature or make a source Record a command. Native cursor and outcome meaning
stays runtime-owned. The local Python protocol introduces transport-neutral immutable views and opaque host authority,
not storage/model rules. No JSON schema is claimed to validate a Python authority
handle. The pinned task-board logical model and CONTRACT-001 identify source reuse.
