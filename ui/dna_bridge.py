"""Small stable public boundary for optional Design-DNA capabilities.

Public/application code may import this module. The private DNA implementation
is loaded lazily so MultiMind remains importable and usable with a boring,
neutral presentation when that implementation is absent, broken, or
incompatible.

MusicDNA uses the same host-safe Theme Studio seam.  A music track is an atomic
identity bundle; the only cross-product axis exposed here is the canonical
MultiMind archetype.  Web/Information DNA is deliberately ignored for a music
identity so typography, palette, world, material and interaction voice cannot
be accidentally mixed apart.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
import logging
from typing import Any, Optional


logger = logging.getLogger(__name__)
_MUSIC_PREFIX = "music:"


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


@dataclass(frozen=True)
class ThemeStudioDNAOption:
    """Small serializable catalog item exposed to presentation hosts."""

    id: str
    display_name: str
    role: str
    category: str = ""


@dataclass(frozen=True)
class ThemeStudioProjection:
    """Host-safe Theme Studio projection with no private implementation types."""

    identity_dna_id: str
    web_information_dna_id: Optional[str]
    archetype_id: str
    identity_display_name: str
    web_information_display_name: str = ""
    colors: dict[str, str] = field(default_factory=dict)
    typography: dict[str, Any] = field(default_factory=dict)
    spacing: dict[str, str] = field(default_factory=dict)
    radius: dict[str, str] = field(default_factory=dict)
    presentation_policy: dict[str, Any] = field(default_factory=dict)
    identity_projection: dict[str, str] = field(default_factory=dict)


def _warn(operation: str, exc: Exception) -> None:
    logger.warning("Optional Design-DNA %s failed; using safe fallback: %s", operation, exc)


def _optional_import(module_name: str):
    try:
        return import_module(module_name)
    except Exception as exc:  # Optional private package must never own host availability.
        _warn(f"import {module_name}", exc)
        return None


def _music_option_snapshots() -> tuple[ThemeStudioDNAOption, ...]:
    """Return atomic MusicDNA choices without making them a public dependency."""
    try:
        from ui.music_dna_bridge import list_music_theme_options

        return tuple(
            ThemeStudioDNAOption(
                id=f"{_MUSIC_PREFIX}{item.id}",
                display_name=f"♫ {item.display_name} — {item.artist}",
                role="identity",
                category=f"music:{item.tier}",
            )
            for item in list_music_theme_options(include_all=True)
        )
    except Exception as exc:
        _warn("MusicDNA catalog", exc)
        return ()


def _resolve_music_composition(
    identity_dna_id: str,
    archetype_id: str,
) -> Optional[ThemeStudioProjection]:
    """Resolve one atomic MusicDNA track through one canonical archetype."""
    if not str(identity_dna_id or "").startswith(_MUSIC_PREFIX):
        return None
    track_id = str(identity_dna_id)[len(_MUSIC_PREFIX):].strip()
    if not track_id:
        return None
    try:
        from ui.music_dna_bridge import realize_music_theme

        plan = realize_music_theme(track_id, archetype_id)
    except Exception as exc:
        _warn("MusicDNA realization", exc)
        return None
    if plan is None:
        return None

    spacing_md = {
        "compact": "0.75rem",
        "comfortable": "1rem",
        "spacious": "1.25rem",
    }.get(plan.density, "1rem")
    radius_md = {
        "none": "0px",
        "small": "4px",
        "medium": "8px",
        "large": "12px",
    }.get(plan.radius, "8px")
    status_richness = (
        "rich"
        if plan.archetype_id in {"command_center", "ai_research_lab", "agent_canvas"}
        else "standard"
    )

    return ThemeStudioProjection(
        identity_dna_id=f"{_MUSIC_PREFIX}{plan.track_id}",
        web_information_dna_id=None,
        archetype_id=plan.archetype_id,
        identity_display_name=f"♫ {plan.display_name} — {plan.artist}",
        web_information_display_name="MusicDNA atomic · internal axes locked",
        colors={
            "background": plan.background,
            "surface": plan.surface,
            "text": plan.text,
            "primary": plan.primary,
            "accent": plan.accent,
            "border": plan.border,
        },
        typography={
            "font_family_base": plan.font_family,
            "font_family_mono": plan.mono_font,
        },
        spacing={"sm": "0.5rem", "md": spacing_md, "lg": "1.5rem"},
        radius={"sm": "2px", "md": radius_md, "lg": radius_md},
        presentation_policy={
            "metadata_prominence": "music-dna",
            "status_richness": status_richness,
            "navigation_density": plan.mobile_strategy,
            "secondary_compactness": plan.density == "compact",
            "information_discoverability": plan.primary_object,
            "utility_grouping": plan.layout_flow,
        },
        identity_projection={
            "hierarchy_contrast": "strong",
            "border_stroke_style": "solid",
            "energy_emphasis": "track-bound",
            "surface_treatment": plan.layout_flow,
            "transition_speed": "deliberate",
        },
    )


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


def list_theme_studio_dna_options(role: Optional[str] = None) -> tuple[ThemeStudioDNAOption, ...]:
    """List Theme Studio choices through the optional-package seam.

    Registered role-based DNA and atomic MusicDNA share the picker catalog, but
    music entries stay atomic and are resolved by ``_resolve_music_composition``.
    Missing/incompatible private packages remain a valid empty-catalog state.
    """
    if role not in {None, "identity", "web_information"}:
        return ()

    options: list[ThemeStudioDNAOption] = []
    if ensure_dna_registered():
        module = _optional_import("dna_quarantine.legacy_ui_dna")
        if module is not None:
            try:
                for dna in module.list_dna():
                    dna_role = str(getattr(dna, "role", "") or "")
                    if role is not None and dna_role != role:
                        continue
                    dna_id = str(getattr(dna, "id", "") or "").strip()
                    display_name = str(getattr(dna, "display_name", "") or "").strip()
                    if not dna_id or not display_name:
                        continue
                    options.append(
                        ThemeStudioDNAOption(
                            id=dna_id,
                            display_name=display_name,
                            role=dna_role,
                            category=str(getattr(dna, "category", "") or ""),
                        )
                    )
            except Exception as exc:
                _warn("Theme Studio DNA catalog", exc)

    if role in {None, "identity"}:
        options.extend(_music_option_snapshots())

    deduped = {item.id: item for item in options}
    return tuple(sorted(deduped.values(), key=lambda item: (item.display_name.lower(), item.id)))


def resolve_theme_studio_composition(
    identity_dna_id: str,
    web_information_dna_id: Optional[str],
    archetype_id: str,
) -> Optional[ThemeStudioProjection]:
    """Resolve a Theme Studio composition into host-safe tokens.

    Music identities are intercepted first and always ignore Web/Information DNA
    so the track bundle remains atomic.  Non-music identities continue through
    the existing private Theme Studio owner unchanged.
    """
    if str(identity_dna_id or "").startswith(_MUSIC_PREFIX):
        return _resolve_music_composition(identity_dna_id, archetype_id)

    if not ensure_dna_registered():
        return None
    module = _optional_import("dna_quarantine.theme_studio.state")
    if module is None:
        return None
    try:
        draft = module.init_draft_from_composition(
            identity_dna_id=identity_dna_id,
            web_information_dna_id=web_information_dna_id or None,
            archetype_id=archetype_id,
        )
        projection = draft.resolve()
        provenance = dict(getattr(projection, "provenance", {}) or {})
        policy = getattr(projection, "presentation_policy", None)
        identity_projection = getattr(projection, "identity_projection", None)
        return ThemeStudioProjection(
            identity_dna_id=str(draft.identity_dna_id),
            web_information_dna_id=(
                str(draft.web_information_dna_id)
                if draft.web_information_dna_id
                else None
            ),
            archetype_id=str(projection.archetype_id),
            identity_display_name=str(
                provenance.get("identity_display_name") or draft.identity_dna_id
            ),
            web_information_display_name=str(
                provenance.get("web_information_display_name") or ""
            ),
            colors={str(key): str(value) for key, value in dict(draft.colors or {}).items()},
            typography=dict(draft.typography or {}),
            spacing={str(key): str(value) for key, value in dict(draft.spacing or {}).items()},
            radius={str(key): str(value) for key, value in dict(draft.radius or {}).items()},
            presentation_policy={
                "metadata_prominence": str(getattr(policy, "metadata_prominence", "standard")),
                "status_richness": str(getattr(policy, "status_richness", "standard")),
                "navigation_density": str(getattr(policy, "navigation_density", "standard")),
                "secondary_compactness": bool(getattr(policy, "secondary_compactness", False)),
                "information_discoverability": str(
                    getattr(policy, "information_discoverability", "standard")
                ),
                "utility_grouping": str(getattr(policy, "utility_grouping", "standard")),
            },
            identity_projection={
                "hierarchy_contrast": str(
                    getattr(identity_projection, "hierarchy_contrast", "strong")
                ),
                "border_stroke_style": str(
                    getattr(identity_projection, "border_stroke_style", "solid")
                ),
                "energy_emphasis": str(
                    getattr(identity_projection, "energy_emphasis", "balanced")
                ),
                "surface_treatment": str(
                    getattr(identity_projection, "surface_treatment", "flat")
                ),
                "transition_speed": str(
                    getattr(identity_projection, "transition_speed", "deliberate")
                ),
            },
        )
    except Exception as exc:
        _warn("Theme Studio composition resolution", exc)
        return None


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
    "ThemeStudioDNAOption",
    "ThemeStudioProjection",
    "dna_available",
    "ensure_dna_registered",
    "list_theme_studio_dna_options",
    "resolve_identity_projection",
    "resolve_material",
    "resolve_source_dna",
    "resolve_theme_studio_composition",
    "render_theme_studio_surface",
    "theme_studio_available",
]
