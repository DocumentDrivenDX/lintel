"""Exercise installed alpha code without importing the source checkout."""

from __future__ import annotations

import importlib.util
import json
import sysconfig
from importlib.metadata import distribution
from pathlib import Path
from typing import Any

import lintel
from lintel.node_id import StringKeyNodeCodec
from lintel.ports.values import ElementRef, NodeKey
from lintel.projection import TrustedPreparedRef, load_prepared_api

EXPECTED_VERSION = "0.1.0a5"
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


def main() -> None:
    package = distribution("lintel-api")
    assert package.version == lintel.__version__ == EXPECTED_VERSION
    assert Path(lintel.__file__).is_relative_to(sysconfig.get_path("purelib"))
    assert importlib.util.find_spec("lintel.experimental") is None
    assert importlib.util.find_spec("lintel_build") is None

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
                "installedPreparedApi": "pass",
                "apiDigest": prepared.api_digest,
                "moduleOrigin": lintel.__file__,
            }
        )
    )


if __name__ == "__main__":
    main()
