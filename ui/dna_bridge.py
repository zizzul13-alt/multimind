"""Small stable public boundary for optional Design-DNA capabilities.

Public/application code may import this module. The private DNA implementation
is loaded lazily so MultiMind remains importable and usable with a boring,
neutral presentation when that implementation is absent, broken, or
incompatible.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
import logging
from typing import Any, Optional


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FallbackMaterialResolution:
    """Host-safe material result used when the optional DNA package is unavailable."""

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


def _warn(operation: str, exc: Exception) -> None:
    logger.warning("Optional Design-DNA %s failed; using safe fallback: %s", operation, exc)


def _optional_import(module_name: str):
    try:
        return import_module(module_name)
    except Exception as exc:  # Optional private package must never own host availability.
        _warn(f"import {module_name}", exc)
        return None


def dna_available() -> bool:
    """Return whether the optional Design-DNA runtime can currently be loaded."""
    return _optional_import("dna_quarantine.legacy_ui_dna.resolver") is not None


def ensure_dna_registered() -> bool:
    """Idempotently bootstrap DNA/theme proofs when healthy; otherwise no-op."""
    module = _optional_import("dna_quarantine.legacy_ui_dna.bootstrap")
    if module is None:
        return False
    try:
        module.ensure_proof_dna_and_themes_registered()
        return True
    except Exception as exc:
        _warn("bootstrap", exc)
        return False


def resolve_material(theme_or_dna_input: Any, material_type: Optional[str] = None, material_root: Optional[str] = None):
    """Resolve optional DNA material while preserving a structural fallback."""
    module = _optional_import("dna_quarantine.legacy_ui_dna.resolver")
    if module is None:
        return FallbackMaterialResolution()
    try:
        return module.resolve_material(theme_or_dna_input, material_type=material_type, material_root=material_root)
    except Exception as exc:
        _warn("material resolution", exc)
        return FallbackMaterialResolution(error_reason="Design-DNA material resolution failed")


def resolve_source_dna(theme_or_dna_input: Any):
    """Resolve source DNA when healthy; unavailability is a valid public state."""
    module = _optional_import("dna_quarantine.legacy_ui_dna.resolver")
    if module is None:
        return None
    try:
        return module.resolve_source_dna(theme_or_dna_input)
    except Exception as exc:
        _warn("source resolution", exc)
        return None


def resolve_identity_projection(identity_dna: Any):
    """Project DNA semantics or return neutral host-safe presentation defaults."""
    module = _optional_import("dna_quarantine.legacy_ui_dna.resolver")
    if module is None:
        return FallbackIdentityProjection()
    try:
        return module.resolve_identity_projection(identity_dna)
    except Exception as exc:
        _warn("identity projection", exc)
        return FallbackIdentityProjection()


def theme_studio_available() -> bool:
    """Return whether the optional Theme Studio implementation can be loaded."""
    return _optional_import("dna_quarantine.theme_studio.surface") is not None


def _render_theme_studio_fallback() -> None:
    # Streamlit stays a host-only dependency and is imported only for fallback UI.
    import streamlit as st

    st.info("Theme Studio is unavailable. MultiMind is using the safe default presentation.")


def render_theme_studio_surface() -> bool:
    """Render optional Theme Studio; degrade safely on absence or private failure."""
    module = _optional_import("dna_quarantine.theme_studio.surface")
    if module is not None:
        try:
            module.render_theme_studio_surface()
            return True
        except Exception as exc:
            _warn("Theme Studio render", exc)

    _render_theme_studio_fallback()
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
