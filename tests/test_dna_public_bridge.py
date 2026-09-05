"""Q3 public DNA bridge: optional-package and safe-fallback contract."""
from __future__ import annotations

import ast
from pathlib import Path

import ui.dna_bridge as bridge

ROOT = Path(__file__).resolve().parents[1]


def _missing_private_package(name: str):
    if name.startswith("dna_quarantine"):
        raise ModuleNotFoundError(name)
    raise AssertionError(f"unexpected import: {name}")


def test_bridge_has_no_eager_private_or_legacy_dna_imports():
    path = ROOT / "ui/dna_bridge.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
    assert all(
        not name.startswith(("design_dna", "dna_quarantine", "ui.dna", "ui.theme_studio"))
        for name in imports
    )


def test_missing_private_dna_is_a_valid_boring_fallback(monkeypatch):
    monkeypatch.setattr(bridge, "import_module", _missing_private_package)

    assert bridge.dna_available() is False
    assert bridge.ensure_dna_registered() is False
    assert bridge.resolve_source_dna("anything") is None

    material = bridge.resolve_material("anything")
    assert material.status == "fallback"
    assert material.is_resolved is False
    assert material.resolved_path is None

    projection = bridge.resolve_identity_projection(None)
    assert projection.hierarchy_contrast == "strong"
    assert projection.border_stroke_style == "solid"
    assert projection.energy_emphasis == "balanced"
    assert projection.surface_treatment == "flat"
    assert projection.transition_speed == "deliberate"

    assert bridge.theme_studio_available() is False


def test_public_bridge_is_the_only_host_facing_dna_dependency():
    expected = {
        "app.py",
        "ui/presentation/brand.py",
        "ui/themes/registry.py",
    }
    for rel in expected:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "ui.dna_bridge" in text
        assert "from ui.dna." not in text
        assert "from ui.theme_studio" not in text
        assert "from dna_quarantine" not in text
        assert "from design_dna" not in text
