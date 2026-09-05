"""Small optional Design-DNA bridge for public presentation surfaces.

Q3 boundary law:
- public application/presentation/theme code depends only on this module;
- private/quarantined DNA and Theme Studio imports stay lazy;
- absence of the private package degrades to deterministic safe defaults;
- unrelated import/runtime defects are not silently swallowed.

Q4 owns proving the repository/runtime with the private package physically absent.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

_PRIVATE_PREFIXES = (
    "dna_quarantine",
    "ui.dna",
    "ui.theme_studio",
)


@dataclass(frozen=True)
class BridgeMaterialResult:
    """Public material-resolution payload independent of private DNA types."""

    status: str = "fallback"
    material: Any = None
    resolved_path: Optional[str] = None
    error_reason: Optional[str] = "private_dna_unavailable"
    ornament_emphasis: Optional[str] = None

    @property
    def is_resolved(self) -> bool:
        return self.status == "resolved" and bool(self.resolved_path)


@dataclass(frozen=True)
class BridgeIdentityProjection:
    """Public bounded identity projection with safe default semantics."""

    hierarchy_contrast: str = "strong"
    border_stroke_style: str = "solid"
    energy_emphasis: str = "balanced"
    surface_treatment: str = "flat"
    transition_speed: str = "deliberate"


def _is_private_absence(exc: ImportError) -> bool:
    """Return True only for missing quarantine/compatibility modules.

    Import errors for unrelated dependencies remain visible instead of being
    converted into a misleading safe-default success.
    """
    missing = getattr(exc, "name", None)
    if not missing:
        return False
    return any(missing == prefix or missing.startswith(prefix + ".") for prefix in _PRIVATE_PREFIXES)


def _fallback_material(reason: str = "private_dna_unavailable") -> BridgeMaterialResult:
    return BridgeMaterialResult(error_reason=reason)


def ensure_optional_dna_registered() -> bool:
    """Register optional legacy proof DNA/themes when the private package exists."""
    try:
        from dna_quarantine.legacy_ui_dna.bootstrap import ensure_proof_dna_and_themes_registered
    except (ImportError, ModuleNotFoundError) as exc:
        if _is_private_absence(exc):
            return False
        raise
    ensure_proof_dna_and_themes_registered()
    return True


def resolve_brand_material(theme_or_dna_input: Any) -> BridgeMaterialResult:
    """Resolve optional material identity without exposing private DNA classes."""
    try:
        from dna_quarantine.legacy_ui_dna.resolver import resolve_material, resolve_source_dna
    except (ImportError, ModuleNotFoundError) as exc:
        if _is_private_absence(exc):
            return _fallback_material()
        raise

    result = resolve_material(theme_or_dna_input)
    source_dna = resolve_source_dna(theme_or_dna_input)
    return BridgeMaterialResult(
        status=getattr(result, "status", "fallback"),
        material=getattr(result, "material", None),
        resolved_path=getattr(result, "resolved_path", None),
        error_reason=getattr(result, "error_reason", None),
        ornament_emphasis=getattr(source_dna, "ornament_emphasis", None) if source_dna else None,
    )


def resolve_theme_identity_projection(theme: Any) -> BridgeIdentityProjection:
    """Resolve optional identity semantics or return the canonical safe default."""
    try:
        from dna_quarantine.legacy_ui_dna.resolver import (
            resolve_identity_projection,
            resolve_source_dna,
        )
    except (ImportError, ModuleNotFoundError) as exc:
        if _is_private_absence(exc):
            return BridgeIdentityProjection()
        raise

    source_dna = resolve_source_dna(theme)
    projection = resolve_identity_projection(source_dna)
    return BridgeIdentityProjection(
        hierarchy_contrast=getattr(projection, "hierarchy_contrast", "strong"),
        border_stroke_style=getattr(projection, "border_stroke_style", "solid"),
        energy_emphasis=getattr(projection, "energy_emphasis", "balanced"),
        surface_treatment=getattr(projection, "surface_treatment", "flat"),
        transition_speed=getattr(projection, "transition_speed", "deliberate"),
    )


def render_optional_theme_studio(
    fallback: Optional[Callable[[], None]] = None,
) -> bool:
    """Render Theme Studio only when the quarantined implementation is present.

    Returns True when the private surface rendered. On private-package absence it
    optionally invokes a public fallback callback and returns False.
    """
    try:
        from dna_quarantine.theme_studio.surface import render_theme_studio_surface
    except (ImportError, ModuleNotFoundError) as exc:
        if not _is_private_absence(exc):
            raise
        if fallback is not None:
            fallback()
        return False

    render_theme_studio_surface()
    return True
