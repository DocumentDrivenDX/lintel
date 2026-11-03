"""Explicit disposable PG18 setup through the existing public UMF lifecycle."""

from __future__ import annotations

import json
import tempfile
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Self, cast

import pgserver
import psycopg
import umf_access.lifecycle
import umf_access.unified as runtime
import umf_codegen
from psycopg import sql

# Integration-only dynamic results from the public, version-pinned upstream APIs.
CODEGEN = cast(Any, umf_codegen)
LIFECYCLE = cast(Any, umf_access.lifecycle)
RUNTIME = cast(Any, runtime)
PGSERVER = cast(Any, pgserver)


@dataclass
class Counts:
    statements: int = 0
    data_reads: int = 0
    leases: int = 0
    releases: int = 0


def cursor_class(counts: Counts) -> type[psycopg.AsyncCursor[Any]]:
    class CountedCursor(psycopg.AsyncCursor[Any]):
        async def execute(
            self,
            query: Any,
            params: Any = None,
            *,
            prepare: bool | None = None,
            binary: bool | None = None,
        ) -> Self:
            counts.statements += 1
            if isinstance(query, str) and query.startswith("WITH umf_read AS MATERIALIZED"):
                counts.data_reads += 1
            return await super().execute(cast(Any, query), params, prepare=prepare, binary=binary)

    return CountedCursor


@dataclass
class Fixture:
    dsn: str = field(repr=False)
    bundle: dict[str, Any]
    reference: dict[str, Any]
    binding: dict[str, Any]
    policy: Any
    schema: str
    alice: Any
    bob: Any
    database_facts: dict[str, object]
    counts: Counts = field(default_factory=Counts)

    def reader(self, connection: psycopg.AsyncConnection[Any] | None = None) -> Any:
        @asynccontextmanager
        async def factory(_identity: Any) -> AsyncGenerator[psycopg.AsyncConnection[Any], None]:
            self.counts.leases += 1
            try:
                if connection is not None:
                    yield connection
                else:
                    async with await psycopg.AsyncConnection.connect(
                        self.dsn,
                        autocommit=True,
                        cursor_factory=cursor_class(self.counts),
                    ) as native:
                        yield native
            finally:
                self.counts.releases += 1

        session = RUNTIME.AsyncSession(
            factory, self.policy, transaction_owner="caller" if connection else "adapter"
        )
        return RUNTIME.NativeTableBinding(
            session,
            self.bundle,
            self.reference,
            self.binding,
            cursor_secret=b"lintel fabricated cursor secret 00000000",
            outcome_secret=b"lintel fabricated outcome secret 000000",
        )

    def request(self, operation: str, inputs: dict[str, Any], **controls: Any) -> dict[str, Any]:
        return {
            "contract": "umf.access/1",
            "schema": self.bundle["sourceDigest"],
            "kind": "table",
            "module": "demo",
            "operation": operation,
            "call": {"kind": "single", "inputs": inputs, **controls},
            "phase": "invoke",
            "mutation": False,
            "idempotency_key": None,
        }

    def change_title(self, value: str) -> None:
        with psycopg.connect(self.dsn, autocommit=True) as writer:
            writer.execute(
                sql.SQL("UPDATE {} SET title=%s WHERE id=%s").format(
                    sql.Identifier(self.schema, "notes")
                ),
                (value, "t-001"),
            )


def _install(dsn: str) -> Fixture:
    source = json.loads(Path(__file__).with_name("model.umf.json").read_text())
    cfg: dict[str, Any] = {
        "module": "demo",
        "schema": "lintel_probe",
        "ownerRole": "lintel_owner",
        "personRole": "lintel_person",
        "batchRole": "lintel_batch",
        "groupRoles": {},
    }
    deployment = CODEGEN.compile_table_deployment(text=json.dumps(source), configuration=cfg)
    assert deployment["status"] == "compiled", deployment
    bundle = deployment["bundle"]
    migration = CODEGEN.compile_table_migration(
        migration_id="s02", predecessor=None, previous_bundle=None, next_bundle=bundle
    )
    assert migration["status"] == "compiled", migration
    reference = _apply_and_seed(dsn, cfg, migration["plan"])
    binding = _binding(source, bundle, cfg)
    policy = RUNTIME.SessionPolicy(
        {"alice": "lintel_alice", "bob": "lintel_bob"}, {}, cfg["schema"], catalog_only=True
    )
    with psycopg.connect(dsn, autocommit=True) as metadata:
        number = metadata.info.server_version
        assert 180000 <= number < 190000
        row = metadata.execute(
            "SELECT datcollate, datlocprovider FROM pg_catalog.pg_database "
            "WHERE datname=current_database()"
        ).fetchone()
        assert row is not None
        database_facts: dict[str, object] = {
            "serverVersionNum": number,
            "databaseCollation": row[0],
            "localeProvider": row[1],
        }
    return Fixture(
        dsn,
        bundle,
        reference,
        binding,
        policy,
        cfg["schema"],
        RUNTIME.SessionIdentity("person", "alice"),
        RUNTIME.SessionIdentity("person", "bob"),
        database_facts,
    )


def _apply_and_seed(dsn: str, cfg: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    with psycopg.connect(dsn, autocommit=True) as admin:
        for role in (
            cfg["ownerRole"],
            cfg["personRole"],
            cfg["batchRole"],
            "lintel_alice",
            "lintel_bob",
        ):
            admin.execute(
                sql.SQL(
                    "CREATE ROLE {} NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB "
                    "NOCREATEROLE NOREPLICATION"
                ).format(sql.Identifier(role))
            )
        for role in ("lintel_alice", "lintel_bob"):
            admin.execute(
                sql.SQL("GRANT {} TO {} WITH INHERIT TRUE, SET FALSE").format(
                    sql.Identifier(cfg["personRole"]), sql.Identifier(role)
                )
            )
        admin.execute(
            sql.SQL("CREATE SCHEMA {} AUTHORIZATION {}").format(
                sql.Identifier(cfg["schema"]), sql.Identifier(cfg["ownerRole"])
            )
        )
        with admin.transaction():
            admin.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(cfg["ownerRole"])))
            admin.execute("SET LOCAL search_path=pg_catalog")
            installed = LIFECYCLE.apply_table_migration(
                admin,
                plan,
                approved_digest=plan["digest"],
                expected_head=None,
                person_roles=("lintel_alice", "lintel_bob"),
            )
        for key, owner, title in [
            ("t-001", "lintel_alice", "A"),
            ("t-002", "lintel_alice", "A"),
            ("t-003", "lintel_alice", "B"),
            ("t-004", "lintel_bob", "A"),
        ]:
            admin.execute(
                sql.SQL("INSERT INTO {} (id, owner, title) VALUES (%s,%s,%s)").format(
                    sql.Identifier(cfg["schema"], "notes")
                ),
                (key, owner, title),
            )
        return cast(dict[str, Any], installed["installationReference"])


def _binding(source: dict[str, Any], bundle: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    table = source["modules"][0]["extensions"]["umf.tables"]["tables"][0]
    return {
        "version": "umf.raw-read-binding/0.1",
        "schema": cfg["schema"],
        "modelJson": bundle["source"]["utf8"],
        "modelSha256": bundle["sourceDigest"],
        "tables": [
            {
                "logical": ["demo", "Note"],
                "native": "notes",
                "key": ["id"],
                "columns": [
                    {
                        "logical": c["field"]["element"],
                        "native": c["name"],
                        "carrier": "string",
                        "nullable": False,
                    }
                    for c in table["columns"]
                ],
            }
        ],
        "relationships": [],
        "nativeLifecycle": {
            "version": "umf.table-lifecycle/0.1",
            "module": "demo",
            "configurationDigest": bundle["configurationDigest"],
            "deploymentDigest": bundle["bundleDigest"],
        },
    }


@contextmanager
def provision() -> Generator[Fixture, None, None]:
    # Keep fabricated scratch data for diagnostics; stop the owned server on every exit.
    directory = tempfile.mkdtemp(prefix="lintel-s02-")
    pgdata = Path(directory) / "pgdata"
    # Only this disposable fabricated cluster uses --no-sync; it is not durable storage.
    PGSERVER.initdb(
        ["--no-sync", "--auth=trust", "--auth-local=trust", "--encoding=utf8", "-U", "postgres"],
        pgdata=pgdata,
    )
    server = PGSERVER.get_server(pgdata, cleanup_mode="stop")
    try:
        yield _install(server.get_uri())
    finally:
        server.cleanup()
