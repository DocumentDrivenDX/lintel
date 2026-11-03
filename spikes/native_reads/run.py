"""Run the explicit disposable native spike and retain safe, exact-cohort evidence."""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
from importlib.metadata import version
from pathlib import Path

from spikes.native_reads.fixture import provision
from spikes.native_reads.probes import run_probes


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    with provision() as fixture:
        observed = asyncio.run(run_probes(fixture))
    paths = [
        *Path(__file__).parent.glob("*.py"),
        Path(__file__).with_name("model.umf.json"),
        root / "pyproject.toml",
        root / "uv.lock",
    ]
    receipt = {
        "spike": "S-02/native-reads",
        "python": sys.version.split()[0],
        "cohort": {
            name: version(name)
            for name in ("umf-access", "umf-codegen", "weft-sql", "psycopg", "pgserver-pg18")
        },
        "inputsSha256": {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)
        },
        "native": fixture.database_facts,
        "observed": observed,
        "upstreamSourceChanges": [],
        "limits": [
            "fabricated disposable local PostgreSQL only",
            "no GraphQL/Relay browser or Batten host",
            "not full lintel.execution/1 conformance; pagination gap is not a pass",
        ],
    }
    destination = root / "docs/helix/04-build/evidence/s02-native-reads.json"
    destination.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
