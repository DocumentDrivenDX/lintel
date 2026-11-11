"""Fail if a tracked file exceeds 1 MB or the tracked tree exceeds 3 MB."""

import subprocess
import sys
from pathlib import Path

MAX_FILE = 1_000_000
MAX_TREE = 3_000_000


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    names = (
        subprocess.run(["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True)
        .stdout.decode()
        .split("\0")
    )
    total = 0
    failed = False
    for name in filter(None, names):
        path = root / name
        if not path.is_file():
            continue
        size = path.stat().st_size
        total += size
        if size > MAX_FILE:
            print(f"file too large: {name} ({size} bytes, limit {MAX_FILE})")
            failed = True
    if total > MAX_TREE:
        print(f"tracked tree too large: {total} bytes, limit {MAX_TREE}")
        failed = True
    print(f"tracked tree: {total} bytes")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
