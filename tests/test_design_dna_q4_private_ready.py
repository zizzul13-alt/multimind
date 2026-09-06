"""Q4 extraction-readiness guards for the quarantined/private Design-DNA candidate."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOTS = (ROOT / "design_dna", ROOT / "dna_quarantine")
REVERSE_SHIM_PREFIXES = ("ui.dna", "ui.theme_studio")
FORBIDDEN_APPLICATION_PREFIXES = ("core", "providers", "database")
INVENTORY = ROOT / "docs/design-dna/quarantine/PRIVATE_EXTRACTION_INVENTORY.yaml"


def _imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            result.append(node.module)
        elif isinstance(node, ast.Import):
            result.extend(alias.name for alias in node.names)
    return tuple(result)


def _private_python_files():
    for root in PRIVATE_ROOTS:
        for path in root.rglob("*.py"):
            if "__pycache__" not in path.parts:
                yield path


def _matches(name: str, prefix: str) -> bool:
    return name == prefix or name.startswith(prefix + ".")


def test_private_candidate_has_no_reverse_import_through_legacy_public_shims():
    violations = {}
    for path in _private_python_files():
        bad = tuple(
            name for name in _imports(path)
            if any(_matches(name, prefix) for prefix in REVERSE_SHIM_PREFIXES)
        )
        if bad:
            violations[path.relative_to(ROOT).as_posix()] = bad
    assert violations == {}


def test_private_candidate_does_not_pull_provider_core_or_database_layers_into_dna():
    violations = {}
    for path in _private_python_files():
        bad = tuple(
            name for name in _imports(path)
            if any(_matches(name, prefix) for prefix in FORBIDDEN_APPLICATION_PREFIXES)
        )
        if bad:
            violations[path.relative_to(ROOT).as_posix()] = bad
    assert violations == {}


def test_theme_studio_implementation_is_quarantine_owned_and_bypasses_public_shims():
    state = (ROOT / "dna_quarantine/theme_studio/state.py").read_text(encoding="utf-8")
    surface = (ROOT / "dna_quarantine/theme_studio/surface.py").read_text(encoding="utf-8")
    assert "dna_quarantine.legacy_ui_dna" in state
    assert "dna_quarantine.legacy_ui_dna" in surface
    assert "from dna_quarantine.theme_studio.state import" in surface
    assert "from ui.dna" not in state
    assert "from ui.dna" not in surface
    assert "from ui.theme_studio" not in state
    assert "from ui.theme_studio" not in surface


def test_legacy_ui_dna_package_self_imports_are_private_relative_imports():
    package = ROOT / "dna_quarantine/legacy_ui_dna"
    for name in ("__init__.py", "bootstrap.py", "mapper.py", "proofs.py", "registry.py", "resolver.py"):
        text = (package / name).read_text(encoding="utf-8")
        assert "from ui.dna" not in text, name


def test_public_legacy_paths_remain_thin_compatibility_shims():
    for rel in (
        "ui/dna/__init__.py", "ui/dna/bootstrap.py", "ui/dna/mapper.py", "ui/dna/models.py",
        "ui/dna/proofs.py", "ui/dna/registry.py", "ui/dna/resolver.py",
        "ui/theme_studio/state.py", "ui/theme_studio/surface.py",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert len(text) < 1500, rel
        assert "dna_quarantine" in text, rel


def test_private_extraction_inventory_is_complete_and_not_an_extraction_overclaim():
    text = INVENTORY.read_text(encoding="utf-8")
    for category in (
        "runtime_private_owned:", "legacy_public_compatibility_shims:", "public_bridge:",
        "host_owned_consumers:", "private_owned_tests:", "private_owned_docs:",
        "canonical_fixtures:", "asset_policy_and_manifests:",
    ):
        assert category in text
    assert "q4_state: PRIVATE_READY" in text
    assert "q4_state: PRIVATE_READY_CANDIDATE_AWAITING_GOVERNOR_ACC" not in text
    assert "actual_private_repository_extraction_completed: false" in text
    assert "public_history_sanitized: false" in text
    assert "final_approved_count: 0" in text
    assert "moving_files_does_not_erase_public_git_history: true" in text
    assert "destructive_history_rewrite_authorized: false" in text


def test_q2_deferred_reverse_import_debt_is_explicitly_resolved_at_q4():
    text = (ROOT / "docs/design-dna/quarantine/DNA_QUARANTINE_MANIFEST.yaml").read_text(encoding="utf-8")
    assert "RESOLVED_AT_Q4_PRIVATE_READY_CUT__NO_INTERNAL_REVERSE_IMPORT_THROUGH_UI_DNA_OR_UI_THEME_STUDIO_SHIMS" in text
    assert "NON_RESOLVER_INTERNAL_LEGACY_SELF_IMPORTS_STILL_ROUTE_THROUGH_UI_DNA_SHIMS_UNTIL_Q4" not in text


def test_public_dna_bridge_safe_fallback_survives_private_candidate_absence(monkeypatch):
    import ui.dna_bridge as bridge

    real_import = bridge.import_module

    def without_private_candidate(name: str):
        if name.startswith("dna_quarantine"):
            raise ModuleNotFoundError(name)
        return real_import(name)

    monkeypatch.setattr(bridge, "import_module", without_private_candidate)
    assert bridge.dna_available() is False
    assert bridge.ensure_dna_registered() is False
    material = bridge.resolve_material("anything")
    identity = bridge.resolve_identity_projection(None)
    assert material.status == "fallback"
    assert material.is_resolved is False
    assert identity.hierarchy_contrast == "strong"
    assert bridge.theme_studio_available() is False


def test_bridge_itself_does_not_eagerly_import_private_candidate():
    path = ROOT / "ui/dna_bridge.py"
    imports = _imports(path)
    assert all(not name.startswith("dna_quarantine") for name in imports)
