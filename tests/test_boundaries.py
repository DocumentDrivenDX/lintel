from pathlib import Path

import pytest

from scripts.check_boundaries import check, violations


@pytest.mark.parametrize(
    ("module", "source", "allowed"),
    [
        ("projection", "from umf import read_document", True),
        ("schema", "from spikes.direct_umf.projection import project", True),
        ("run", "from strawberry.fastapi import GraphQLRouter", True),
        ("projection", "import strawberry", False),
        ("schema", "import batten", False),
        ("schema", "import psycopg", False),
        ("schema", "from umf._private import model", False),
        ("projection", "from spikes.direct_umf.schema import build_probe_schema", False),
        ("projection", "from umf import _hidden", False),
        ("projection", "__import__('batten')", False),
        ("schema", "import importlib; importlib.import_module('batten')", False),
    ],
)
def test_import_controls(module: str, source: str, allowed: bool) -> None:
    assert (not violations(source, module)) is allowed


def test_source_boundaries() -> None:
    assert check(Path(__file__).resolve().parents[1]) == []
