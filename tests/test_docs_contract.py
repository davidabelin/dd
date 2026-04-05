"""Documentation contract tests for the Double-digits maintainer docs."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAINTAINER_DOCS = ROOT / "docs" / "maintainer"
MAINTAINER_FILES = (
    "README.md",
    "overview.md",
    "architecture.md",
    "interfaces.md",
    "models-and-artifacts.md",
    "operations.md",
)
PRODUCTION_ROOTS = (
    ROOT / "dd_core",
    ROOT / "dd_models",
    ROOT / "dd_visuals",
    ROOT / "dd_web",
    ROOT / "dd_cli",
)


def test_maintainer_index_links_required_pages():
    index = (MAINTAINER_DOCS / "README.md").read_text(encoding="utf-8")
    for name in MAINTAINER_FILES:
        assert (MAINTAINER_DOCS / name).exists()
        if name != "README.md":
            assert f"]({name})" in index


def test_production_modules_and_public_entrypoints_have_docstrings():
    python_files = [ROOT / "run.py"]
    for root in PRODUCTION_ROOTS:
        python_files.extend(sorted(root.rglob("*.py")))

    for path in python_files:
        module = ast.parse(path.read_text(encoding="utf-8"))
        assert ast.get_docstring(module), f"Missing module docstring: {path}"
        for node in module.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue
                assert ast.get_docstring(node), f"Missing function docstring: {path}:{node.name}"
            elif isinstance(node, ast.ClassDef):
                if node.name.startswith("_"):
                    continue
                assert ast.get_docstring(node), f"Missing class docstring: {path}:{node.name}"
                for child in node.body:
                    if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    if child.name.startswith("_") and child.name != "__init__":
                        continue
                    assert ast.get_docstring(child), f"Missing method docstring: {path}:{node.name}.{child.name}"
