from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Protocol, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response as HttpxResponse

import lintel
from lintel.app import create_memory_app
from lintel.cli import main
from lintel.memory import MemoryNodeCodec, MemoryPort, capabilities_for
from lintel.ports import ExecutionError, OperationRef, RequestScope
from lintel.projection import load_prepared_api
from lintel.trust import pin_for

ID_PREFIX = "demo.task-board.identity-v1:board."


class _Client(Protocol):
    def post(
        self, url: str, *, headers: Mapping[str, str], json: Mapping[str, object]
    ) -> HttpxResponse: ...


@pytest.fixture
def demo(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> Path:
    assert main(["example", "task-board", str(tmp_path)]) == 0
    assert (
        main(
            [
                "prepare",
                str(tmp_path / "task-board.umf.json"),
                "--exposure",
                str(tmp_path / "exposure.json"),
                "--host",
                str(tmp_path / "host-profile.json"),
                "-o",
                str(tmp_path / "api.json"),
            ]
        )
        == 0
    )
    capsys.readouterr()
    return tmp_path


def _query(demo: Path, query: str, variables: dict[str, object] | None = None) -> dict[str, object]:
    app, prepared = create_memory_app(demo / "api.json", demo / "records.json")
    body: dict[str, object] = {"query": query}
    if variables:
        body["variables"] = variables
    response = cast(_Client, TestClient(app)).post(
        "/graphql",
        headers={"x-lintel-api": prepared.api_digest, "content-type": "application/json"},
        json=body,
    )
    assert response.status_code == 200
    return response.json()


def test_example_prepare_serve_flow_answers_node_query(demo: Path) -> None:
    body = _query(
        demo,
        'query { node(id: "' + ID_PREFIX + 'Task:task-2") { id ... on Task { title estimate } } }',
    )
    assert body == {
        "data": {
            "node": {
                "id": ID_PREFIX + "Task:task-2",
                "title": "Cut the release",
                "estimate": "9007199254740993.01",
            }
        }
    }


def test_nodes_returns_null_for_unknown_and_malformed_ids(demo: Path) -> None:
    ids = [
        ID_PREFIX + "Task:task-1",
        ID_PREFIX + "Task:nope",
        "garbage",
        ID_PREFIX + "Person:person-1",
    ]
    body = _query(
        demo,
        "query($ids:[ID!]!){ nodes(ids:$ids){ ... on Task { title } "
        "... on Person { displayName } } }",
        {"ids": ids},
    )
    assert body["data"] == {
        "nodes": [{"title": "Write the quickstart"}, None, None, {"displayName": "Ada"}]
    }


def test_wrong_api_digest_is_refused(demo: Path) -> None:
    app, _ = create_memory_app(demo / "api.json", demo / "records.json")
    response = cast(_Client, TestClient(app)).post(
        "/graphql",
        headers={"x-lintel-api": "0" * 64, "content-type": "application/json"},
        json={"query": "{ __typename }"},
    )
    assert response.status_code == 412


def test_expect_digest_and_tampering_are_refused(demo: Path) -> None:
    with pytest.raises(ValueError, match="API_MISMATCH"):
        create_memory_app(demo / "api.json", demo / "records.json", expect_digest="0" * 64)
    # The artifact is canonical JSON; any edit must fail admission against its own pin.
    contents = (demo / "api.json").read_bytes()
    pin = pin_for(contents)
    with pytest.raises(ValueError, match="API_MISMATCH"):
        load_prepared_api(contents.replace(b"task-board-demo", b"other-board-demo"), pin)


def test_connections_and_commands_are_unsupported(demo: Path) -> None:
    contents = (demo / "api.json").read_bytes()
    prepared = load_prepared_api(contents, pin_for(contents))
    port = MemoryPort.from_json(prepared, (demo / "records.json").read_bytes())
    assert dict(port.capabilities()) == dict(prepared.capabilities)
    assert isinstance(port.codec, MemoryNodeCodec)
    operation = OperationRef("board", "lookupTasks", "table")
    scope = RequestScope("task-board-demo", prepared.api_digest, "query", "x", "r", 0.0)

    async def attempt() -> list[str]:
        codes: list[str] = []
        async with port.session(scope) as session:
            for call in (
                session.connection(operation, {}, 1, None, ()),
                session.invoke(operation, {}, "k", None),
            ):
                try:
                    await call
                except ExecutionError as error:
                    codes.append(error.code)
        return codes

    assert asyncio.run(attempt()) == ["UNSUPPORTED", "UNSUPPORTED"]


def test_capabilities_cover_every_lookup_and_limit(demo: Path) -> None:
    exposure = json.loads((demo / "exposure.json").read_text())
    host = json.loads((demo / "host-profile.json").read_text())
    caps = capabilities_for(exposure, host)
    assert caps["operation.binding/board/lookupTasks/table"] == "lintel.memory/1"
    assert caps["operation.binding/board/lookupPeople/table"] == "lintel.memory/1"
    assert caps["limit.maxPage"] == "100"


def test_prepare_reports_invalid_umf_without_traceback(
    demo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = demo / "bad.json"
    bad.write_text("{}")
    code = main(
        [
            "prepare",
            str(bad),
            "--exposure",
            str(demo / "exposure.json"),
            "--host",
            str(demo / "host-profile.json"),
            "-o",
            str(demo / "out.json"),
        ]
    )
    assert code == 1
    assert "prepare failed" in capsys.readouterr().err
    assert not (demo / "out.json").exists()


def test_version_flag_matches_package(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--version"])
    assert raised.value.code == 0
    assert capsys.readouterr().out.strip() == f"lintel {lintel.__version__}"


def test_serve_path_does_not_need_umf(demo: Path) -> None:
    script = f"""
import importlib.abc, sys
class Deny(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        banned = ('umf.', 'strawberry.', 'lintel.build', 'lintel.experimental')
        if fullname in ('umf', 'strawberry') or fullname.startswith(banned):
            raise ModuleNotFoundError(fullname)
sys.meta_path.insert(0, Deny())
import lintel.cli, lintel.memory, lintel.trust
from lintel.app import create_memory_app
create_memory_app({str(demo / "api.json")!r}, {str(demo / "records.json")!r})
"""
    result = subprocess.run(
        [sys.executable, "-c", script], check=False, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
