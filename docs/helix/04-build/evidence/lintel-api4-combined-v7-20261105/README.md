# Lintel prepared API `/4` and Weft `/7` build evidence

## Scope

This receipt covers Lintel’s explicit `prepare_api_v4` build path and runtime
admission for one genuine Weft `/7` artifact. It does not qualify native Host
execution, ordinary Page plus Relay in one request, browser behavior, or a
production trust issuer. The upstream generated artifact carried a task-local
receipt. The API4 selection exposes only `demo.Note.owner`; `demo.Note.id` is
retained as the hidden string primary Key. The upstream Note Record has no
other fields in this fixture.

The API3 builder was run against the same artifact and refused it with
`UNSUPPORTED` at `generated read algebra profile`. API4 used the exact outer
`weft.generated-read-algebra/7` profile. API2/API3 formats and the API3 default
path remain unchanged; existing byte-pinned API2/API3 tests passed.

## Source and verifier inputs

The upstream source-built artifact was emitted from UMF build27 and Codegen
0.1.0a8 with Weft 0.4.66.dev1. Its upstream Weft wheel SHA-256 is
`1214a26beb73b351dcf7c684baf0465562e512798afe5138dce39d5ac1588660`. The
combined artifact reports source digest
`0a508516d89051e3d34d0203db278c6ad1f5a5b7651a04ffc8cfeaa76aed686f`, generated
bundle digest `4788ddf2c6b796a5e6fc375a173aff1ad84c2e5f01af3ba1451668f14b3f61fe`,
target binding digest
`3dc296a0e8c4b4243d4427dc8971a89fc3c3895fe11a10ab128ae5a269b9f740`,
artifact digest
`bd6a87dd7dcff4c35467f402ae5d4a79c736b64a642a7b3060798050895e259f`, receipt
digest `55fb4d4d5bf10ea173ed21b5e094578c425183b18d518c697f734ad3ba679d3e`,
payload digest
`16830430280c929dff84b954e0307d9aed215fedaa2498efe6f3fb5d9f1f5490`, and
algebra JSON digest
`9250d00b34aebc24ed2e2151c2c2279cc423639cc80a8594c797ac3ec0043c3b`.
The source-built artifact’s `demo/Note` root was marked eligible for both
ordinary Page and forward connection, but this Lintel build probe only verifies
the forward connection admission.

The verifier package was the provisional, source-built executor 0.1.0a9 wheel
at `/private/tmp/umf-access-generated-executor-a9-provisional-20261105/` with
SHA-256 `5b973058ac2bc9557c3460349fab6fde27e9f63bb913dd9db4b5f7ca3f66784a`.
The probe imported the verifier from that wheel path. It used `umf-core==0.10.0`
for the build-only UMF reader. `umf_access` runtime imports and Weft imports
were blocked and remained absent during Lintel admission. The executor wheel is
provisional pending its separate review; this receipt does not freeze its
package version.

The selected capabilities include `binding.profile=pg18/1`,
`connection.forward=edge-cursor-1`, `identity.codec=lintel.node-id.string-key/1`,
`read.consistency=request-snapshot-1`,
`operation.binding/demo/Note/record=pg18/1`, and
`scalar.codec.profile=lintel.scalars/1`, plus the host-bound limit pairs from
the selected host profile. The generated connection row joins the selected
Record, hidden primary Key `demo.id`, visible Field `demo.owner`, source digest,
artifact and receipt digests, target binding digest, and algebra digest.

## API4 artifact

The emitted and runtime-admitted artifact is preserved at
[`prepared-api-v4-weft7-build27-proof.json`](../../../../tests/fixtures/prepared-api-v4-weft7-build27-proof.json)
with test-only prepared-artifact pins at
[`prepared-api-v4-weft7-build27-trust.json`](../../../../tests/fixtures/prepared-api-v4-weft7-build27-trust.json).

- Prepared artifact SHA-256: `0db3dd875e9255e9b2635d37392a8e870683e6fc7fbb9cba8bb90f4dfef37bff`
- `apiDigest`: `c2713e1ac02f5766cc220eabf930830a67071384c1ab65b02a019caf1b8f53b5`
- `schemaDigest`: `e47e1f2a23d1edd26a0553040437eb101d44fee17daea4926602fbf165f05129`
- Artifact version: `lintel.prepared-api/4`
- Exact connection `readProfile`: `weft.generated-read-algebra/7`

The test validates the closed API4 JSON Schema, loads the prepared artifact
through the nominal runtime loader, checks API3 `/5` versus API4 `/7` codec
refusals, and assembles the API4 router with the exact generated string-Key
validator registry.

## Candidate distributions

The API4 candidate distributions are local unpublished outputs in
`/private/tmp/lintel-api4-a5-a4-provisional2-20261105/`, built with Hatchling
1.33.0. Their bytes are candidates, not frozen release inputs.

| Distribution | SHA-256 |
| --- | --- |
| `lintel_api-0.1.0a5-py3-none-any.whl` | `e90e5109d219c70c1a8f796572531d849f80705e7a23316923aa2d7f7e169aae` |
| `lintel_api-0.1.0a5.tar.gz` | `3a3a6e9bebd1951547bfe79b1e1a4e8c523e639ce31cad76ef042a70e0dc12be` |
| `lintel_api_build-0.1.0a4-py3-none-any.whl` | `4bd311e67bece28123746ee5e6f750d5912bee6c6baee7b3d415ce97814ccfcb` |
| `lintel_api_build-0.1.0a4.tar.gz` | `9799836a5f3043db17d9f7a63e9d5903741e39422939f0353c349ce7786d193a` |

The runtime wheel has 19 Python modules, byte-identical to the current
`src/lintel` files. The build wheel has nine `lintel_build` modules. Runtime and
build wheel module inventories do not overlap; the two sdist module inventories
also do not overlap. Runtime wheel metadata requires only FastAPI 0.135.1,
GraphQL Core 3.3.1, and Strawberry GraphQL 0.339.1. It contains no UMF,
Weft, executor, or build-package dependency. The build wheel requires Lintel
API a5, UMF Core 0.10.0, and the provisional executor a9.

The runtime wheel was imported directly from its wheel path with imports of
UMF and `lintel_build` blocked. The API4 artifact was loaded, its router was
assembled, and a synthetic neutral execution port served one GraphQL connection
request with HTTP 200. This checks the generic runtime route only; it is not a
native execution claim.

## Quality

The command `./.venv/bin/python scripts/check_quality.py` passed: Ruff, Ruff
format, Pyright (zero errors, zero warnings, zero information), boundary checks,
and 97 tests. One existing Starlette/httpx deprecation warning was reported by
the test client. The captured output is in [`quality.stdout.txt`](quality.stdout.txt).

Probe commands and outputs are preserved beside this receipt as `.py.txt` and
`.stdout.txt` files. The source fixture and prepared artifact trust files are
test fixtures; they are not production trust material.
