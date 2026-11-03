"""Observe the installed public runtime; target-profile gaps are explicit results."""

from __future__ import annotations

from typing import Any

import psycopg
from psycopg import sql

from spikes.native_reads.fixture import Fixture, cursor_class


def table(result: dict[str, Any]) -> dict[str, Any]:
    assert "table" in result, result
    return result["table"]


async def pagination(fixture: Fixture) -> dict[str, Any]:
    binding = fixture.reader()
    alice = binding.for_identity(fixture.alice)
    page = table(await alice.execute(fixture.request("read_page", {}, size=2)))
    assert [r["id"] for r in page["rows"]] == ["t-001", "t-002"]
    terminal = table(
        await alice.execute(fixture.request("read_page", {}, size=2, cursor=page["cursor"]))
    )
    assert [r["id"] for r in terminal["rows"]] == ["t-003"] and terminal["cursor"] is None
    single = table(await alice.execute(fixture.request("read_page", {}, size=1)))
    resumed = table(
        await alice.execute(fixture.request("read_page", {}, size=1, cursor=single["cursor"]))
    )
    assert [r["id"] for r in resumed["rows"]] == ["t-002"]
    before = fixture.counts.data_reads
    zero = await alice.execute(fixture.request("read_page", {}, size=0))
    resized = await alice.execute(fixture.request("read_page", {}, size=2, cursor=single["cursor"]))
    foreign = await binding.for_identity(fixture.bob).execute(
        fixture.request("read_page", {}, size=2, cursor=page["cursor"])
    )
    assert "error" in zero and resized["error"]["code"] == "INVALID_CURSOR"
    assert foreign["error"]["code"] == "INVALID_CURSOR"
    assert fixture.counts.data_reads == before
    bob = table(
        await binding.for_identity(fixture.bob).execute(fixture.request("read_page", {}, size=2))
    )
    assert [r["id"] for r in bob["rows"]] == ["t-004"]
    return {
        "visiblePage": ["t-001", "t-002"],
        "tieBreakOrder": "title ASC, id ASC",
        "nextPage": ["t-003"],
        "personRls": True,
        "foreignCursorRefusedBeforeDataRead": True,
        "pageFrameKeys": sorted(page),
        "perEdgeCursorsPresent": "edges" in page,
        "terminalCursorPresent": terminal["cursor"] is not None,
        "exactPreviousPageEvidencePresent": "hasPreviousPage" in page,
        "firstZero": zero["error"]["code"],
        "changedSize": resized["error"]["code"],
        "sameSizeSingleEdgeContinuation": True,
        "gap": "page-next token is not an arbitrary-edge Relay connection",
    }


async def batching(fixture: Fixture) -> dict[str, Any]:
    binding = fixture.reader()
    alice = binding.for_identity(fixture.alice)
    keys = ["t-001", "t-004", "missing", "t-003", "t-001"] * 10
    request = fixture.request("lookup", {})
    request["call"] = {"kind": "batch", "items": [{"id": {"string": k}} for k in keys]}
    before = fixture.counts.leases
    closed_wire = await alice.execute(request)
    assert closed_wire["error"]["code"] == "INVALID" and fixture.counts.leases == before
    before_reads = fixture.counts.data_reads
    table(await alice.execute(fixture.request("read_page", {}, size=2)))
    rows = table(
        await alice.execute(
            fixture.request("lookup_50", {f"k{i:02}": {"string": k} for i, k in enumerate(keys)})
        )
    )["rows"]
    by_key = {row["id"]: row for row in rows}
    slots = [by_key.get(key) for key in keys]
    assert len(slots) == 50 and set(by_key) == {"t-001", "t-003"}
    assert all(slots[i] == slots[0] for i in range(0, 50, 5))
    assert all(slots[i] is None for i in range(1, 50, 5))
    assert all(slots[i] is None for i in range(2, 50, 5))
    batched_reads = fixture.counts.data_reads - before_reads
    assert batched_reads == 2, batched_reads
    before_reads = fixture.counts.data_reads
    for key in keys:
        table(await alice.execute(fixture.request("lookup", {"id": {"string": key}})))
    loop_reads = fixture.counts.data_reads - before_reads
    assert loop_reads == 50, loop_reads
    return {
        "requestedSlots": 50,
        "returnedDistinctAuthorizedRows": len(rows),
        "duplicatesRetained": True,
        "missingAndDeniedSlots": sum(s is None for s in slots),
        "nativeRootPlusInLookupReads": batched_reads,
        "nativeLoopLookupReads": loop_reads,
        "closedBatchWire": closed_wire["error"]["code"],
        "closedBatchWireAcquiredLeases": 0,
        "qualifiedSubset": "declared 50-key IN lookup; caller reorders slots",
        "unqualified": "generic batches and relationship parent/target enforcement",
    }


async def consistency(fixture: Fixture) -> dict[str, Any]:
    request = fixture.request("lookup", {"id": {"string": "t-001"}})
    alice = fixture.reader().for_identity(fixture.alice)
    first = table(await alice.execute(request))["rows"][0]
    fixture.change_title("committed-between-calls")
    second = table(await alice.execute(request))["rows"][0]
    assert first["title"] != second["title"]
    async with await psycopg.AsyncConnection.connect(
        fixture.dsn,
        autocommit=True,
        cursor_factory=cursor_class(fixture.counts),
    ) as connection:
        async with connection.transaction():
            await connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            initial_role = await (await connection.execute("SELECT current_user")).fetchone()
            borrowed = fixture.reader(connection).for_identity(fixture.alice)
            control_sql = sql.SQL("SELECT title FROM {} WHERE id=%s").format(
                sql.Identifier(fixture.schema, "notes")
            )
            control_first = await (await connection.execute(control_sql, ("t-001",))).fetchone()
            before_reads = fixture.counts.data_reads
            refused = await borrowed.execute(request)
            assert refused["error"]["code"] == "SCHEMA_MISMATCH", refused
            assert fixture.counts.data_reads == before_reads
            fixture.change_title("committed-during-snapshot")
            control_second = await (await connection.execute(control_sql, ("t-001",))).fetchone()
            assert control_first == control_second
            final_role = await (await connection.execute("SELECT current_user")).fetchone()
            assert initial_role == final_role and int(connection.info.transaction_status) == 2
        assert not connection.closed
    later = table(await alice.execute(request))["rows"][0]
    assert later["title"] == "committed-during-snapshot"
    return {
        "defaultPerCallViewsDiffer": True,
        "postgresRepeatableReadControlAgrees": True,
        "runtimeRepeatableRead": refused["error"]["code"],
        "runtimeReadDispatchedUnderRepeatableRead": False,
        "newRequestSeesCommittedChange": True,
        "callerRoleRestored": True,
        "callerTransactionPreserved": True,
        "borrowedConnectionPreserved": True,
        "runtimeRequestSnapshotQualified": False,
        "gap": "native admission requires read committed; do not weaken its freshness guard",
        "limits": "sequential borrowed read-only transaction; no cross-page snapshot",
    }


async def run_probes(fixture: Fixture) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, probe in (
        ("pagination", pagination),
        ("batching", batching),
        ("consistency", consistency),
    ):
        print("Native probe: " + name, flush=True)
        result[name] = await probe(fixture)
    assert fixture.counts.leases == fixture.counts.releases
    result["leaseBalance"] = {
        "acquired": fixture.counts.leases,
        "released": fixture.counts.releases,
    }
    result["measuredDataReadStatements"] = fixture.counts.data_reads
    return result
