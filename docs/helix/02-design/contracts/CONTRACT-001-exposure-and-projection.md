---
ddx:
  id: CONTRACT-001
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-001
      kind: informed_by
    - id: lintel.architecture
      kind: informed_by
  schemas:
    - id: lintel.exposure
      version: "1"
      title: Lintel explicit exposure profile
      path: docs/helix/02-design/schemas/exposure.schema.json
      schemaFormat: json-schema
    - id: lintel.task-board
      version: "0.10.0"
      title: Fabricated task-board logical model
      path: src/lintel/examples/task-board/task-board.umf.json
      schemaFormat: umf
---

# CONTRACT-001: Exposure and deterministic API projection

**Type**: configuration and library boundary. **Version**: `lintel.exposure/1`.
Target contract; no implemented compiler or upstream compatibility is asserted.

## Purpose

Select a GraphQL API from admitted Unified Modeling Fabric (UMF) declarations
without adding a second model, policy language or query compiler.

## Scope and Boundaries

Lintel owns API selection/naming. UMF owns meaning and constraint interpretation;
the trusted host supplies the admitted UMF JSON source/dependency closure and
qualified execution capabilities. Types, keys, relationships and declared
operations are read from UMF itself, using public UMF parsing/validation. No
intermediate schema-description service or alternate semantic model is required. Configuration cannot install a provider, select executable
Python, supply a role, or grant access. The JSON Schema owns configuration shape;
this Contract owns reference resolution and behavior.

## Normative Surface

Authoritative shape: [exposure.schema.json](../schemas/exposure.schema.json).
Concrete selection: [task-board.exposure.json](../examples/task-board.exposure.json).
All schema members are required, including empty arrays. Unknown members MUST
refuse this version; the original supplied bytes remain available to the host.

| Surface | Rule |
| --- | --- |
| `application` | Exact host-admitted application identity; never taken from GraphQL variables. |
| `identityNamespace` | Stable host-approved identity domain; immutable across compatible model changes. |
| `records` | Explicit Record/Key, GraphQL name, lookup operation, selected Fields and relationships. No implicit all-record exposure. |
| `connections` | Named root connections to exposed Records and admitted read operation identities. |
| `mutations` | Named roots for declared commands/actions; inputs derive from upstream metadata, never unrestricted CRUD. |
| `operation.kind` | `table` denotes an understood table declaration; `action` an understood action declaration. Never infer equivalence between profiles. |

Record/Field references reuse UMF module/element identities. Key IDs are authored
stable keys, not display names. Relationship references use module/relationship
ID and direction. Every member must resolve in the exact approved source/dependency
closure. Duplicate source identities, GraphQL names or role-conflicting operations
MUST refuse. Names starting `__` and reserved Relay/core outcome names MUST refuse.
Names are case-sensitive. No pluralization, singularization or automatic suffixing
resolves collisions in version 1.

Each exposed Record MUST have one explicitly selected required-scalar Key and a
qualified lookup. Every relationship target MUST be exposed for lookup, even if
it has no list connection. This requirement does not grant list/mutation access.
The selected relationship operation MUST match source, target, direction and
multiplicity. Version 1 admits monomorphic optional/to-one forward expansion;
collection/inverse/polymorphic relationships refuse until separately qualified.

Native Field `id` does not replace Relay `id`. Authors select a distinct API name
such as `nativeId`. Key fields need not themselves be exposed: the runtime returns
internal exact keys to the Node codec without leaking hidden fields to GraphQL.

The initial action profile admits no declared business output values: selecting
action outputs that cannot be preserved by the command outcome profile MUST
refuse. Native table returning rows are deliberately not published as mutable
Node snapshots; CONTRACT-003 explicitly projects effect IDs/receipts and current
refetch. This cannot silently discard an authored action business-result contract.

Preparation MUST intersect explicit exposure with required runtime capabilities.
A selected unsupported feature blocks activation; silently removing it is forbidden.
The original UMF source remains retained without rewriting unknown content.
Unselected unfamiliar metadata remains retained upstream. A constraint affecting
selected meaning cannot be ignored because its metadata field is hidden.

The complete API is an immutable per-application prepared artifact. Export and
execution MUST use the same artifact. SDL type/field/argument definitions are
lexicographically ordered with UTF-8, LF, and one terminal newline; identity Key
component order stays authored. Description text is retained verbatim, escaped by
the GraphQL serializer. Identical approved inputs yield identical SDL bytes.

`schemaDigest` is lowercase SHA-256 of exported SDL bytes. `apiDigest` is SHA-256
of length-framed UTF-8 bytes: domain `lintel.api/1`, raw exposure bytes, sorted
qualified source/dependency identities and digests, canonical capability profile,
scalar codec profile, and SDL. Each frame uses an unsigned big-endian 64-bit byte
length. Source entries are sorted by exact qualified identity; duplicate identity
refuses. Capability profile uses sorted unique capability IDs/versions serialized
as compact JSON arrays of string pairs. All behavior-bearing limits and binding
profile versions are included in that profile. No credential/actor value is hashed
into the shared artifact. Byte identity is conservative; whitespace changes may
change apiDigest without changing schemaDigest.

## Precedence and Compatibility

Host admission and upstream declared semantics precede exposure; host limits can
only tighten. The schema owns structure, this Contract semantic invariants.
Unknown versions refuse. Compatible source edits preserve Node identity; they
still require a newly admitted API artifact and manifest. An unchanged SDL is
not proof of compatible behavior. No runtime hot mutation of the active artifact.

## Error Semantics

| Condition | Outcome | Retry | Recovery |
| --- | --- | --- | --- |
| Malformed configuration/reference | Preparation diagnostic `INVALID_EXPOSURE` with JSON pointer | No | Fix source/selection |
| Unknown selected meaning/capability | `UNSUPPORTED` with selected reference | No | Qualify provider or revise explicit selection |
| Ambiguous GraphQL name/key | `NAME_COLLISION` / `AMBIGUOUS_IDENTITY` | No | Explicitly rename/select |
| Source/binding identity mismatch | `API_MISMATCH` | No automatic retry | Re-admit exact cohort |

Preparation diagnostics contain stable code, configuration pointer and safe source
reference, never instance data. Configuration is immutable on refusal.

## Examples

The Task record exposes `taskKey` as `nativeId`, a Task lookup and a root list.
Person exposes lookup/fields for assignee expansion and Node refetch but no root
list. Completing tasks exists only because `completeTask` is explicitly selected.
The example's operation names are required host obligations, not implemented UMF
commands: the logical model alone cannot activate this API.

## Schema Basis

Inspected core 0.10.0, current Records/Fields/Keys/Relationships, `umf.actions`
0.1.0 and `umf.tables` 0.1.0. Reuse references and meanings; local additions are
API names, exposure and operation bindings. JSON Schema Draft 2020-12 fits a small
closed transport configuration; putting GraphQL naming in UMF core would couple
modeling to this consumer. The pinned logical example has no physical binding or
action implementation. Direct document consumption needs no new schema API.
Native execution spikes qualify capabilities separately; only demonstrated gaps
justify upstream changes.
