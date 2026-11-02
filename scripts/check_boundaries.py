"""AST checks for the bounded S-01 spike; not a sandbox for untrusted code."""

from __future__ import annotations

import ast
from pathlib import Path

ALLOWED = {
    "projection": {"umf"},
    "schema": {"strawberry", "graphql", "spikes.direct_umf.projection"},
    "run": {
        "fastapi",
        "httpx",
        "strawberry.fastapi",
        "spikes.direct_umf.schema",
        "spikes.direct_umf.projection",
    },
}
STDLIB = {
    "__future__",
    "collections",
    "dataclasses",
    "hashlib",
    "importlib.metadata",
    "json",
    "pathlib",
    "re",
    "sys",
    "typing",
    "uuid",
    "asyncio",
}


def violations(source: str, module: str) -> list[str]:
    errors: list[str] = []
    for node in ast.walk(ast.parse(source)):
        imports: list[str] = []
        if isinstance(node, ast.Import):
            imports = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                errors.append("relative imports must use explicit module identity")
            imports = [node.module or ""]
            if any(alias.name.startswith("_") for alias in node.names):
                errors.append("private import")
        errors.extend(_dynamic_calls(node))
        for name in imports:
            if any(part.startswith("_") for part in name.split(".") if part != "__future__"):
                errors.append("private import")
            allowed = STDLIB | ALLOWED[module]
            if not any(name == prefix or name.startswith(prefix + ".") for prefix in allowed):
                errors.append("forbidden dependency: " + name)
    return errors


def _dynamic_calls(node: ast.AST) -> list[str]:
    if not isinstance(node, ast.Call):
        return []
    if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "__import__"}:
        return ["dynamic execution/import"]
    if isinstance(node.func, ast.Attribute) and node.func.attr == "import_module":
        return ["dynamic import"]
    return []


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for file in sorted((root / "spikes/direct_umf").glob("*.py")):
        if file.stem == "__init__":
            if file.read_text().strip():
                errors.append("package initializer must remain empty")
        elif file.stem not in ALLOWED:
            errors.append("unmapped source module: " + file.name)
        else:
            errors.extend(
                file.name + ": " + error for error in violations(file.read_text(), file.stem)
            )
    return errors


if __name__ == "__main__":
    failures = check(Path(__file__).resolve().parents[1])
    print("\n".join(failures) if failures else "S-01 import boundaries: PASS")
    raise SystemExit(bool(failures))
