# Lintel prepared API `/3` a4/a3 candidate wheel evidence

Captured 2026-11-05. This receipt covers the Lintel API3 source gate, candidate
package construction, wheel payload identity, and compiler-free runtime
admission/router creation. It does not qualify Batten's native adapter, a live
HTTP request, a PostgreSQL execution, whole-process peak memory, publication,
or deployment.

## Governing scope and pins

The prepared `/3` shape and `/5` joins are governed by
[CONTRACT-006](../../../02-design/contracts/CONTRACT-006-prepared-api-build-runtime.md)
and the
[API3 strict `/5` build/admission receipt](../prepared-api-v3-strict5.md).
The exact prepared API3 proof artifact is SHA-256
`1126ea1bd72e2925bd994d0c80f645aa8d8f28229d3d66e666c4b66f5767e053`, with API
digest `df8642490abd76e8e3597b96080bf4e7609aeaecb0fbab6b6848076bce52c303`.
The unchanged API2 baseline fixture is SHA-256
`53fa234381c5339d4c810f702b9b09fc3d6ec720adb252ba077205cae00414dc`, API digest
`3a58d05f097f5feeb7ce55598711c260d101bf59c9de77f38a89a0e9d9ef1935`.

The runtime distribution is `lintel-api==0.1.0a4`, with exact requirements
FastAPI 0.135.1, Strawberry GraphQL 0.339.1, and graphql-core 3.3.1. Its
runtime dependency boundary contains no UMF, Weft, generated-executor, codegen,
or Lintel build package. The build distribution is `lintel-api-build==0.1.0a3`
and pins `lintel-api==0.1.0a4`, `umf-core==0.10.0`,
`umf-access-generated-executor==0.1.0a7`, and `graphql-core==3.3.1`.

## Artifacts and verification

Candidate wheels and sdists remain in the temporary candidate directory; no
wheel binary is copied into this governed evidence folder. The checksummed
[`candidate-manifest.json`](candidate-manifest.json) records all four artifact
hashes and exact wheel `Requires-Dist` metadata.
[`payload-hashes-and-runtime.json`](payload-hashes-and-runtime.json) records
every runtime/build wheel payload file's SHA-256 and source path, package
origins/versions in the isolated runtime site, and the admission check results.
All 18 runtime payload files and all 8 build payload files match their source
bytes exactly.

The isolated runtime site is
`/private/tmp/lintel-api-a4-runtime-site-20261105`. Python ran with `-S` and
loaded the candidate runtime and selected runtime dependency closure from that
site. API3 strict `/5` and API2 baseline fixtures both admitted; bare
`StringKeyNodeCodec` instances were refused, while codecs registered against
the exact prepared root Key validators allowed router construction. The
following imports were absent: `umf_access`,
`umf_access_generated_executor`, `umf_access_build`, `weft_sql`, `umf_codegen`,
and `lintel_build`. This is admission/router evidence only; no request was
sent through Batten or a native database.

The source quality command was `.venv/bin/python scripts/check_quality.py`.
It passed formatting/checks, Pyright with zero errors, import boundaries, and
96 tests (one existing Starlette/httpx deprecation warning).

## Byte and result limits

The separate accounting layers remain: native result-frame limit of 8 MiB per
frame; Batten serialized selected outcomes charged across the operation
against prepared `responseBytes`; and Lintel's final UTF-8 GraphQL response cap
before request-session release. These checks do not establish an 8 MiB
process-memory peak.

## Native-spike lock follow-up

The optional native-spike group and `uv.lock` still name UMF access dev8,
UMF codegen a5, and Weft .4.54. The approved current candidate cohort is
available only through local wheel inputs at capture time. The lock remains
unchanged because embedding temporary local wheel paths would make it
non-portable. A portable lock refresh should follow the cross-repository
candidate freeze that supplies stable public artifact URLs or index entries;
then update only the native-spike cohort pins and regenerate the lock while
preserving unrelated library versions.
