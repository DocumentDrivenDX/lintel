---
ddx:
  id: CONTRACT-005
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-005
      kind: informed_by
    - id: FEAT-006
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
    - id: CONTRACT-004
      kind: informed_by
  schemas:
    - id: lintel.host-profile
      version: "1"
      title: Bounded host profile
      path: docs/helix/02-design/schemas/host-profile.schema.json
      schemaFormat: json-schema
---

# CONTRACT-005: Hosting, lifecycle and bounded HTTP execution

**Type**: ASGI/library/configuration. **Version**: `lintel.host/1` target.

## Purpose

Mount one prepared GraphQL/Relay API without giving Lintel ownership of Batten's
identity, provider lifecycle, data deployment or platform dependency installation.

## Scope and Boundaries

FastAPI/ASGI hosting is in Lintel; Batten's optional consumer adapter remains in
Batten and implements CONTRACT-002. Pure Lintel projection/ports never import
Batten or web frameworks. Batten core/ASGI do not import/discover the optional
adapter. The embedding composition root wires both sides explicitly.

## Normative Surface

Authoritative configuration: [host-profile.schema.json](../schemas/host-profile.schema.json).
The [example](../examples/host-profile.json) defines explicit initial engineering
ceilings, not measured service capacity. Host policy may tighten any ceiling,
including disabling introspection; widening requires a new qualified profile.
All members are explicit. JSON Schema defaults are annotations, not an instruction
to silently inject native business defaults. defaultPage must not exceed maxPage;
relationshipBatch must not exceed maxLookup. Invalid combinations refuse preparation.

### Construction and lifecycle

Target library entrypoints:
`lintel.graphql.prepare_api(description, exposure, capabilities, host_profile)`
returns an immutable prepared artifact or safe preparation diagnostics;
`lintel.asgi.create_router(prepared, executor, node_codec, resolve_context)`
constructs a router after comparing the executor capability snapshot and Node
codec profile with the prepared artifact; `lintel.asgi.create_app(router, *, owned_closers=())` constructs
a standalone FastAPI app. Factories do no native I/O, dependency installation,
provider discovery or schema deployment. `description` must be a qualified
upstream public description under CONTRACT-001, not an arbitrary Python model.

`resolve_context` is an injected asynchronous host function for the ASGI request.
It returns the trusted CONTRACT-002 authority/application/request/deadline scope
or a host access refusal. Identity never comes from GraphQL arguments, Node IDs,
cursors or tracing context. Mounted application identity must equal prepared
identity; user-controlled route prefixes cannot select an unadmitted app.

Embedding hosts prepare providers before making the router ready. A borrowed
executor is never closed or globally changed by Lintel. Standalone owned_closers
are explicit async callbacks supplied only by composition; they run once, in
reverse order, after admission seals and active requests drain/cancel within the
configured deadline. A cleanup timeout is a reported incomplete shutdown, not
successful closure. Failure during preparation cannot publish a ready endpoint.
An embedded host owns its outer ASGI lifespan; mounting adds no competing lifecycle.

### HTTP profile

One host-configured mount (default example `/graphql`) supports POST only.
Content-Type is application/json; successful response representation is
application/graphql-response+json. Accept absent or */* selects that representation;
a client accepting only unsupported media receives 406. GET/other data methods
receive 405; OPTIONS/CORS and CSRF behavior are host-managed and never default to
credentialed wildcard access. No GraphiQL IDE, uploads or subscriptions in production
MVP. Native REST/OpenAPI data endpoints are not constructed.

Request body is one object with `query` string, optional `operationName` string or
null, optional `variables` object or null and optional `extensions` object. Null
variables means empty variables; no batch array. Unknown top-level members or
missing query refuse. Extensions are inert optional metadata and are never an
authority/dispatch channel. Persisted-operation-only requests are unsupported.

The host authenticates and authorizes API access before private schema details or
operations are exposed. `X-Lintel-Api` is required and equals the prepared apiDigest;
its absence/mismatch returns 412 with safe `API_MISMATCH` before effects. The header
is a compatibility check, not authentication. Syntax, variable, operation selection
and cost checks complete before any selected operation executes.

| Condition | HTTP status / GraphQL body |
| --- | --- |
| Invalid media / unacceptable response type / method | 415 / 406 / 405; no business dispatch |
| Unauthenticated / forbidden endpoint | 401 / 403 host-safe refusal |
| Invalid body, syntax, validation or variables | 400 with errors, no data |
| Pre-execution resource limit | 413 for byte limits; 400 for operation limits; safe LIMIT_EXCEEDED |
| API digest mismatch | 412 with errors, no data |
| Executed operation, including field errors or typed command refusal | 200 with GraphQL data/errors semantics |
| Unexpected failure before safe execution result | 500 sanitized; a dispatched mutation remains potentially committed |

The HTTP working draft informs transport behavior; this selected finite profile
is defined here and is not a claim of full draft conformance. Middleware must not
reinterpret an executed command result as a retryable network failure.

### Bounds and cost

Initial ceilings: first/default 100/25; plural lookup and related chunks 100;
relationship hops 1; depth 8; reachable field occurrences 256; aliases 32; cost
10,000; root mutation fields 4; in-flight provider dispatches 8; request 1 MiB;
response 8 MiB; query document 256 KiB; request execution deadline 30 seconds;
Node IDs 2,048 bytes; cursors 4,096 bytes; invocation keys 128 bytes.
These are bounded testable defaults, not latency/throughput SLOs.

Depth counts root selected field as one and each selected child as another,
including connection wrappers. Relationship hops count only source-to-target
Record traversals. Preflight traverses reachable fragments with GraphQL's normal
cycle/validation checks and accounts for every alias/repeated reachable occurrence;
it may conservatively overcount mutually exclusive branches. No ignored selection
can hide native work from budget enforcement.

Cost recursively assigns `cost(field)=1+multiplier*sum(cost(children))`.
Multiplier is max(1, resolved first) at a connection, max(1, number of IDs) at
plural Node lookup, otherwise 1. The connection multiplier is applied once at its
connection field, not again at edges/node. Scalar fields have no children and cost
one. Introspection uses known prepared-schema collection bounds instead of native
paging multipliers and stays under the same response/operation limits. Variables
are coerced before cost; over-limit cost rejects before provider calls.

Response construction is bounded. A read exceeding output budget returns a safe
failure rather than truncated success. For writes, the runtime must enforce its
result bound before commit where possible. If final HTTP serialization/transport
fails after dispatch, retain commitment uncertainty and original key; never label
it a pre-effect rejection. Deadlines/cancellation do not automatically roll back
already committed commands. No request monopolizes the event loop with synchronous
native work: qualified async adapters or host-owned scheduling preserve custody.

## Precedence and Compatibility

Host authentication/admission/current authority precede Lintel execution. Native
limits may be stricter. Effective profile values participate in apiDigest.
Unknown profile versions refuse rather than falling back. Runtime reload uses a
new prepared artifact/router with old admission drained; live schema mutation is
outside version 1. Databricks-specific trusted headers/config remain provider-owned.

## Error Semantics

Public errors contain fixed code and safe GraphQL location/path, never raw native
messages, variables, credentials, hidden identifiers or exception stacks. Auth and
compatibility failures execute no native business operation. Cleanup/cancellation
outcomes remain separately observable to the host. Dispatched mutation retry is
never automatic, including on 500, timeout, abort or exporter failure.

## Examples

Batten prepares its existing public host/providers and constructs its own
`batten.lintel` adapter, then supplies it to create_router. Lintel imports neither
that package nor raw providers. Shutting down one app releases its request sessions
but does not close the shared Batten executor used by another app.

## Schema Basis

The local host profile describes transport/resource policy, not UMF native data
semantics. It uses Draft 2020-12 as a small closed configuration schema. Original
UMF meanings and authority handles are retained through CONTRACT-001/002; no new
environment names or deployment/authorization language is introduced.

## Non-Normative Notes

Databricks Apps packaging must separately qualify interpreter, proxy/user vs app
identity, wheels and connectivity. A local ASGI check proves none of those.
Batten owns diagnostic transport and authoritative audit. Lintel propagates safe
application/API/request/operation identities and outcome codes; never variables,
Node/cursor/key contents or tokens. Trace context is correlation, not authority.
Exact OpenTelemetry package/convention pins and host mapping belong to the cohort
qualification; receiver/correlation/privacy/export-outage proof remains required.
This contract does not define a new log store, query API or diagnostic wire schema.
