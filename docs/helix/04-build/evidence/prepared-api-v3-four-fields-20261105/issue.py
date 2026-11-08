from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, "/private/tmp/lintel-api3-issuance-site-20261105")

from umf_access_generated_executor import (  # noqa: E402
    GeneratedFiles,
    GeneratedManifest,
    TargetBinding,
    TrustedArtifactRef,
)
from lintel_build import prepare_api_v3  # noqa: E402

ROOT = Path("/Users/erik/Projects/lintel")
UMF_EVIDENCE = Path(
    "/Users/erik/Projects/umf/docs/helix/04-build/evidence/"
    "generated-execution-v5-two-roots-20261104"
)
OUTPUT = Path("/private/tmp/lintel-api3-four-fields-20261105")

source = (UMF_EVIDENCE / "source.umf.json").read_bytes()
assert hashlib.sha256(source).hexdigest() == (
    "9201dd239991e6bc42385edffaae94712dd12e8cbecd3706d172e127b2e0e4d8"
)
manifest_raw = (UMF_EVIDENCE / "manifest.json").read_bytes()
manifest_json = json.loads(manifest_raw)
assert manifest_json["artifactDigest"] == (
    "bf85f3e7008cb073cb9c757277556aba6c0e121d509e389cd0b14952762bbeda"
)
files = GeneratedFiles.from_mapping(
    {
        "algebra/read.json": (UMF_EVIDENCE / "algebra-read.json").read_bytes(),
        "native/native-table-source.json": (
            UMF_EVIDENCE / "native-table-source.json"
        ).read_bytes(),
    }
)
assert dict(files.inventory) == manifest_json["inventory"]
manifest = GeneratedManifest.from_json(manifest_raw)
trust_json = json.loads((UMF_EVIDENCE / "trusted-artifact.json").read_bytes())
receipt_json = json.loads((UMF_EVIDENCE / "receipt.json").read_bytes())
trusted = TrustedArtifactRef(
    artifact_id=trust_json["artifactId"],
    artifact_digest=trust_json["artifactDigest"],
    receipt_digest=trust_json["receiptDigest"],
    payload_digest=receipt_json["payloadDigest"],
    source_digest=trust_json["sourceDigest"],
    target_binding_digest=trust_json["targetBindingDigest"],
    inventory=tuple(tuple(row) for row in trust_json["inventory"]),
    issuer=trust_json["issuer"],
    build_id=trust_json["buildId"],
)
target_json = json.loads((UMF_EVIDENCE / "target.json").read_bytes())
target = TargetBinding(
    id=target_json["id"],
    profile=target_json["profile"],
    version=target_json["version"],
    binding_digest=target_json["bindingDigest"],
)
previous = json.loads(
    (ROOT / "tests/fixtures/prepared-api-v3-strict5-proof.json").read_bytes()
)
caps = dict(previous["capabilities"])
limits = {key: int(value) for key, value in previous["hostProfile"]["limits"]}
host = {
    "format": "lintel.host/1",
    "mount": previous["hostProfile"]["mount"],
    "introspection": previous["hostProfile"]["introspection"],
    "limits": limits,
}
exposure = (OUTPUT / "exposure.json").read_bytes()
prepared = prepare_api_v3(
    source,
    (),
    exposure,
    caps,
    host,
    previous["scalarCodecProfile"],
    manifest,
    files,
    trusted,
    target,
)
(OUTPUT / "prepared-api.json").write_bytes(prepared)
print(hashlib.sha256(prepared).hexdigest())
