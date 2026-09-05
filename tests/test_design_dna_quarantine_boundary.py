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
PUBLIC_BRIDGE_FILES = {"ui/dna_bridge.py"}
Q3_DECOUPLED_PUBLIC_SURFACES = (
    "app.py",
    "ui/presentation/brand.py",
    "ui/themes/registry.py",
)
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
Q2_INTEGRATION_COMMIT = "1377bc78d46fc129be074172380de3f17ba2b0a2"
Q2_ACC_PATH = "docs/design-dna/quarantine/Q2_ACC.yaml"
Q2_CLOSURE_COMMIT = "3b95ae1155bae7b5a37d646a46ba21c1964b6953"
M10_INTEGRATION_COMMIT = "40d4fd8a58a4d8cb4a2f29d89944cfbe1d0ed4cc"
M10_ACC_PATH = "docs/design-dna/migration/status/M10_ACC.yaml"
MIGRATION_STATUS_PATH = "docs/design-dna/migration/status/MIGRATION_STATUS.yaml"


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
        if _is_quarantine_path(rel) or rel in PUBLIC_BRIDGE_FILES:
            continue
        violations[rel] = imports
    assert violations == {}, (
        "DNA quarantine violation: deep DNA/Theme Studio import outside declared "
        f"quarantine or single public bridge: {violations}"
    )


def test_q3_public_bridge_allowlist_is_one_small_explicit_module():
    assert PUBLIC_BRIDGE_FILES == {"ui/dna_bridge.py"}
    assert len(PUBLIC_BRIDGE_FILES) == 1


def test_q3_former_public_bridge_owners_have_zero_deep_dna_imports():
    violations = {
        rel: _dna_imports(ROOT / rel)
        for rel in Q3_DECOUPLED_PUBLIC_SURFACES
        if _dna_imports(ROOT / rel)
    }
    assert violations == {}


def test_q3_bridge_private_imports_are_lazy_and_host_neutral():
    path = ROOT / "ui/dna_bridge.py"
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    assert "streamlit" not in text
    assert "reflex" not in text
    assert "dna_quarantine" in text

    top_level_private_imports = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("dna_quarantine"):
                top_level_private_imports.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("dna_quarantine"):
                    top_level_private_imports.append(alias.name)
    assert top_level_private_imports == []


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
    assert "Q2_legacy_ui_dna_move:\n    status: ACC_CLOSED_INTEGRATED" in text
    assert f"integration_commit: {Q2_INTEGRATION_COMMIT}" in text
    assert f"acc_manifest: {Q2_ACC_PATH}" in text
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


def test_q2_acc_manifest_matches_integrated_runtime_and_exact_main_proof():
    text = (ROOT / Q2_ACC_PATH).read_text(encoding="utf-8")
    assert "governor_status: ACC_CLOSED_INTEGRATED" in text
    assert "accepted: true" in text
    assert "closed: true" in text
    assert "integrated: true" in text
    assert f"integration_commit: {Q2_INTEGRATION_COMMIT}" in text
    assert "pull_request: 79" in text
    assert "post_merge_exact_main:" in text
    assert "ci_run: 95" in text
    assert text.count("passed: 30752") >= 2
    assert text.count("total: 30752") >= 2
    assert "pip_check: CLEAN" in text
    assert "next_gate: M10" in text
    assert "next_gate_authorized_by_this_manifest: false" in text


def test_m10_acc_manifest_matches_integrated_runtime_and_exact_main_proof():
    text = (ROOT / M10_ACC_PATH).read_text(encoding="utf-8")
    assert "batch: M10" in text
    assert "governor_status: ACC_CLOSED_INTEGRATED" in text
    assert "accepted: true" in text
    assert "closed: true" in text
    assert "integrated: true" in text
    assert f"integration_commit: {M10_INTEGRATION_COMMIT}" in text
    assert "pull_request: 81" in text
    assert "ci_run: 105" in text
    assert "ci_run: 106" in text
    assert text.count("passed: 37547") >= 2
    assert text.count("total: 37547") >= 2
    assert text.count("pip_check: CLEAN") >= 2
    assert "mr014: FIXED_MULTI_PANEL_STITCHED_APPLIQUE_WRAPPER" in text
    assert "mr021: FIXED_STRUCTURAL_WOODWORK_CONSERVATION_OPERATION" in text
    assert "eq4_credit: 0" in text
    assert "next_gate: Q3_THEME_BRIDGE_DECOUPLING" in text
    assert "next_gate_authorized_by_this_manifest: false" in text


def test_migration_master_ledger_cannot_regress_q2_or_m10_after_durable_closure():
    text = (ROOT / MIGRATION_STATUS_PATH).read_text(encoding="utf-8")
    assert f"authoritative_main_at_update: {M10_INTEGRATION_COMMIT}" in text
    assert "current_closed_batch: M10" in text
    assert "next_eligible_batch: M11" in text
    assert "quarantine_next_gate: Q3_THEME_BRIDGE_DECOUPLING" in text
    assert "Q2:\n    status: DURABLE_CLOSED" in text
    assert f"integration_commit: {Q2_INTEGRATION_COMMIT}" in text
    assert f"acc_manifest: {Q2_ACC_PATH}" in text
    assert "exact_main_tests: 30752" in text
    assert "exact_main_ci_run: 95" in text
    assert f"closure_commit: {Q2_CLOSURE_COMMIT}" in text
    assert "closure_pull_request: 80" in text
    assert "closure_exact_main_tests: 30754" in text
    assert "closure_exact_main_ci_run: 100" in text
    assert "M10:\n    governor_status: ACC_CLOSED_INTEGRATED" in text
    assert f"integration_commit: {M10_INTEGRATION_COMMIT}" in text
    assert "pull_request: 81" in text
    assert f"manifest: {M10_ACC_PATH}" in text
    assert "clean_head_tests: 37547" in text
    assert "clean_head_ci_run: 105" in text
    assert "exact_main_tests: 37547" in text
    assert "exact_main_ci_run: 106" in text
    assert "gate: Q3_THEME_BRIDGE_DECOUPLING" in text
    assert "then_gate: M11_FIXTURES_14" in text
    assert "credited: 0" in text
    assert "production_cutover: false" in text
