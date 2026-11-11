# Working in Lintel

- Setup and checks: `uv sync --locked`, then `uv run ruff check . && uv run ruff format --check .`,
  `uv run pyright`, `uv run python scripts/check_boundaries.py`, `uv run pytest -q`.
- Layout: `lintel.ports` (neutral host contract), `lintel.graphql` / `lintel.projection`
  (runtime), `lintel.build` (needs `umf`), `lintel.memory` / `lintel.app` / `lintel.cli`
  (demo server), `lintel.experimental` (laboratory, not a product API).
- Import rule: the runtime (`lintel.graphql`, `lintel.projection`, `lintel.memory`,
  `lintel.app`, `lintel.trust`) must not import `umf`, `lintel.build` or `strawberry`.
  Lintel must not import Batten.
- Lintel consumes UMF; it does not define UMF semantics. Keep claims in docs to what CI tests.
- No evidence, receipts, qualification packets or candidate artifacts in git; tests and CI
  are the gate. `docs/helix/` is design background, not a deliverable to extend.
- The README quickstart is executed by `scripts/smoke_installed.py`: keep them in step.
