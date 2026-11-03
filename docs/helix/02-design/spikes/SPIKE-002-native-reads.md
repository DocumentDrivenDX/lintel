---
ddx:
  id: SPIKE-002
  type: tech-spike
  activity: design
  authoring:
    home: repo
  links:
    - id: TD-002
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
---

# S-02: Native pagination, batching and consistency

## Objective

Determine which current public UMF runtime capabilities can satisfy Relay read
requirements and which require an owning upstream change. Bound this probe to
one disposable PostgreSQL 18 installation, fabricated rows, a declared paged read
and keyed lookup, and an async public Python runtime. No GraphQL service, Batten
host, client/browser or release qualification is inferred.

## Hypothesis

The native runtime may already support request consistency through caller-owned
transactions. Page continuation and read batches require experiments rather than
assuming the target Lintel protocol exists upstream.

## Approach

Use pinned UMF access 0.1.0.dev8, codegen 0.1.0a5, Weft 0.4.54, psycopg 3.3.6 and
pgserver-pg18 18.6.1. Install only during development. A disposable server owns all
roles/schema/data; startup, installation, concurrency writes and shutdown are
explicit laboratory setup. Never connect to a supplied production DSN.

1. Compile admitted UMF table operations and apply an approved installation.
2. Read with person RLS, tied ordering plus key, next-page, terminal and empty
   results. Try first=0, interior-edge continuation, size changes and foreign scope.
3. Attempt the public batch-read wire; compare native dispatch counts with a
   50-item loop baseline. Do not disguise that loop as batching.
4. Interleave a committed writer with repeated reads under default per-call
   sessions and a caller-owned repeatable-read, read-only transaction.
5. Record observed results, exact inputs/cohort and required changes. Upstream
   changes follow a demonstrated failure only; do not add another schema API.

## Findings

**FINDING 1**: Scoped next-page reads work with native person row-level security
and tied title/key ordering. The returned page frame has one next-page token,
not a cursor per edge or exact previous-page evidence. Terminal rows have no
cursor. Changing requested size refuses cursor reuse; size zero refuses.
Evidence: [native observations](../../04-build/evidence/s02-native-reads.json).

**FINDING 2**: The closed batch-read request refuses before lease acquisition,
but an existing declared fixed-arity 50-key IN read executes in one data statement.
One root plus that lookup uses two measured data reads; the 50-call loop uses 50.
The caller reconstructs ordered duplicate and absent/denied slots from exact keys.
This proves a bounded existing route, not generic batching or relationship policy.

**FINDING 3**: Default per-call reads can observe an intervening committed update.
The public native binding refuses a caller-owned repeatable-read transaction with
SCHEMA_MISMATCH before the data read. PostgreSQL itself retains a consistent view
in the independent laboratory control. Native request-snapshot-1 is unqualified.
The installed head admission guard requires read committed; widening that check
alone would not establish fresh authority or generation checks under a snapshot.

## Analysis

**Hypothesis**: partially confirmed. Existing declared operations avoid a generic
batch API change, but the proposed caller-owned snapshot route is refused.
Native support claims follow the measured subset, not public method names.
The first probe is bounded to the installed public interfaces, not all US-002
acceptance criteria. Request-local Node materialization and host revocation
checks remain Lintel/Batten responsibilities even if native snapshots work.

## Conclusions

The selected runtime already supports bounded keyed batching through declared
IN reads. It does not supply the selected Relay connection or native request
snapshot profile. Those are demonstrated execution-boundary gaps, not missing
UMF schema descriptions. No model/schema API is introduced.

## Recommendations

**RECOMMENDATION**: Reuse the existing declared-IN path for a separately qualified
batch adapter. Limit upstream execution work to authenticated arbitrary-edge
positions/exact PageInfo and a snapshot design preserving fresh admission and
resource custody. Do not weaken guards or relabel next-page tokens as edge cursors.
No upstream source change is made by this investigation; a correct solution spans
native admission and compiler evidence rather than a permissive local patch.

Confidence is high for the observed single-table async cohort. Two-record
relationship parent/target enforcement, 0–100 generic key chunking, revocation,
cancellation, GraphQL/Relay and Batten integration remain unqualified. No concern
selection changes follow from this probe.

## Artifacts

- `spikes/native_reads/fixture.py`: explicit disposable native setup and counters.
- `spikes/native_reads/probes.py`: public runtime calls and observations.
- `spikes/native_reads/run.py`: composition and safe receipt.
- `spikes/native_reads/model.umf.json`: derived from UMF's public synthetic
  [table-operation fixture](https://github.com/DocumentDrivenDX/umf/blob/b12a489844f29947ee52115b90f4ccc5c8bc5032/tests/unified/table-operation-model.json),
  with title ordering and declared keyed/50-key reads; no private application source.
- Cohort source: [UMF v0.5.8](https://github.com/DocumentDrivenDX/umf/releases/tag/umf-v0.5.8)
  and [family PostgreSQL wheel](https://github.com/DocumentDrivenDX/pgserver/releases/tag/pg18.6-pgv0.8.6-r2).
