---
ddx:
  id: SPIKE-001
  type: tech-spike
  activity: design
  authoring:
    home: repo
  links:
    - id: TD-001
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
---

# S-01: Direct UMF to dynamic GraphQL

## Objective

Can Python consume the existing UMF JSON directly and construct/query/export a
Strawberry schema without generated Python clients or another schema API?

Bound the first probe to core 0.10.0 scalar record projections, deterministic SDL,
qualified references, name refusal, Decimal/UUID codecs and input omission/null.
The fabricated task-board source is the existing governed example. Probe roots
are harness conveniences, not invented UMF operation declarations or a shippable
API. Native execution, Relay identity/edges, browser clients and hosting authority
remain S-02–05. This probe is a bounded part of S-01, not all US-001 conformance.

## Hypothesis

The published umf-core public reader and validator already supply the necessary
model input. Lintel needs GraphQL projection code, not new UMF schema machinery.

## Approach

1. Establish a source module map and AST import checker with forbidden controls.
2. Install a locked Python 3.11 cohort; read/validate original UMF through its
   public Python functions and retain its original supplied source text.
3. Select explicit record/member references and map the bounded subset to dynamic
   Strawberry output/input types. Retain tri-state input presence.
4. Export sorted SDL, run exact-value and refusal tests, and exercise a real
   in-process FastAPI HTTP request using the same schema.
5. Record evidence and make upstream changes only for demonstrated missing
   capabilities. Do not infer native runtime qualification from fabricated rows.

## Findings

**FINDING 1**: Published umf-core 0.10.0 already reads and validates the model
through public functions. No access-description API, generated client or upstream
source modification is needed for this subset.

**FINDING 2**: Dynamic Strawberry types preserve exact Decimal/UUID string carriers
and input omission/null. GraphQL names require independent safe Python attribute
names; Lintel maps those locally rather than imposing Python naming on UMF.
The 40-case corpus and FastAPI query provide the evidence below.

Execution results and cohort: [S-01 evidence](../../04-build/evidence/s01-direct-umf.json).
Verification and limitations: [execution record](../../04-build/direct-umf-spike.md).

## Analysis

**Hypothesis**: confirmed for the bounded scalar-only probe.

The spike deliberately refuses incomplete UMF validation globally. Production
preparation must distinguish selected from unrelated unknown meanings using UMF
validation/interpretation; this conservative spike does not establish that wider
behavior. It checks selected element shape so future semantics cannot disappear.
Source text remains retained unchanged. Decimal precision/scale are retained in
UMF; native domain enforcement is not demonstrated by the lexical codec probe.

## Conclusions

The passing run proves direct UMF scalar projection and the exercised framework
integration. It does not qualify the task-board's undeclared operation bindings.

## Recommendations

**RECOMMENDATION**: Continue using UMF JSON as the schema authority. Reuse public read_document and
validate_document. Determine native execution gaps through S-02/S-03 before
changing the runtime. No concern selection changes follow from this probe.

Confidence is high for the exercised subset; remaining S-01 operation/closure
qualification and native execution are separate. Do not make UMF/runtime changes
on the strength of this scalar-only result.

## Artifacts

- `spikes/direct_umf/projection.py`: UMF boundary and bounded projection.
- `spikes/direct_umf/schema.py`: Strawberry construction and lexical codecs.
- `spikes/direct_umf/run.py`: fabricated FastAPI transport proof and receipt.
- `scripts/check_boundaries.py`, `tests/test_boundaries.py`: real source checks.
- `tests/test_direct_umf.py`: observable projection/coercion/refusal controls.
- [Strawberry schema API](https://strawberry.rocks/docs/types/schema) and
  [scalar API](https://strawberry.rocks/docs/types/scalars): primary framework references.
