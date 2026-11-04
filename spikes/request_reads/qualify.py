"""Native qualification of the local upstream request-read implementation."""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import replace
from importlib.metadata import version
from pathlib import Path
from typing import Any, cast

import psycopg
import umf_access.unified as runtime
from psycopg import sql

from spikes.native_reads.fixture import Fixture, cursor_class, provision

ACCESS = cast(Any, runtime)


def reader_and_snapshot(fixture: Fixture, leases: list[Any] | None = None) -> tuple[Any, Any]:
    @asynccontextmanager
    async def factory(_identity: Any) -> AsyncGenerator[psycopg.AsyncConnection[Any], None]:
        fixture.counts.leases += 1
        try:
            async with await psycopg.AsyncConnection.connect(
                fixture.dsn,
                autocommit=True,
                cursor_factory=cursor_class(fixture.counts),
            ) as connection:
                if leases is not None:
                    leases.append(connection)
                try:
                    yield connection
                finally:
                    assert connection.closed or int(connection.info.transaction_status) == 0, (
                        "runtime returned an unusable connection to its factory"
                    )
        finally:
            fixture.counts.releases += 1

    admission = ACCESS.AsyncSession(factory, fixture.policy)
    snapshot = ACCESS.AsyncSession(factory, fixture.policy)
    reader = ACCESS.AsyncTableReader(
        admission,
        fixture.bundle,
        fixture.reference,
        fixture.binding,
        cursor_secret=b"lintel fabricated cursor secret 00000000",
    )
    return reader, snapshot


def ids(connection: dict[str, Any]) -> list[str]:
    return [edge["row"]["id"] for edge in connection["edges"]]


async def pages(fixture: Fixture) -> dict[str, Any]:
    # Hidden earlier row must not leak through the compiler's previous-page probe.
    with psycopg.connect(fixture.dsn, autocommit=True) as admin:
        admin.execute(
            sql.SQL("UPDATE {} SET title=%s WHERE id=%s").format(
                sql.Identifier(fixture.schema, "notes")
            ),
            ("0", "t-004"),
        )
    reader, snapshot = reader_and_snapshot(fixture)
    async with reader.request(
        fixture.alice, snapshot_session=snapshot, api_scope="app/api-v1"
    ) as request:
        first = await request.connection("read_page", {}, first=2)
        assert ids(first) == ["t-001", "t-002"]
        assert first["hasNextPage"] is True and first["hasPreviousPage"] is False
        middle = await request.connection(
            "read_page", {}, first=2, after=first["edges"][0]["cursor"]
        )
        assert ids(middle) == ["t-002", "t-003"]
        assert middle["hasPreviousPage"] is True and middle["hasNextPage"] is False
        terminal = await request.connection("read_page", {}, first=1, after=middle["endCursor"])
        assert (
            ids(terminal) == []
            and terminal["startCursor"] is None
            and terminal["endCursor"] is None
        )
        assert terminal["hasPreviousPage"] is True and terminal["hasNextPage"] is False
        zero = await request.connection("read_page", {}, first=0)
        assert ids(zero) == [] and zero["hasNextPage"] is True and zero["hasPreviousPage"] is False
        resized = await request.connection("read_page", {}, first=1, after=first["startCursor"])
        assert ids(resized) == ["t-002"]
        cursor = middle["endCursor"]
    try:
        await request.read("lookup", {"id": {"string": "t-001"}})
    except RuntimeError:
        pass
    else:
        raise AssertionError("closed scope accepted")
    for actor, scope, token in [
        (fixture.bob, "app/api-v1", cursor),
        (fixture.alice, "app/api-v2", cursor),
        (fixture.alice, "app/api-v1", "tampered" + cursor),
    ]:
        async with reader.request(actor, snapshot_session=snapshot, api_scope=scope) as request:
            before = fixture.counts.data_reads
            try:
                await request.connection("read_page", {}, first=2, after=token)
            except RuntimeError:
                assert fixture.counts.data_reads == before
            else:
                raise AssertionError("foreign or tampered cursor accepted")
    await deleted_position(fixture, reader, snapshot, first["startCursor"])
    return {
        "hiddenEarlierRowDoesNotLeakThroughPreviousFlag": True,
        "deletedPositionPreviousFlagExact": True,
        "interiorEdge": True,
        "terminalEdge": True,
        "exactFlags": True,
        "firstZero": True,
        "changedSize": True,
        "closedScopeRefused": True,
        "foreignAndTamperedRefused": True,
    }


async def deleted_position(fixture: Fixture, reader: Any, snapshot: Any, cursor: str) -> None:
    with psycopg.connect(fixture.dsn, autocommit=True) as admin:
        admin.execute(
            sql.SQL("DELETE FROM {} WHERE id=%s").format(sql.Identifier(fixture.schema, "notes")),
            ("t-001",),
        )
    try:
        async with reader.request(
            fixture.alice, snapshot_session=snapshot, api_scope="app/api-v1"
        ) as request:
            deleted = await request.connection("read_page", {}, first=2, after=cursor)
            assert ids(deleted) == ["t-002", "t-003"] and deleted["hasPreviousPage"] is False
    finally:
        with psycopg.connect(fixture.dsn, autocommit=True) as admin:
            admin.execute(
                sql.SQL("INSERT INTO {} (id,owner,title) VALUES (%s,%s,%s)").format(
                    sql.Identifier(fixture.schema, "notes")
                ),
                ("t-001", "lintel_alice", "A"),
            )


async def consistent_fields(fixture: Fixture) -> dict[str, Any]:
    reader, snapshot = reader_and_snapshot(fixture)
    inputs = {"id": {"string": "t-001"}}
    async with reader.request(
        fixture.alice, snapshot_session=snapshot, api_scope="app/api-v1"
    ) as request:
        first = await request.read("lookup", inputs)
        fixture.change_title("updated-after-snapshot")
        again, duplicate = cast(
            tuple[dict[str, Any], dict[str, Any]],
            await asyncio.gather(request.read("lookup", inputs), request.read("lookup", inputs)),
        )
        assert first["rows"] == again["rows"] == duplicate["rows"]
        # Independent native witness: the retained admission lease fences the lifecycle lock.
        lock = int.from_bytes(
            hashlib.sha256(b"umf.table-lifecycle/0.1\0lintel_probe").digest()[:8],
            "big",
            signed=True,
        )
        with psycopg.connect(fixture.dsn, autocommit=True) as admin:
            with admin.transaction():
                assert admin.execute(
                    "SELECT pg_catalog.pg_try_advisory_xact_lock(%s)", (lock,)
                ).fetchone() == (False,)
    with psycopg.connect(fixture.dsn, autocommit=True) as admin:
        with admin.transaction():
            assert admin.execute(
                "SELECT pg_catalog.pg_try_advisory_xact_lock(%s)", (lock,)
            ).fetchone() == (True,)
    later = await reader.read(fixture.alice, "lookup", inputs)
    assert later["rows"][0]["title"] == "updated-after-snapshot"
    return {
        "interleavedUpdateStable": True,
        "concurrentDispatchSerialized": True,
        "laterRequestFresh": True,
        "lifecycleLockHeldUntilScopeExit": True,
    }


async def revocation(fixture: Fixture) -> dict[str, Any]:
    reader, snapshot = reader_and_snapshot(fixture)
    inputs = {"id": {"string": "t-001"}}
    try:
        async with reader.request(
            fixture.alice, snapshot_session=snapshot, api_scope="app/api-v1"
        ) as request:
            await request.read("lookup", inputs)
            with psycopg.connect(fixture.dsn, autocommit=True) as admin:
                admin.execute("REVOKE lintel_person FROM lintel_alice")
            before = fixture.counts.data_reads
            try:
                await request.read("lookup", inputs)
            except RuntimeError:
                assert fixture.counts.data_reads == before
            else:
                raise AssertionError("revocation did not refuse before data read")
    finally:
        with psycopg.connect(fixture.dsn, autocommit=True) as admin:
            admin.execute("GRANT lintel_person TO lintel_alice WITH INHERIT TRUE, SET FALSE")
    return {"liveRoleRevocationRefusedBeforeDataRead": True}


async def dangerous_roles(fixture: Fixture) -> dict[str, Any]:
    reader, snapshot = reader_and_snapshot(fixture)
    for attribute in ("BYPASSRLS", "SUPERUSER"):
        try:
            async with reader.request(
                fixture.alice, snapshot_session=snapshot, api_scope="app/api-v1"
            ) as request:
                await request.read("lookup", {"id": {"string": "t-001"}})
                with psycopg.connect(fixture.dsn, autocommit=True) as admin:
                    statement = (
                        "ALTER ROLE lintel_alice BYPASSRLS"
                        if attribute == "BYPASSRLS"
                        else "ALTER ROLE lintel_alice SUPERUSER"
                    )
                    admin.execute(cast(Any, statement))
                before = fixture.counts.data_reads
                try:
                    await request.read("lookup", {"id": {"string": "t-001"}})
                except RuntimeError:
                    assert fixture.counts.data_reads == before
                else:
                    raise AssertionError("unsafe native role was not refused")
        finally:
            with psycopg.connect(fixture.dsn, autocommit=True) as admin:
                admin.execute("ALTER ROLE lintel_alice NOBYPASSRLS NOSUPERUSER")
    return {"bypassRlsRefusedBeforeDataRead": True, "superuserRefusedBeforeDataRead": True}


async def settings_drift(fixture: Fixture) -> dict[str, Any]:
    leases: list[Any] = []
    reader, snapshot = reader_and_snapshot(fixture, leases)
    async with reader.request(
        fixture.alice, snapshot_session=snapshot, api_scope="app/api-v1"
    ) as request:
        await request.read("lookup", {"id": {"string": "t-001"}})
        data = None
        for connection in leases:
            isolation = await (await connection.execute("SHOW transaction_isolation")).fetchone()
            if isolation == ("repeatable read",):
                data = connection
        assert data is not None
        await data.execute("SELECT pg_catalog.set_config('search_path','public',true)")
        before = fixture.counts.data_reads
        try:
            await request.read("lookup", {"id": {"string": "t-001"}})
        except RuntimeError:
            assert fixture.counts.data_reads == before
        else:
            raise AssertionError("snapshot settings drift accepted")
    assert fixture.counts.leases == fixture.counts.releases
    return {"snapshotSettingsDriftRefusedBeforeDataRead": True, "poisonedScopeRolledBack": True}


async def cancellation(fixture: Fixture) -> dict[str, Any]:
    reader, snapshot = reader_and_snapshot(fixture)
    started = asyncio.Event()

    async def worker() -> None:
        async with reader.request(
            fixture.alice, snapshot_session=snapshot, api_scope="app/api-v1"
        ) as request:
            started.set()
            await request.read("lookup", {"id": {"string": "t-001"}})

    with psycopg.connect(fixture.dsn, autocommit=True) as blocker:
        with blocker.transaction():
            blocker.execute(
                sql.SQL("LOCK TABLE {} IN ACCESS EXCLUSIVE MODE").format(
                    sql.Identifier(fixture.schema, "notes")
                )
            )
            task = asyncio.create_task(worker())
            try:
                await asyncio.wait_for(started.wait(), 10)
                for _ in range(100):
                    with psycopg.connect(fixture.dsn, autocommit=True) as monitor:
                        waiting = monitor.execute(
                            "SELECT count(*) FROM pg_catalog.pg_stat_activity "
                            "WHERE wait_event_type='Lock' AND wait_event='relation'"
                        ).fetchone()
                    if waiting and waiting[0]:
                        break
                    await asyncio.sleep(0.02)
                else:
                    raise AssertionError("native relation wait was not witnessed")
            finally:
                task.cancel()
                await asyncio.sleep(0)
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                else:
                    raise AssertionError("cancellation did not propagate")
    assert fixture.counts.leases == fixture.counts.releases
    await reader.read(fixture.alice, "lookup", {"id": {"string": "t-001"}})
    return {
        "nativeRelationWaitWitnessed": True,
        "repeatedCancellationPropagates": True,
        "bothLeasesReleased": True,
        "readerUsableAfterCancellation": True,
    }


async def drain_on_close(fixture: Fixture) -> dict[str, Any]:
    reader, snapshot = reader_and_snapshot(fixture)
    with psycopg.connect(fixture.dsn, autocommit=True) as blocker:
        with blocker.transaction():
            blocker.execute(
                sql.SQL("LOCK TABLE {} IN ACCESS EXCLUSIVE MODE").format(
                    sql.Identifier(fixture.schema, "notes")
                )
            )
            async with reader.request(
                fixture.alice, snapshot_session=snapshot, api_scope="app/api-v1"
            ) as request:
                task = asyncio.create_task(request.read("lookup", {"id": {"string": "t-001"}}))
                for _ in range(100):
                    with psycopg.connect(fixture.dsn, autocommit=True) as monitor:
                        waiting = monitor.execute(
                            "SELECT count(*) FROM pg_catalog.pg_stat_activity "
                            "WHERE wait_event_type='Lock' AND wait_event='relation'"
                        ).fetchone()
                    if waiting and waiting[0]:
                        break
                    await asyncio.sleep(0.02)
                else:
                    task.cancel()
                    raise AssertionError("in-flight read never reached native wait")
            try:
                await task
            except asyncio.CancelledError:
                pass
            else:
                raise AssertionError("in-flight read escaped scope close")
    assert fixture.counts.leases == fixture.counts.releases
    return {"inFlightReadCancelledAndDrainedOnExit": True, "noLateResult": True}


async def deadline(fixture: Fixture) -> dict[str, Any]:
    policy = ACCESS.SessionPolicy(
        fixture.policy.people,
        fixture.policy.batches,
        fixture.schema,
        catalog_only=True,
        statement_timeout_ms=100,
    )
    limited = replace(fixture, policy=policy)
    reader, snapshot = reader_and_snapshot(limited)
    try:
        async with reader.request(limited.alice, snapshot_session=snapshot, api_scope="app/api-v1"):
            await asyncio.sleep(0.3)
    except TimeoutError:
        pass
    else:
        raise AssertionError("request deadline did not propagate")
    assert fixture.counts.leases == fixture.counts.releases
    return {"requestDeadlinePropagates": True, "timedOutLeasesReleased": True}


async def qualify(fixture: Fixture) -> dict[str, Any]:
    observations: dict[str, Any] = {}
    for name, probe in [
        ("pages", pages),
        ("consistency", consistent_fields),
        ("revocation", revocation),
        ("dangerousRoles", dangerous_roles),
        ("settingsDrift", settings_drift),
        ("cancellation", cancellation),
        ("drainOnClose", drain_on_close),
        ("deadline", deadline),
    ]:
        print("Request-read qualification: " + name, flush=True)
        observations[name] = await probe(fixture)
    assert fixture.counts.leases == fixture.counts.releases
    observations["noUnusableLeaseReturned"] = True
    observations["leases"] = {
        "acquired": fixture.counts.leases,
        "released": fixture.counts.releases,
    }
    return observations


def main() -> None:
    with provision() as fixture:
        observed = asyncio.run(qualify(fixture))
    root = Path(__file__).resolve().parents[2]
    result = {
        "profile": "local-upstream-request-reads",
        "python": sys.version.split()[0],
        "weftDistributionVersion": version("weft-sql"),
        "native": fixture.database_facts,
        "observed": observed,
        "limits": "local source candidate; Psycopg3/PG18 only, not a release",
    }
    (root / "docs/helix/04-build/evidence/request-reads-native.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
