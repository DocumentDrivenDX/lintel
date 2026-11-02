---
ddx:
  id: CONTRACT-003
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-002
      kind: informed_by
    - id: FEAT-003
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
---

# CONTRACT-003: GraphQL and Relay server profile

**Type**: GraphQL schema and execution. **Version**: `lintel.graphql/1` target.

## Purpose

Define the bounded server/client-visible behavior of a schema projected by
CONTRACT-001 and executed through CONTRACT-002.

## Scope and Boundaries

MVP: one application per mounted endpoint, keyed Nodes, root forward connections,
one-hop optional/to-one relationships and declared commands with observation.
No arbitrary query language, subscriptions, federation, uploads, incremental
responses, automatic CRUD or backward paging. GraphQL language/execution reference
is September 2025; Relay identification/connections references are linked below.
This selected profile is not a claim of full standard/toolchain conformance.

## Normative Surface

The [task-board SDL](../examples/task-board.graphql) is the concrete example's
shape authority. It is illustrative output, not a handwritten schema to maintain
per application. Host operation metadata and exposure generate equivalent shapes.
Native SDL is linked directly; it is not relabeled as a UMF browser schema.

### Nodes, visibility and field stability

Every exposed keyed type implements exactly `Node { id: ID! }`. The root has
`node(id: ID!): Node` and `nodes(ids: [ID!]!): [Node]!`. Plural lookup preserves
order, duplicates and null slots. Missing/denied/foreign-scope/unknown-type IDs
return null without per-ID errors or existence distinctions. Malformed IDs follow
the same unavailable outcome; global input-size violations still fail validation.
Node IDs are opaque host codec results. They never authorize access.

A query uses CONTRACT-002 request-snapshot-1. Two appearances of an available Node
must agree on shared selected fields. Host authorization precedes every data
read, including refetch and relationship paths; a visible edge is not a grant.
GraphQL types are fixed for an admitted app, not rebuilt per actor. Introspection
requires host permission to access that app's API metadata; it does not grant data.

A missing/hidden to-one target yields null. Relationship fields are nullable even
when native integrity says a target exists, unless the host separately qualifies
non-null visibility. Missing required scalar output is an execution failure, never
invented null/coercion. The engine's normal non-null propagation applies and the
safe error code identifies a failed field without disclosing native data.

### Connections

A root connection exposes `first: Int = 25` and `after: String`; no last/before.
Valid first is 0–100 subject to tighter host limits. An omitted first uses the
prepared default; explicit null or a negative value is INVALID, and a value above
the effective ceiling is LIMIT_EXCEEDED, before provider dispatch. Each edge has a non-null cursor
and available node; PageInfo has both direction booleans and nullable start/end
cursors. Empty edge lists return null start/end, including first=0. Runtime probing
still supplies correct next/previous flags; first=0 is not an invented empty dataset.

Ordering is fixed by the declared operation, with exact stable key tie-breaks.
Filtering/order arguments exist only if declared and qualified upstream. There is
no totalCount by default. Every returned edge cursor resumes strictly after that
edge under the same scoped arguments/order; start/end match first/last edges.
Both booleans are exact visible-order facts required by this selected profile.
If their determination exceeds the qualified budget, refuse rather than guess.
The same request is snapshot-consistent; later pages are live new requests and
may see inserts/deletes. No cross-page snapshot is promised.

Expansion follows the explicit relationship mapping and upstream batch loader.
Aliases/fragments cannot increase relationship depth beyond one hop. Results
never expose hidden related keys through cursors, counts or diagnostic text.

### Scalars, enums and presence

| UMF selected meaning | GraphQL / wire representation | TypeScript wire type |
| --- | --- | --- |
| string / boolean | String / Boolean | string / boolean |
| integer | BigInt custom scalar; exact base-10 JSON string | branded string |
| decimal | Decimal custom scalar; exact finite JSON numeric-token string | branded string |
| UUID | UUID custom scalar; validated UUID text under the chosen codec | branded string |
| date / exact instant | Date / ExactTimestamp custom scalar; exact qualified lexical text | branded string |
| opaque128/binary | Only separately qualified hex/text scalar codec; otherwise refuse | no implicit number conversion |
| floating/native/container forms | Outside MVP unless an independently qualified exact codec is selected | no fallback to Float/JSON |

BigInt accepts `-?(0|[1-9][0-9]*)`; Decimal accepts finite JSON-number lexical syntax
inside a JSON string. Strings are retained without parsing through float or JS
number. Native scale/width/domain restrictions remain enforced upstream. Literal
and variable coercion apply the same rule. Unsupported precision/temporal meaning
refuses. Vocabulary references are metadata unless qualified enforcement exists.
For authored finite string sets, the MVP uses identity-named GraphQL enum values
only when every original value is a valid non-reserved enum name; no case folding
or punctuation replacement. Invalid/colliding enum names refuse. Boolean/integer/
decimal domains retain their exact scalar carriers and upstream membership
validation rather than changing primitive values into GraphQL enum names.
The enum type name is exposed Record typeName + upperFirst(field API name) + Enum;
upperFirst uppercases only an initial ASCII lowercase character. Generated type
collisions refuse. This conversion does not confer any ontology/vocabulary meaning.

GraphQL omitted input, explicit null and supplied value remain distinct. There
are no client/server defaults unless the operation declares them; generated
GraphQL arguments MUST NOT evaluate native defaults itself. Defaults in server
pagination are protocol controls, not native business defaults. Explicit unsetting
requires an upstream-declared parameter/effect; null is not a universal unset.

An absent-allowed output Field projects to a generated per-carrier Presence object
with `state: PresenceState!` and nullable `value`; ABSENT/NULL require no value,
VALUE requires one. This explicit wrapper prevents absence collapsing into null.
If the runtime cannot distinguish states, that selected Field refuses activation.
The example has only required scalar outputs, so no wrapper appears in its SDL.

### Commands, confirmation and recovery

Generate one mutation per explicitly selected command and one read-only
`observe<Name>` root (prefix observe and apply upperFirst to the
selected mutation name; all generated collisions refuse) for commands with qualified outcome observation. The MVP selects only commands with qualified effect observation; a supplied key
alone is not evidence of replay/recovery. Input type names are upperFirst(mutation
API name) + Input, and observation types are Observe + that name. Native parameter
IDs are input field names unchanged; invalid/reserved/colliding names refuse
until a versioned override profile exists. Labels never select argument identity.
Inputs
come from declared parameters. An explicitly typed entity/key parameter maps
to ID and is decoded to the corresponding qualified NodeKey; plain scalar strings
never acquire entity semantics by naming convention. Add `invocationKey: ID!` and optional
`confirmation: String`. The caller creates/retains the key before dispatch.
Confirmation is an opaque host challenge/response reference, never a client grant.
Observation uses a separate generated input type with the original declared
arguments and invocationKey, excluding confirmation: observing cannot approve or
reissue a command. Protocol controls never enter the native argument digest.
Inputs named like protocol controls require explicit upstream/projection resolution;
no collision is silently renamed. Name mapping and reserved generated names are
checked across the whole schema.

CommandOutcome variants follow the example SDL. Applied carries effect IDs and
a safe receipt, Recovered carries receipt/durability without business rows,
Unknown preserves the key and commitment uncertainty, Rejected names a fixed code
and optional host challenge. Observation returns only Recovered, NotObserved or
Rejected, never applies an unobserved command. NotObserved is not a future no-commit
guarantee. Output durability preserves caller-owned pending commits.

Mutations never return mutable Node snapshots in this first profile. Clients
refetch after a confirmed durable outcome; affected IDs support invalidation.
Multiple top-level mutation fields execute under GraphQL's serial root rule,
retain independent commit outcomes and never imply one transaction. Each field
gets its own command context; query caches are not reused across commands. Later
fields cannot treat an earlier receipt as permission. A host may refuse a command
requiring unimplemented multi-operation atomicity before its effects.

## Precedence and Compatibility

GraphQL engine coercion/execution and this selected stronger profile compose;
UMF/host meaning cannot be weakened. CONTRACT-001 governs naming and identity;
CONTRACT-002 governs native facts. Scalar codec/Node namespace/operation changes
need explicit cohort compatibility assessment even when SDL is unchanged.
Custom scalars require both runtime codecs and client mappings; types alone prove neither.

## Error Semantics

Unexpected read/field failures use normal GraphQL `errors`, null propagation and
safe `extensions.code` from CONTRACT-002. Expected command refusals use the typed
Rejected result, not a second command error protocol. Invalid syntax/variables
are pre-execution failures. Lost transport after mutation dispatch becomes client
uncertainty, never a fabricated Rejected result. No automatic mutation retry.

## Examples

[Operations](../examples/task-board.operations.graphql) show list/refetch/complete/
observe. [Relay documents](../examples/task-board.relay.graphql) show compiler-only
connection/refetchable directives. Run the Relay compiler before sending wire
operations; the server does not interpret those client directives.

## Schema Basis

Reuse current UMF 0.10 logical meanings and declared operation metadata. The local
SDL adds protocol Node/connection/outcome/presence types without changing core.
The pinned logical example intentionally lacks physical/command declarations;
[host obligations](../examples/README.md) distinguish desired shapes from delivery.

## Non-Normative Notes

Standards: [GraphQL September 2025](https://spec.graphql.org/September2025/),
[Relay identification](https://relay.dev/graphql/objectidentification.htm) and
[connections](https://relay.dev/graphql/connections.htm). Lintel's exact backward
availability booleans and finite forward profile are explicit design choices;
passing SDL validation does not qualify these runtime properties.
