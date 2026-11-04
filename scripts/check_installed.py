"""Exercise installed alpha code without importing the source checkout."""

from __future__ import annotations

import json
import sysconfig
from importlib.metadata import distribution
from pathlib import Path

import lintel
from lintel.experimental.projection import project
from lintel.experimental.schema import build_probe_schema


def main() -> None:
    package = distribution("lintel-api")
    assert package.version == lintel.__version__ == "0.1.0a1"
    assert Path(lintel.__file__).is_relative_to(sysconfig.get_path("purelib"))
    # This file is fixture input only; no checkout code is added to sys.path.
    fixture = (
        Path(__file__).resolve().parents[1] / "docs/helix/02-design/examples/task-board.umf.json"
    )
    plan = project(
        fixture.read_text(),
        ("board", "Task"),
        "Task",
        {("board", "title"): "title", ("board", "estimate"): "estimate"},
    )
    schema = build_probe_schema(plan, {"title": "Fabricated", "estimate": "9007199254740993.01"})
    result = schema.execute_sync("{ probe { title estimate } }")
    assert not result.errors
    assert result.data == {"probe": {"title": "Fabricated", "estimate": "9007199254740993.01"}}
    print(
        json.dumps(
            {
                "distribution": package.metadata["Name"],
                "version": package.version,
                "installedProjection": "pass",
                "moduleOrigin": lintel.__file__,
            }
        )
    )


if __name__ == "__main__":
    main()
