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
