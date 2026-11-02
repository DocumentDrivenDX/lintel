# Task-board reference profile

These are original fabricated design inputs. They specify an intended journey;
no executable API, native table install or Relay compiler result is supplied.

- `task-board.umf.json` is the logical core 0.10 model. It has no table/action
  vocabulary and cannot by itself execute any operation.
- `task-board.exposure.json` explicitly selects API names and required host
  operation identities. Field `note` is hidden from reads; its optional command
  input is distinct from unrestricted writes or generic unset.
- `task-board.graphql` is illustrative target SDL, not generated implementation
  output. Its scalar and outcome behavior is governed by CONTRACT-003.
- `task-board.operations.graphql` contains standard executable GraphQL documents.
- `task-board.relay.graphql` contains authoring directives interpreted by Relay's
  compiler; those documents must not be sent unchanged as wire queries.
- `task-board.cases.json` is fixture planning data, not a UMF data instance or a
  domain-pack/native binding. Values have the meanings described here, not an
  invented interoperable data format. `host-profile.json` is bounded configuration.

## Required host operations

| Source identity | Meaning and required capability |
| --- | --- |
| board.lookupTasks / lookupPeople (table) | Authorized ordered keyed batch lookup under request-snapshot-1. |
| board.listTasks (table) | Authorized Task connection ordered by title then exact taskKey using an explicitly qualified native C collation for this fixture; per-edge cursor and exact PageInfo. |
| board.readAssignees (table) | To-one batch traversal for Task -> Person, preserving absent/denied target slots. |
| board.completeTask (table) | Task identity input; optional tri-state note. Transition OPEN to DONE under current authority/confirmation; omitted note does not change it, explicit null clears the native nullable note, supplied text stores it. Native operation parameters/effects must declare this behavior. |

The desired completeTask.task parameter is explicitly a Task Key reference.
A native scalar Field parameter alone does not establish that role; the owning
UMF operation declaration or qualified native binding must declare it or the ID projection refuses.
S-03 must first inspect existing UMF operation declarations and native bindings.
A new upstream field is justified only if those cannot express the required role;
a separate schema API is not a prerequisite.

The physical mappings, native policies, declared command parameter metadata,
snapshot/receipt storage and qualified operation declarations must be authored
and admitted upstream before the example can activate. These rows are obligations
for that work, not alternate definitions of `umf.tables` or an accepted dialect.

## Concrete expected observations

Alice sees tasks t-001, t-002, t-003. With first=2, the first page has t-001/t-002;
after its first edge, the next page has t-002/t-003. Bob sees only t-004.
Alice's t-003 assignee is null because p-2 is hidden; it is not a permission to
look up p-2. A duplicate Node in Alice's query agrees on its selected fields under
concurrent writes. Different apps can reuse native keys without sharing Node IDs
or client stores. The decimal on t-001 retains `9007199254740993.01` exactly.

After a committed completeTask response is lost, observation of the same key and
original arguments recovers a receipt without replay. Current reads refetch DONE.
If the outer caller transaction is still open, durability is PENDING_CALLER_COMMIT;
no UI or receipt may call it committed. A missing receipt is not proof of no effect.

The 50-parent batching case is generated deterministically by the native harness;
all parents reference p-1. Its assertion measures real native dispatch count,
not only mocked loader calls. Seed application is explicit, upstream and separate
from Lintel startup.
