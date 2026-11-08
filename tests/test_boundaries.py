from pathlib import Path

import pytest

from scripts.check_boundaries import check, violations


@pytest.mark.parametrize(
    ("module", "source", "allowed"),
    [
        ("projection", "from umf import read_document", True),
        ("schema", "from lintel.experimental.projection import project", True),
        ("run", "from strawberry.fastapi import GraphQLRouter", True),
        ("projection", "import strawberry", False),
        ("ports", "import batten", False),
        ("ports_protocols", "import psycopg", False),
        ("ports_values", "import umf_access.unified", False),
        ("ports_errors", "import weft_sql", False),
        ("ports", "from lintel.ports._values import NodeKey", False),
        ("schema", "import batten", False),
        ("schema", "import psycopg", False),
        ("schema", "from umf._private import model", False),
        ("projection", "from lintel.experimental.schema import build_probe_schema", False),
        ("projection", "from umf import _hidden", False),
        ("projection", "__import__('batten')", False),
        ("schema", "import importlib; importlib.import_module('batten')", False),
    ],
)
def test_import_controls(module: str, source: str, allowed: bool) -> None:
    assert (not violations(source, module)) is allowed


def test_source_boundaries() -> None:
    assert check(Path(__file__).resolve().parents[1]) == []


@pytest.mark.parametrize(
    ("module", "source", "allowed"),
    [
        ("native_fixture", "from umf_access.lifecycle import apply_table_migration", True),
        ("native_probes", "from spikes.native_reads.fixture import Fixture", True),
        ("native_probes", "from umf_access.unified import AsyncTableReader", True),
        ("native_probes", "from umf_access.unified.operation_values import token_encode", False),
        ("native_probes", "import batten", False),
        ("projection", "import psycopg", False),
        ("native_fixture", "from spikes.native_reads.probes import run_probes", False),
    ],
)
def test_native_import_controls(module: str, source: str, allowed: bool) -> None:
    assert (not violations(source, module)) is allowed


def test_public_ports_exports_are_stable_and_complete() -> None:
    from lintel import (
        Arguments,
        CommandResult,
        ConnectionPage,
        CoreLiteral,
        Edge,
        ElementRef,
        ExecutionError,
        ExecutionPort,
        NodeCodec,
        NodeKey,
        NodeValue,
        OperationRef,
        RequestScope,
        RequestSession,
        ports,
    )

    expected = {
        "Arguments",
        "CommandResult",
        "ConnectionPage",
        "ConnectionIntent",
        "CoreLiteral",
        "Edge",
        "ElementRef",
        "ExecutionError",
        "ExecutionErrorCode",
        "ExecutionPort",
        "NodeCodec",
        "PlannedExecutionPort",
        "PlannedRequestSession",
        "NodeKey",
        "NodeValue",
        "OperationRef",
        "RequestScope",
        "RequestSession",
    }
    assert set(ports.__all__) == expected
    assert all(hasattr(ports, name) for name in expected)
    assert all(hasattr(ports, name) for name in expected - {"ExecutionErrorCode"})
    assert all(hasattr(__import__("lintel"), name) for name in expected - {"ExecutionErrorCode"})
    assert Arguments is ports.Arguments
    assert CoreLiteral is ports.CoreLiteral
    assert ElementRef.__name__ == "ElementRef"
    assert OperationRef.__name__ == "OperationRef"
    assert NodeKey.__name__ == "NodeKey"
    assert NodeValue.__name__ == "NodeValue"
    assert Edge.__name__ == "Edge"
    assert ConnectionPage.__name__ == "ConnectionPage"
    assert RequestScope.__name__ == "RequestScope"
    assert CommandResult.__name__ == "CommandResult"
    assert ExecutionPort.__name__ == "ExecutionPort"
    assert NodeCodec.__name__ == "NodeCodec"
    assert RequestSession.__name__ == "RequestSession"
    assert ExecutionError.__name__ == "ExecutionError"
