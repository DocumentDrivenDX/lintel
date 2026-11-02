"""One quality entrypoint for the bounded spike; no dependency installation."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CEILINGS = {
    "mccabe": {"max-complexity": 10},
    "pylint": {
        "max-returns": 6,
        "max-branches": 12,
        "max-statements": 40,
        "max-public-methods": 15,
    },
}


def shape_errors(root: Path) -> list[str]:
    errors: list[str] = []
    config = tomllib.loads((root / "pyproject.toml").read_text())["tool"]["ruff"]["lint"]
    for section, expected in CEILINGS.items():
        if config.get(section) != expected:
            errors.append("strict ceiling configuration changed: " + section)
    for folder in ("scripts", "spikes", "tests"):
        for file in (root / folder).rglob("*.py"):
            limit = 800 if folder == "tests" else 500
            if len(file.read_text().splitlines()) > limit:
                errors.append("file exceeds ceiling: " + str(file.relative_to(root)))
    return errors


def main() -> int:
    errors = shape_errors(ROOT)
    if errors:
        print("\n".join(errors))
        return 1
    for arguments in [
        ["-m", "ruff", "check", "scripts", "spikes", "tests"],
        ["-m", "ruff", "format", "--check", "scripts", "spikes", "tests"],
        ["-m", "pyright", "--pythonpath", sys.executable],
        ["scripts/check_boundaries.py"],
        ["-m", "pytest", "-q", "--tb=short"],
    ]:
        result = subprocess.run([sys.executable, *arguments], cwd=ROOT, check=False)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
