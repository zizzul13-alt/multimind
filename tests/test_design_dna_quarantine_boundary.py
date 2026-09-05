"""DNA quarantine dependency-spread guard.

This does not move the private implementation yet. It freezes the currently known
public/legacy import seams so M8-M12 cannot silently spread DNA/Theme Studio
knowledge into new application modules before private-repo extraction.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

QUARANTINE_PREFIXES = (
    "design_dna/",
    "dna_quarantine/",
    "ui/dna/",
    "ui/theme_studio/",
    "tests/",
)
LEGACY_PUBLIC_BRIDGE_FILES = {
    "app.py",
    "ui/presentation/brand.py",
    "ui/themes/registry.py",
}
DNA_MODULE_PREFIXES = (
    "design_dna",
    "ui.dna",
    "ui.theme_studio",
    "dna_quarantine",
)


def _python_files():
    for path in ROOT.rglob("*.py"):
        rel = path.relative_to(ROOT).as_posix()
        if any(part in {".git", ".venv", "venv", "__pycache__"} for part in path.parts):
            continue
        yield rel, path


def _dna_imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
    return tuple(
        item
        for item in imports
        if any(item == prefix or item.startswith(prefix + ".") for prefix in DNA_MODULE_PREFIXES)
    )


def _is_quarantine_path(rel: str) -> bool:
    return rel.startswith(QUARANTINE_PREFIXES)


def test_no_new_dna_or_theme_studio_dependency_spread_outside_declared_boundary():
    violations = {}
    for rel, path in _python_files():
        imports = _dna_imports(path)
        if not imports:
            continue
        if _is_quarantine_path(rel) or rel in LEGACY_PUBLIC_BRIDGE_FILES:
            continue
        violations[rel] = imports
    assert violations == {}, (
        "DNA quarantine violation: new deep DNA/Theme Studio import outside declared "
        f"quarantine or bridge seam: {violations}"
    )


def test_public_bridge_allowlist_is_small_and_explicit():
    assert LEGACY_PUBLIC_BRIDGE_FILES == {
        "app.py",
        "ui/presentation/brand.py",
        "ui/themes/registry.py",
    }
    assert len(LEGACY_PUBLIC_BRIDGE_FILES) == 3


def test_quarantine_manifest_exists_and_locks_private_extraction_goal():
    manifest = ROOT / "docs/design-dna/quarantine/DNA_QUARANTINE_MANIFEST.yaml"
    text = manifest.read_text(encoding="utf-8")
    assert "status: ACTIVE_QUARANTINE" in text
    assert "NO_NEW_DNA_DEPENDENCY_OUTSIDE_DECLARED_QUARANTINE_OR_PUBLIC_BRIDGE" in text
    assert "Q1_theme_studio_move:" in text
    assert "Q4_private_repository_cut:" in text
