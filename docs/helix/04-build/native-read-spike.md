# Native read spike execution

Governing scope: [SPIKE-002](../02-design/spikes/SPIKE-002-native-reads.md),
CONTRACT-002/003 and TD-002. Execution is explicitly authorized by the owner.
The direct-UMF baseline was pushed as d8d6b7ad1e9b28cd470ac61ac6144c1922e59d7b.

Bound the first probe to pagination, a public batch attempt and interleaved reads.
There is no comparable token-usage baseline or enforced usage cap available.
No production endpoint or full US-002 conformance is claimed.

## Module map and checks

| Module | Responsibility | Allowed integration |
| --- | --- | --- |
| fixture | Synthetic UMF, approved install, owned PostgreSQL, counters | public codegen/lifecycle/runtime, psycopg, pgserver |
| probes | Calls and assertions on observed read behavior | fixture, public runtime, psycopg |
| run | Compose probe and serialize evidence | fixture, probes |

`uv run --group spike --group native-spike python scripts/check_quality.py`
checks imports, strict typing, source ceilings and tests. Native execution is
explicit: `uv run --group spike --group native-spike python -m spikes.native_reads.run`.
Negative import controls refuse private cursor helpers and reverse module coupling.
The native spike uses existing public UMF operation/binding formats, not another
model-description schema. Counters observe actual native statements and leases;
no fake executor qualifies performance. Role/data values are fabricated.

## Continuation

The public release cohort is installed and the native probes exercise real
PostgreSQL, compiled operations, person RLS and interleaved committed writes.
[Native observations](evidence/s02-native-reads.json) retain the exact cohort,
source hashes, statement counts and explicit profile gaps.

Supported subset: page-next continuation; native person visibility; declared
50-key IN lookup, with caller slot reconstruction. Observed counts are two data
reads for root + batch versus 50 for individual lookup calls. Generic batch wire
refuses before acquisition; its refusal does not prove all batching is missing.

Demonstrated gaps: no per-edge/terminal cursors or exact previous-page evidence;
caller-owned repeatable-read native execution refuses SCHEMA_MISMATCH during
admission. Independent database controls separate PostgreSQL snapshot behavior
from the qualified native runtime path. No full request-snapshot claim follows.

No upstream source changes have been made. Preserve the current admission guard;
next work needs a runtime/compiler design for scoped edge positions and current
admission plus a consistent data view. Merely accepting repeatable read is unsafe
as a substitute for that design. The fixed-arity batch route needs Lintel adapter
qualification before widening runtime APIs. Native facts are not a Batten host,
GraphQL server, browser or whole-US-002 conformance result.

Setup initializes only a new fabricated scratch cluster with --no-sync, never a
production database. Each exit stops that server; fabricated data stays in system
temporary storage for diagnosis. SQL in the laboratory snapshot control is an
independent control, not a Lintel execution implementation. Data-read counters
recognize the pinned compiler's WITH umf_read frame; leases are checked for balance. These are cohort-specific measurements, not portable telemetry.

Final source checks: [47 passing tests, lint/type/boundary checks](evidence/s02-checks.json).
Document checks: [links and preserved metadata](evidence/s02-document-checks.json).
The observed server is PostgreSQL 18.6 (180006), with C.UTF-8 database collation.
Ordering evidence covers the fabricated ASCII labels only, not a wider collation profile.
All 61 acquired runtime leases were released. The owned server was stopped on exit.
The S-02 files remain separate from the already pushed S-01 commit.
