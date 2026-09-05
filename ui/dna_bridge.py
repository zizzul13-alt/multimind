"""Small stable public boundary for optional Design-DNA capabilities.

Public/application code may import this module.  The quarantined/private DNA
implementation is loaded lazily so MultiMind remains importable and usable with
only the boring built-in presentation when that implementation is absent.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Optional


@dataclass(frozen=True)
class FallbackMaterialResolution:
    """Host-safe material result used when the optional DNA package is absent."""

    status: str = "fallback"
    material: Any = None
    resolved_path: Optional[str] = None
    error_reason: Optional[str] = "Design-DNA package unavailable"

    @property
    def is_resolved(self) -> bool:
        return False


@dataclass(frozen=True)
class FallbackIdentityProjection:
    """Neutral semantic projection matching the legacy resolver defaults."""

    hierarchy_contrast: str = "strong"
    border_stroke_style: str = "solid"
    energy_emphasis: str = "balanced"
    surface_treatment: str = "flat"
    transition_speed: str = "deliberate"


def _optional_import(module_name: str):
    try:
        return import_module(module_name)
    except (ImportError, ModuleNotFoundError):
        return None


def dna_available() -> bool:
    """Return whether the optional Design-DNA runtime can currently be loaded."""
    return _optional_import("dna_quarantine.legacy_ui_dna.resolver") is not None


def ensure_dna_registered() -> bool:
    """Idempotently bootstrap DNA/theme proofs when available; otherwise no-op."""
    module = _optional_import("dna_quarantine.legacy_ui_dna.bootstrap")
    if module is None:
        return False
    module.ensure_proof_dna_and_themes_registered()
    return True


def resolve_material(theme_or_dna_input: Any, material_type: Optional[str] = None, material_root: Optional[str] = None):
    """Resolve optional DNA material while preserving a structural fallback."""
    module = _optional_import("dna_quarantine.legacy_ui_dna.resolver")
    if module is None:
        return FallbackMaterialResolution()
    return module.resolve_material(theme_or_dna_input, material_type=material_type, material_root=material_root)


def resolve_source_dna(theme_or_dna_input: Any):
    """Resolve source DNA when installed; absence is a valid public state."""
    module = _optional_import("dna_quarantine.legacy_ui_dna.resolver")
    if module is None:
        return None
    return module.resolve_source_dna(theme_or_dna_input)


def resolve_identity_projection(identity_dna: Any):
    """Project DNA semantics or return neutral host-safe presentation defaults."""
    module = _optional_import("dna_quarantine.legacy_ui_dna.resolver")
    if module is None:
        return FallbackIdentityProjection()
    return module.resolve_identity_projection(identity_dna)


def theme_studio_available() -> bool:
    """Return whether the optional Theme Studio implementation is installed."""
    return _optional_import("dna_quarantine.theme_studio.surface") is not None


def render_theme_studio_surface() -> bool:
    """Render optional Theme Studio; show a bounded host fallback when unavailable."""
    module = _optional_import("dna_quarantine.theme_studio.surface")
    if module is not None:
        module.render_theme_studio_surface()
        return True

    # Streamlit stays a host-only dependency and is imported only for the fallback UI.
    import streamlit as st

    st.info("Theme Studio is unavailable. MultiMind is using the safe default presentation.")
    return False


__all__ = [
    "FallbackIdentityProjection",
    "FallbackMaterialResolution",
    "dna_available",
    "ensure_dna_registered",
    "resolve_identity_projection",
    "resolve_material",
    "resolve_source_dna",
    "render_theme_studio_surface",
    "theme_studio_available",
]
