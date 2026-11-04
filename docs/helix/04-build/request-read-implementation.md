# Upstream request-read implementation qualification

The native spike was committed and pushed as feafb8a. Its release-cohort findings
remain historical evidence. Local UMF/Weft candidates now implement its two gaps;
this does not claim the released cohort gained those interfaces.

[Installed-wheel native results](evidence/request-reads-native.json) cover exact
per-edge continuation and flags, hidden/deleted positions, resized pages, zero
first, native-role admission, stable snapshot fields, lifecycle locking, deadlines,
settings drift and cancellation. All28 leases return closed or idle. The
[legacy replay](evidence/request-reads-legacy.json) preserves S-02's ordinary page
semantics and its caller-owned RR refusal.

UMF owns `AsyncTableReader.request` and the two-lease lifecycle. Weft owns page and
previous-position SQL lowering. The model remains UMF; no description API or new
model format is introduced. API scope is a trusted host execution context value.
Source and artifact hashes live in the owning projects' verification receipts at
`docs/helix/04-build/evidence/lintel-request-reads/verification.json`.

The qualifier lives in `spikes/request_reads/qualify.py`. It requires the local
candidate UMF and Weft wheels in an isolated environment, rather than Lintel's
pinned released native-spike cohort. Run that interpreter with
`python -m spikes.request_reads.qualify`. Ordinary source verification remains
`uv run --locked --group spike --group native-spike python scripts/check_quality.py`.

No runtime package install or provider construction is added to product startup.
Initial qualification is async Psycopg3 direct leases, person identities and
PostgreSQL18.6. The host factory must support two leases. Lintel's neutral-port
adapter, generic pool/other-driver coverage, GraphQL/Relay clients and Batten
integration are not established by this native primitive qualification.
