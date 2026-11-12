"""Exercise the installed wheel (not the checkout): imports, admission, README quickstart.

Run as ``python -I scripts/smoke_installed.py [--version X]`` with the interpreter of a
fresh venv holding the built wheel installed with ``[build,serve,experimental]``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import sysconfig
import tempfile
import time
from importlib.metadata import distribution
from pathlib import Path
from typing import Any

import lintel
from lintel.build.http_projection import project_http
from lintel.http import create_router as create_http_router
from lintel.node_id import StringKeyNodeCodec
from lintel.ports.values import ElementRef, NodeKey
from lintel.projection import TrustedPreparedRef, load_prepared_api

README = Path(__file__).resolve().parents[1] / "README.md"
# These files are fixture input only; no checkout code is added to sys.path.
FIXTURES = Path(__file__).resolve().parents[1] / "tests/fixtures"


def _pairs(rows: list[list[str]]) -> tuple[tuple[str, str], ...]:
    return tuple((row[0], row[1]) for row in rows)


def _trusted_ref(trust: dict[str, Any]) -> TrustedPreparedRef:
    sources: list[dict[str, str]] = trust["sources"]
    return TrustedPreparedRef(
        artifact_sha256=trust["artifactSha256"],
        artifact_digest=trust["artifactDigest"],
        application=trust["application"],
        api_digest=trust["apiDigest"],
        exposure_sha256=trust["exposureSha256"],
        sources=tuple((row["identity"], row["sha256"]) for row in sources),
        capabilities=_pairs(trust["capabilities"]),
        binding_profile=trust["bindingProfile"],
        scalar_codec_profile=trust["scalarCodecProfile"],
        limits=_pairs(trust["limits"]),
        generated_roots_sha256=trust["generatedRootsSha256"],
        generated_connections_sha256=trust["generatedConnectionsSha256"],
    )


def quickstart_commands() -> list[str]:
    text = README.read_text()
    match = re.search(r"```sh quickstart\n(.*?)```", text, re.DOTALL)
    assert match, "README has no ```sh quickstart block"
    return [
        line
        for line in match.group(1).splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "pip "))
    ]


def _run_shell(line: str, cwd: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    result: subprocess.CompletedProcess[str] = subprocess.CompletedProcess(line, 7, "", "")
    for _attempt in range(40):  # the server prints its digest before it listens
        result = subprocess.run(
            line, shell=True, cwd=cwd, env=env, text=True, capture_output=True, check=False
        )
        if result.returncode != 7:  # curl: connection refused
            break
        time.sleep(0.25)
    return result


def run_quickstart() -> None:
    """Execute the README quickstart verbatim from a scratch directory."""
    env = {**os.environ, "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"]}
    server: subprocess.Popen[str] | None = None
    with tempfile.TemporaryDirectory() as work:
        try:
            for line in quickstart_commands():
                if line.startswith("lintel serve"):
                    server = subprocess.Popen(
                        line.rstrip("&").split(),
                        cwd=work,
                        env=env,
                        stdout=subprocess.PIPE,
                        text=True,
                    )
                    assert server.stdout is not None
                    digest = server.stdout.readline().split(":", 1)[1].strip()
                    assert server.stdout.readline().startswith("POST http")
                    env["DIGEST"] = digest
                    continue
                result = _run_shell(line, work, env)
                assert result.returncode == 0, f"{line}\n{result.stdout}\n{result.stderr}"
                if line.startswith("curl"):
                    answer = json.loads(result.stdout)
                    print("quickstart answer:", json.dumps(answer))
                    assert answer["data"]["node"]["title"] == "Write the quickstart", answer
        finally:
            if server is not None:
                server.terminate()
                server.wait(timeout=10)
    assert server is not None, "quickstart did not start lintel serve"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", help="expected installed version (the release tag)")
    expected = parser.parse_args().version
    package = distribution("lintel-api")
    assert package.version == lintel.__version__
    if expected:
        assert package.version == expected.removeprefix("v"), (package.version, expected)
    assert Path(lintel.__file__).is_relative_to(sysconfig.get_path("purelib"))
    assert importlib.util.find_spec("lintel.experimental") is not None
    assert importlib.util.find_spec("lintel.build") is not None
    assert callable(project_http) and callable(create_http_router)
    run_quickstart()

    codec = StringKeyNodeCodec()
    key = NodeKey(ElementRef("board", "Task"), "primary", ({"string": "Fabricated"},))
    assert codec.decode("app", codec.encode("app", key)) == key

    raw = (FIXTURES / "prepared-api-v4-weft7-build27-proof.json").read_bytes()
    trust = json.loads((FIXTURES / "prepared-api-v4-weft7-build27-trust.json").read_bytes())
    prepared = load_prepared_api(raw, _trusted_ref(trust))
    assert prepared.api_digest == trust["apiDigest"]
    print(
        json.dumps(
            {
                "distribution": package.metadata["Name"],
                "version": package.version,
                "quickstart": "pass",
                "installedPreparedApi": "pass",
                "moduleOrigin": lintel.__file__,
            }
        )
    )


if __name__ == "__main__":
    main()
