# Lintel

Dynamic GraphQL + Relay APIs from UMF, with an embeddable Python/FastAPI runtime
and generated TypeScript operation/fragment artifacts for Batten applications.

## Install the experimental alpha

```sh
pip install lintel-api==0.1.0a1
```

Import `project` from `lintel.experimental.projection` and
`build_probe_schema` / `export_sdl` from `lintel.experimental.schema`.
These expose the bounded S-01 scalar projection: string, boolean, exact decimal
text and canonical UUID, with optional-field omission preserved. Supply UMF JSON
and explicit record/field references; the example below uses the task-board model
in the source distribution.

```python
from pathlib import Path
from lintel.experimental.projection import project
from lintel.experimental.schema import build_probe_schema

plan = project(
    Path("docs/helix/02-design/examples/task-board.umf.json").read_text(),
    ("board", "Task"), "Task", {("board", "title"): "title"},
)
schema = build_probe_schema(plan, {"title": "Fabricated task"})
assert schema.execute_sync("{ probe { title } }").data == {
    "probe": {"title": "Fabricated task"}
}
```

The alpha contains laboratory `probe` and `echo` roots. Do not mount them as a
production API. Native execution/admission, Relay identity/pagination, TypeScript
clients and Batten embedding are not provided by this wheel. Native qualification
harnesses and governed specifications are included in the source archive, without
installing PostgreSQL or its tools as library dependencies. Experimental APIs may
change between alpha releases. Python 3.11 is the initial qualified interpreter.

Lintel is a provisional name. This repository currently contains the HELIX
specifications and a bounded [direct UMF interoperability spike](docs/helix/02-design/spikes/SPIKE-001-direct-umf.md).
The spike reads UMF JSON through the public umf-core reader/validator and builds
a dynamic Strawberry schema. It is not a production API service.

Run `uv sync --locked --group spike --python 3.11`, then
`uv run --locked --group spike python -m spikes.direct_umf.run`.
[Verification and limits](docs/helix/04-build/direct-umf-spike.md) distinguish
this proof from native execution, Relay clients and Batten embedding.

Start with [the project packet](docs/helix/README.md),
[scope and MVP](docs/helix/01-frame/prd.md), and
[architecture](docs/helix/02-design/architecture.md).

The intended family documentation location is
[documentdrivendx.github.io/lintel](https://documentdrivendx.github.io/lintel/).
The [source repository](https://github.com/DocumentDrivenDX/lintel) is created;
family-catalog registration and documentation-site publication remain pending.


The [native read spike](docs/helix/02-design/spikes/SPIKE-002-native-reads.md)
measures pagination, declared-key batching and request consistency on disposable
PostgreSQL 18. Run `uv sync --locked --group spike --group native-spike`, then
`uv run --locked --group spike --group native-spike python -m spikes.native_reads.run`.
Use both dependency groups for `python scripts/check_quality.py` on the current tree.
[Results and gaps](docs/helix/04-build/native-read-spike.md) keep unsupported
execution guarantees explicit; no upstream schema API is introduced.
