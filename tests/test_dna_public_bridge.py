"""Public DNA bridge: optional-package and safe-fallback contract."""
from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import ui.dna_bridge as bridge

ROOT = Path(__file__).resolve().parents[1]


def _missing_private_package(name: str):
    if name.startswith("dna_quarantine"):
        raise ModuleNotFoundError(name)
    raise AssertionError(f"unexpected import: {name}")


def _broken_private_package(_name: str):
    raise RuntimeError("incompatible private package")


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


def _assert_neutral_fallback():
    assert bridge.dna_available() is False
    assert bridge.ensure_dna_registered() is False
    assert bridge.resolve_source_dna("anything") is None
    assert bridge.list_theme_studio_dna_options("identity") == ()
    assert bridge.list_theme_studio_dna_options("web_information") == ()
    assert bridge.resolve_theme_studio_composition("identity", None, "chat_first") is None

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


def test_missing_private_dna_is_a_valid_boring_fallback(monkeypatch):
    monkeypatch.setattr(bridge, "import_module", _missing_private_package)
    _assert_neutral_fallback()


def test_broken_or_incompatible_private_import_is_a_valid_boring_fallback(monkeypatch):
    monkeypatch.setattr(bridge, "import_module", _broken_private_package)
    _assert_neutral_fallback()


def test_private_runtime_operation_failures_do_not_escape_bridge(monkeypatch):
    broken_resolver = SimpleNamespace(
        resolve_material=lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("material boom")),
        resolve_source_dna=lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("source boom")),
        resolve_identity_projection=lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("projection boom")),
    )
    broken_bootstrap = SimpleNamespace(
        ensure_proof_dna_and_themes_registered=lambda: (_ for _ in ()).throw(RuntimeError("bootstrap boom"))
    )

    def importer(name: str):
        if name.endswith("resolver"):
            return broken_resolver
        if name.endswith("bootstrap"):
            return broken_bootstrap
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(bridge, "import_module", importer)
    assert bridge.dna_available() is True
    assert bridge.ensure_dna_registered() is False
    assert bridge.list_theme_studio_dna_options("identity") == ()
    assert bridge.resolve_theme_studio_composition("identity", None, "chat_first") is None
    assert bridge.resolve_source_dna("anything") is None
    assert bridge.resolve_material("anything").status == "fallback"
    assert isinstance(bridge.resolve_identity_projection(None), bridge.FallbackIdentityProjection)


def test_theme_studio_catalog_and_projection_cross_bridge_as_host_safe_values(monkeypatch):
    bootstrap = SimpleNamespace(ensure_proof_dna_and_themes_registered=lambda: None)
    legacy = SimpleNamespace(
        list_dna=lambda: [
            SimpleNamespace(id="rinpa-decorative-spatial", display_name="Rinpa Decorative Spatial", role="identity", category="cultural"),
            SimpleNamespace(id="japan-print-ink", display_name="Japan Print / Ink", role="identity", category="cultural"),
            SimpleNamespace(id="japan-high-density-info", display_name="Japan High-Density Information", role="web_information", category="cultural_web"),
        ]
    )
    policy = SimpleNamespace(
        metadata_prominence="high",
        status_richness="rich",
        navigation_density="compact",
        secondary_compactness=True,
        information_discoverability="enhanced",
        utility_grouping="structured",
    )
    identity_projection = SimpleNamespace(
        hierarchy_contrast="strong",
        border_stroke_style="soft",
        energy_emphasis="expressive",
        surface_treatment="layered",
        transition_speed="deliberate",
    )
    projection = SimpleNamespace(
        archetype_id="chat_first",
        provenance={
            "identity_display_name": "Rinpa Decorative Spatial",
            "web_information_display_name": "Japan High-Density Information",
        },
        presentation_policy=policy,
        identity_projection=identity_projection,
    )
    draft = SimpleNamespace(
        identity_dna_id="rinpa-decorative-spatial",
        web_information_dna_id="japan-high-density-info",
        colors={"background": "#f2ece1", "primary": "#b8860b"},
        typography={"font_family_base": "Georgia, serif"},
        spacing={"md": "1rem"},
        radius={"md": "4px"},
        resolve=lambda: projection,
    )
    theme_state = SimpleNamespace(init_draft_from_composition=lambda **_kwargs: draft)
    resolver = SimpleNamespace()

    def importer(name: str):
        if name.endswith("bootstrap"):
            return bootstrap
        if name == "dna_quarantine.legacy_ui_dna":
            return legacy
        if name == "dna_quarantine.legacy_ui_dna.resolver":
            return resolver
        if name == "dna_quarantine.theme_studio.state":
            return theme_state
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(bridge, "import_module", importer)

    identity_options = bridge.list_theme_studio_dna_options("identity")
    assert [item.id for item in identity_options] == ["japan-print-ink", "rinpa-decorative-spatial"]
    assert all(item.role == "identity" for item in identity_options)
    web_options = bridge.list_theme_studio_dna_options("web_information")
    assert [item.id for item in web_options] == ["japan-high-density-info"]

    result = bridge.resolve_theme_studio_composition(
        "rinpa-decorative-spatial",
        "japan-high-density-info",
        "chat_first",
    )
    assert isinstance(result, bridge.ThemeStudioProjection)
    assert result.identity_display_name == "Rinpa Decorative Spatial"
    assert result.web_information_display_name == "Japan High-Density Information"
    assert result.colors["primary"] == "#b8860b"
    assert result.presentation_policy["navigation_density"] == "compact"
    assert result.identity_projection["surface_treatment"] == "layered"


def test_broken_theme_studio_render_uses_host_fallback(monkeypatch):
    broken_surface = SimpleNamespace(
        render_theme_studio_surface=lambda: (_ for _ in ()).throw(RuntimeError("render boom"))
    )
    monkeypatch.setattr(bridge, "import_module", lambda _name: broken_surface)
    calls = []
    monkeypatch.setattr(bridge, "_render_theme_studio_fallback", lambda: calls.append("fallback"))

    assert bridge.render_theme_studio_surface() is False
    assert calls == ["fallback"]


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
