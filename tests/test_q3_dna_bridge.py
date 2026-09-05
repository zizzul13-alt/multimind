"""Q3 optional DNA bridge torture and safe-default contract tests."""
from __future__ import annotations

import builtins

import pytest

from ui import dna_bridge


def _block_private_imports(monkeypatch, *, unrelated_name: str | None = None):
    original_import = builtins.__import__

    def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "dna_quarantine" or name.startswith("dna_quarantine."):
            missing_name = unrelated_name or name
            exc = ModuleNotFoundError(f"No module named '{missing_name}'")
            exc.name = missing_name
            raise exc
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", blocked_import)


def test_bridge_safe_default_contract_is_small_deterministic_and_public():
    material = dna_bridge.BridgeMaterialResult()
    identity = dna_bridge.BridgeIdentityProjection()

    assert material.status == "fallback"
    assert material.material is None
    assert material.resolved_path is None
    assert material.error_reason == "private_dna_unavailable"
    assert material.ornament_emphasis is None
    assert material.is_resolved is False

    assert identity.hierarchy_contrast == "strong"
    assert identity.border_stroke_style == "solid"
    assert identity.energy_emphasis == "balanced"
    assert identity.surface_treatment == "flat"
    assert identity.transition_speed == "deliberate"


def test_private_package_absence_fails_open_to_public_safe_defaults(monkeypatch):
    _block_private_imports(monkeypatch)

    assert dna_bridge.ensure_optional_dna_registered() is False

    material = dna_bridge.resolve_brand_material("default")
    assert material == dna_bridge.BridgeMaterialResult()

    identity = dna_bridge.resolve_theme_identity_projection(object())
    assert identity == dna_bridge.BridgeIdentityProjection()

    fallback_calls = []
    rendered = dna_bridge.render_optional_theme_studio(
        fallback=lambda: fallback_calls.append("fallback")
    )
    assert rendered is False
    assert fallback_calls == ["fallback"]


def test_bridge_does_not_swallow_unrelated_import_failure(monkeypatch):
    _block_private_imports(monkeypatch, unrelated_name="unrelated_dependency")

    with pytest.raises(ModuleNotFoundError) as exc_info:
        dna_bridge.ensure_optional_dna_registered()
    assert exc_info.value.name == "unrelated_dependency"


def test_bridge_preserves_current_material_resolution_semantics_when_private_exists():
    assert dna_bridge.ensure_optional_dna_registered() is True

    from dna_quarantine.legacy_ui_dna.resolver import resolve_material, resolve_source_dna

    private = resolve_material("default")
    source = resolve_source_dna("default")
    public = dna_bridge.resolve_brand_material("default")

    assert public.status == private.status
    assert public.material is private.material
    assert public.resolved_path == private.resolved_path
    assert public.error_reason == private.error_reason
    assert public.ornament_emphasis == (getattr(source, "ornament_emphasis", None) if source else None)


def test_bridge_preserves_current_identity_projection_semantics_when_private_exists():
    assert dna_bridge.ensure_optional_dna_registered() is True

    from dna_quarantine.legacy_ui_dna.resolver import resolve_identity_projection, resolve_source_dna
    from ui.themes import get_theme

    theme = get_theme("default")
    source = resolve_source_dna(theme)
    private = resolve_identity_projection(source)
    public = dna_bridge.resolve_theme_identity_projection(theme)

    assert public.hierarchy_contrast == private.hierarchy_contrast
    assert public.border_stroke_style == private.border_stroke_style
    assert public.energy_emphasis == private.energy_emphasis
    assert public.surface_treatment == private.surface_treatment
    assert public.transition_speed == private.transition_speed


def test_theme_studio_bridge_delegates_when_private_exists(monkeypatch):
    from dna_quarantine.theme_studio import surface as private_surface

    calls = []
    monkeypatch.setattr(private_surface, "render_theme_studio_surface", lambda: calls.append("rendered"))

    assert dna_bridge.render_optional_theme_studio() is True
    assert calls == ["rendered"]


def test_public_theme_css_survives_private_package_absence(monkeypatch):
    from ui.themes.registry import generate_theme_css

    _block_private_imports(monkeypatch)
    css = generate_theme_css("default")

    assert ":root {" in css
    assert "--mm-heading-font-weight: 700;" in css
    assert "--mm-shape-border-style: solid;" in css
    assert "--mm-transition-spec:" in css


def test_material_resolution_result_keeps_resolved_semantics_without_private_type_dependency():
    resolved = dna_bridge.BridgeMaterialResult(
        status="resolved",
        resolved_path="assets/example.png",
        error_reason=None,
        ornament_emphasis="subtle",
    )
    unresolved = dna_bridge.BridgeMaterialResult(status="resolved", resolved_path=None)

    assert resolved.is_resolved is True
    assert unresolved.is_resolved is False
