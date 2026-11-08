# Lintel API4 `/7` recheck with the updated executor a9 candidate

This follow-up reissues the same one-field API4 artifact with the updated UMF
executor a9 wheel that adds the public `ordinary_page_roots` protocol property.
The earlier receipt at
[`lintel-api4-combined-v7-20261105`](../lintel-api4-combined-v7-20261105/README.md)
remains unchanged and records the earlier provisional executor hash. This
follow-up does not replace that chronology or claim the new executor is final.

## Inputs and environment

- Executor wheel:
  `/Users/erik/Projects/umf/docs/helix/04-build/evidence/generated-ordinary-page-v7-package-candidate-20261105/dist/executor/umf_access_generated_executor-0.1.0a9-py3-none-any.whl`
  SHA-256 `ee5e63e01b1d48518645467cb64749622da574a1feff51dd7a281e8d25d863a2`.
- Lintel runtime wheel a5 SHA-256
  `e90e5109d219c70c1a8f796572531d849f80705e7a23316923aa2d7f7e169aae`.
- Lintel build wheel a4 SHA-256
  `4bd311e67bece28123746ee5e6f750d5912bee6c6baee7b3d415ce97814ccfcb`.
- Python: CPython 3.11.17 in a new venv at
  `/private/tmp/lintel-api4-a5-a4-ex9-recheck-20261105/env`.
- The venv contains the exact Lintel runtime/build wheels and executor candidate.
  GraphQL Core, UMF Core and their Python dependencies were resolved from a
  task-local symlink overlay of `/private/tmp/batten-candidate-full-20261105`;
  UMF Core source was explicitly available at
  `/Users/erik/Projects/umf/python/src`. This is isolated from the global Lintel
  and Batten environments, though its transitive build dependencies come from
  that pinned local candidate environment rather than a newly resolved lock.
- `umf_access` runtime imports and Weft imports were blocked by the probe and
  remained absent. The executor origin was the updated wheel path above; Lintel
  runtime/build origins were the fresh venv's site-packages.

The archived probe source is `builder-probe.py.txt`. Its effective invocation
was:

```sh
PYTHONPATH=/private/tmp/umf-page7-package-candidates-20261105/executor-protocolfix/umf_access_generated_executor-0.1.0a9-py3-none-any.whl:/private/tmp/lintel-api4-a5-a4-ex9-recheck-20261105/dependency-overlay:/Users/erik/Projects/umf/python/src \
  /private/tmp/lintel-api4-a5-a4-ex9-recheck-20261105/env/bin/python \
  /private/tmp/lintel-api4-a5-a4-ex9-recheck-20261105/builder_probe.py
```

The output is preserved in `builder-probe.stdout.txt` (SHA-256
`45996744c4121fcc19f478feef4314f5da12c25cb9d9b023dd1bb03407396334`). The
updated executor reports `weft.generated-read-algebra/7`; API3 refuses with
`UNSUPPORTED` at `generated read algebra profile`. API4 emits
`lintel.prepared-api/4` with exact read profile `/7`.

## Reproduction result

The output artifact and trust pin are byte-identical to the accepted API4
fixture. Artifact SHA-256 is
`0db3dd875e9255e9b2635d37392a8e870683e6fc7fbb9cba8bb90f4dfef37bff`,
`apiDigest` is
`c2713e1ac02f5766cc220eabf930830a67071384c1ab65b02a019caf1b8f53b5`, and
`schemaDigest` is
`e47e1f2a23d1edd26a0553040437eb101d44fee17daea4926602fbf165f05129`. The
output artifact and trust pin hashes are respectively
`0db3dd875e9255e9b2635d37392a8e870683e6fc7fbb9cba8bb90f4dfef37bff` and
`6a29af830cbda5b814c8cf9cd60997d0076a27e8d55af945cb711b71f408a7c9`.

The wheel/source comparison in `wheel-source-match.stdout.json` reports all 19
runtime modules and all nine build modules byte-identical to current source.
The Lintel wheel hashes are unchanged from the accepted API4 candidate.

The upstream combined `/7` artifact and task-local receipt are still the same
source-built fixture described by the earlier receipt. This recheck covers only
builder admission and reproducibility. It does not qualify native Host/Page
execution, browser behavior, deployment, or production trust issuance.
