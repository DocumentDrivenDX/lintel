"""AST checks for bounded interoperability spikes; not a sandbox for untrusted code."""

from __future__ import annotations

import ast
from pathlib import Path

ALLOWED: dict[str, set[str]] = {
    "root": {"lintel.ports", "lintel"},
    "ports": {"lintel.ports"},
    "ports_values": set(),
    "ports_errors": set(),
    "ports_protocols": {"lintel.ports.values"},
    "request_qualify": {"spikes.native_reads.fixture", "umf_access.unified", "psycopg"},
    "native_fixture": {
        "umf_codegen",
        "umf_access.lifecycle",
        "umf_access.unified",
        "psycopg",
        "pgserver",
    },
    "native_probes": {"spikes.native_reads.fixture", "umf_access.unified", "psycopg"},
    "native_run": {"spikes.native_reads.fixture", "spikes.native_reads.probes"},
    "projection": {"umf"},
    "schema": {"strawberry", "graphql", "lintel.experimental.projection"},
    "run": {
        "fastapi",
        "httpx",
        "strawberry.fastapi",
        "lintel.experimental.schema",
        "lintel.experimental.projection",
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
    "contextlib",
    "tempfile",
    "copy",
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
            if name.startswith("umf_access.") and name not in {
                "umf_access.unified",
                "umf_access.lifecycle",
            }:
                errors.append("non-public runtime submodule")
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
    errors = violations((root / "src/lintel/__init__.py").read_text(), "root")
    for folder, prefix in (
        ("spikes/direct_umf", ""),
        ("src/lintel/experimental", ""),
        ("src/lintel/ports", "ports_"),
        ("spikes/native_reads", "native_"),
        ("spikes/request_reads", "request_"),
    ):
        for file in sorted((root / folder).glob("*.py")):
            module = prefix + file.stem
            if file.stem == "__init__" and prefix == "ports_":
                errors.extend(file.name + ": " + e for e in violations(file.read_text(), "ports"))
            elif file.stem == "__init__":
                if file.read_text().strip():
                    errors.append("package initializer must remain empty")
            elif module not in ALLOWED:
                errors.append("unmapped source module: " + file.name)
            else:
                errors.extend(file.name + ": " + e for e in violations(file.read_text(), module))
    return errors


if __name__ == "__main__":
    failures = check(Path(__file__).resolve().parents[1])
    print("\n".join(failures) if failures else "Spike import boundaries: PASS")
    raise SystemExit(bool(failures))
