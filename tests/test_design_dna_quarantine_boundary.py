"""DNA quarantine dependency-spread and compatibility-shim guard."""
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
THEME_STUDIO_SHIMS = (
    "ui/theme_studio/state.py",
    "ui/theme_studio/surface.py",
)
LEGACY_UI_DNA_SHIMS = tuple(
    f"ui/dna/{name}" for name in (
        "__init__.py", "bootstrap.py", "mapper.py", "models.py", "proofs.py", "registry.py", "resolver.py"
    )
)
LEGACY_UI_DNA_IMPL = tuple(
    f"dna_quarantine/legacy_ui_dna/{name}" for name in (
        "__init__.py", "bootstrap.py", "mapper.py", "models.py", "proofs.py", "registry.py", "resolver.py"
    )
)
Q1_INTEGRATION_COMMIT = "2354dfc2e7d5f38e7ffb373f22eee4d19e0fb51e"
Q1_ACC_PATH = "docs/design-dna/quarantine/Q1_ACC.yaml"


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
    assert LEGACY_PUBLIC_BRIDGE_FILES == {"app.py", "ui/presentation/brand.py", "ui/themes/registry.py"}
    assert len(LEGACY_PUBLIC_BRIDGE_FILES) == 3


def test_q1_theme_studio_real_implementation_is_quarantined():
    for rel in (
        "dna_quarantine/theme_studio/__init__.py",
        "dna_quarantine/theme_studio/state.py",
        "dna_quarantine/theme_studio/surface.py",
    ):
        assert (ROOT / rel).is_file(), rel


def test_q1_legacy_theme_studio_modules_are_thin_reexport_shims():
    for rel in THEME_STUDIO_SHIMS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert len(text) < 1500, f"{rel} regrew implementation: {len(text)} bytes"
        assert "dna_quarantine.theme_studio" in text
        assert "streamlit" not in text
        assert "st." not in text


def test_q2_legacy_ui_dna_real_implementation_is_quarantined_and_public_paths_are_shims():
    for rel in LEGACY_UI_DNA_IMPL:
        assert (ROOT / rel).is_file(), rel
        assert (ROOT / rel).stat().st_size > 100, rel
    for rel in LEGACY_UI_DNA_SHIMS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert len(text) < 500, f"{rel} regrew implementation: {len(text)} bytes"
        assert "dna_quarantine.legacy_ui_dna" in text
        assert "streamlit" not in text


def test_q2_public_shims_and_quarantine_exports_preserve_object_identity():
    from ui.dna.models import DesignDNA as PublicDesignDNA
    from dna_quarantine.legacy_ui_dna.models import DesignDNA as PrivateDesignDNA
    from ui.dna.registry import DNARegistry as PublicRegistry
    from dna_quarantine.legacy_ui_dna.registry import DNARegistry as PrivateRegistry
    assert PublicDesignDNA is PrivateDesignDNA
    assert PublicRegistry is PrivateRegistry


def test_q2_repaired_resolver_no_longer_self_imports_through_public_ui_dna_shims():
    path = ROOT / "dna_quarantine/legacy_ui_dna/resolver.py"
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
    assert all(not (name == "ui.dna" or name.startswith("ui.dna.")) for name in imports)
    assert "from .models import" in text
    assert "from .registry import get_registry as get_dna_registry" in text
    assert "from .mapper import dna_to_theme" in text
    assert text.index("def resolve_composition") < text.index("from ui.presentation.resolver import")


def test_quarantine_manifest_exists_and_locks_private_extraction_goal():
    text = (ROOT / "docs/design-dna/quarantine/DNA_QUARANTINE_MANIFEST.yaml").read_text(encoding="utf-8")
    assert "status: ACTIVE_QUARANTINE" in text
    assert "NO_NEW_DNA_DEPENDENCY_OUTSIDE_DECLARED_QUARANTINE_OR_PUBLIC_BRIDGE" in text
    assert "Q0_inventory_and_freeze:\n    status: COMPLETE" in text
    assert "Q1_theme_studio_move:\n    status: COMPLETE" in text
    assert f"integration_commit: {Q1_INTEGRATION_COMMIT}" in text
    assert f"acc_manifest: {Q1_ACC_PATH}" in text
    assert "Q2_legacy_ui_dna_move:\n    status: IMPLEMENTED_PENDING_ACCEPTANCE" in text
    assert "SOURCE_SNAPSHOT_MOVE_WITH_BOUNDED_IMPORT_CYCLE_REPAIR" in text
    assert "NON_RESOLVER_INTERNAL_LEGACY_SELF_IMPORTS_STILL_ROUTE_THROUGH_UI_DNA_SHIMS_UNTIL_Q4" in text
    assert "Q4_private_repository_cut:" in text


def test_q1_acc_manifest_matches_integrated_runtime_and_closed_state():
    text = (ROOT / Q1_ACC_PATH).read_text(encoding="utf-8")
    assert "status: ACC_CLOSED_INTEGRATED" in text
    assert "accepted: true" in text
    assert "closed: true" in text
    assert "integrated: true" in text
    assert f"integration_commit: {Q1_INTEGRATION_COMMIT}" in text
    assert "post_merge_exact_main:" in text
    assert "passed: 28299" in text
