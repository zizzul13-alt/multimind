"""
MultiMind AI - Theme Registry and Resolution Core
Central registry for theme management, resolution, partial override merging, and CSS generation.
"""
import copy
import logging
from typing import Dict, List, Optional, Tuple, Any
import streamlit as st

from ui import tokens
from ui.themes.models import Theme, ThemeMetadata

logger = logging.getLogger(__name__)

DEFAULT_THEME_ID = "default"


class ThemeRegistry:
    """Central registry managing theme registration, resolution, and fallbacks."""

    def __init__(self):
        self._themes: Dict[str, Theme] = {}
        self._register_default_theme()
        self._register_demo_theme()

    def _register_default_theme(self):
        """Registers the canonical default/base theme wrapping ui.tokens."""
        default_theme = Theme(
            id=DEFAULT_THEME_ID,
            display_name="MultiMind Default",
            category="system",
            description="Canonical default theme derived from ui.tokens.",
            metadata=ThemeMetadata(
                description="Default MultiMind AI Design Token Base",
                author="MultiMind Core"
            ),
            colors=copy.deepcopy(tokens.COLORS),
            typography=copy.deepcopy(tokens.TYPOGRAPHY),
            spacing=copy.deepcopy(tokens.SPACING),
            radius=copy.deepcopy(tokens.RADIUS),
        )
        default_theme.validate()
        self._themes[DEFAULT_THEME_ID] = default_theme

    def _register_demo_theme(self):
        """Registers a generic, non-IP demonstration theme to verify runtime theme switching."""
        demo_theme = Theme(
            id="neutral-contrast-demo",
            display_name="Neutral Contrast (Demo)",
            category="experimental",
            description="Generic demonstration theme with semantic token overrides for runtime switching verification.",
            metadata=ThemeMetadata(
                description="S5.2 Runtime Theme Switching Demonstration Theme",
                author="MultiMind Core"
            ),
            colors={
                "primary": "#D97706",
                "primary_hover": "#B45309",
                "primary_active": "#92400E",
                "secondary": "#71717A",
                "secondary_hover": "#52525B",
                "accent": "#06B6D4",
                "background": "#09090B",
                "surface": "#18181B",
                "surface_elevated": "#27272A",
                "surface_muted": "#09090B",
                "surface_hover": "#27272A",
                "surface_input": "#121215",
                "text": "#FAFAFA",
                "text_muted": "#A1A1AA",
                "text_disabled": "#71717A",
                "border": "#3F3F46",
                "border_subtle": "#27272A",
                "border_hover": "#52525B",
                "border_focus": "#D97706",
                "focus_ring": "rgba(217, 119, 6, 0.4)",
                "info": "#06B6D4",
                "info_bg": "rgba(6, 182, 212, 0.15)",
            },
        )
        demo_theme.validate()
        self._themes[demo_theme.id] = demo_theme

    def register_theme(self, theme: Theme) -> None:
        """Registers a new theme after validating its contract."""
        if not isinstance(theme, Theme):
            raise TypeError("Theme must be an instance of Theme dataclass.")
        theme.validate()
        self._themes[theme.id] = theme

    def list_themes(self) -> List[Theme]:
        """Returns a list of all registered themes."""
        return list(self._themes.values())

    def get_theme(self, theme_id: Optional[str]) -> Theme:
        """Retrieves a theme by ID, falling back safely to default theme if unknown/missing."""
        if not theme_id or not isinstance(theme_id, str):
            logger.debug("No valid theme ID provided; falling back to default theme.")
            return self._themes[DEFAULT_THEME_ID]

        theme_id_clean = theme_id.strip()
        if theme_id_clean in self._themes:
            return self._themes[theme_id_clean]

        logger.warning(f"Theme '{theme_id}' not found in registry. Falling back to '{DEFAULT_THEME_ID}'.")
        return self._themes[DEFAULT_THEME_ID]

    def resolve_theme(self, theme_id: Optional[str]) -> Tuple[Theme, Dict[str, Any]]:
        """Resolves a theme by ID and merges partial overrides with base tokens without mutating defaults.

        Returns a tuple of (resolved Theme object, resolved dictionary of token groups).
        """
        theme = self.get_theme(theme_id)

        # Base default token dicts (deep copied to avoid mutation)
        resolved_colors = copy.deepcopy(tokens.COLORS)
        resolved_typography = copy.deepcopy(tokens.TYPOGRAPHY)
        resolved_spacing = copy.deepcopy(tokens.SPACING)
        resolved_radius = copy.deepcopy(tokens.RADIUS)

        # If resolving non-default theme, apply non-mutating overrides
        if theme.id != DEFAULT_THEME_ID:
            if theme.colors:
                resolved_colors.update(theme.colors)
            if theme.spacing:
                resolved_spacing.update(theme.spacing)
            if theme.radius:
                resolved_radius.update(theme.radius)
            if theme.typography:
                if "font_family_base" in theme.typography:
                    resolved_typography["font_family_base"] = theme.typography["font_family_base"]
                if "font_family_mono" in theme.typography:
                    resolved_typography["font_family_mono"] = theme.typography["font_family_mono"]
                if "roles" in theme.typography and isinstance(theme.typography["roles"], dict):
                    roles_base = copy.deepcopy(tokens.TYPOGRAPHY["roles"])
                    for role_key, role_val in theme.typography["roles"].items():
                        if role_key in roles_base and isinstance(role_val, dict):
                            roles_base[role_key].update(role_val)
                        elif isinstance(role_val, dict):
                            roles_base[role_key] = role_val
                    resolved_typography["roles"] = roles_base

        resolved_token_groups = {
            "colors": resolved_colors,
            "typography": resolved_typography,
            "spacing": resolved_spacing,
            "radius": resolved_radius,
        }

        return theme, resolved_token_groups


# Single global registry instance
_global_registry = ThemeRegistry()


def get_registry() -> ThemeRegistry:
    """Returns the global ThemeRegistry singleton."""
    return _global_registry


def register_theme(theme: Theme) -> None:
    """Helper to register a theme in the global registry."""
    _global_registry.register_theme(theme)


def list_themes() -> List[Theme]:
    """Helper to list themes in the global registry, filtered to built-in themes plus session-owned custom themes."""
    all_themes = _global_registry.list_themes()

    session_customs = set()
    try:
        if hasattr(st, "session_state") and "session_custom_themes" in st.session_state:
            session_customs = set(st.session_state.session_custom_themes)
    except Exception:
        session_customs = set()

    visible_themes = []
    for t in all_themes:
        if getattr(t, "category", "") == "custom":
            if t.id in session_customs:
                visible_themes.append(t)
        else:
            visible_themes.append(t)

    return visible_themes


def get_theme(theme_id: Optional[str]) -> Theme:
    """Helper to get a theme from the global registry with fallback."""
    return _global_registry.get_theme(theme_id)


def resolve_theme(theme_id: Optional[str] = DEFAULT_THEME_ID) -> Tuple[Theme, Dict[str, Any]]:
    """Helper to resolve a theme from the global registry."""
    return _global_registry.resolve_theme(theme_id)


def generate_theme_css(theme_id: Optional[str] = DEFAULT_THEME_ID) -> str:
    """Generates `--mm-*` CSS custom properties and typography rules for the resolved theme.

    Keeps CSS output format 100% compatible with ui.tokens.generate_tokens_css().
    """
    theme, resolved = resolve_theme(theme_id)

    colors = resolved["colors"]
    typography = resolved["typography"]
    spacing = resolved["spacing"]
    radius = resolved["radius"]

    from ui.dna.resolver import resolve_source_dna, resolve_identity_projection
    source_dna = resolve_source_dna(theme)
    id_proj = resolve_identity_projection(source_dna)

    css_lines = [":root {"]

    # Fonts
    css_lines.append(f"  --mm-font-base: {typography['font_family_base']};")
    css_lines.append(f"  --mm-font-mono: {typography['font_family_mono']};")

    # Spacing
    for k, v in spacing.items():
        css_lines.append(f"  --mm-space-{k}: {v};")

    # Radius
    for k, v in radius.items():
        css_lines.append(f"  --mm-radius-{k}: {v};")

    # Colors (includes all surface, background, and border semantic role colors)
    for k, v in colors.items():
        css_name = k.replace("_", "-")
        css_lines.append(f"  --mm-color-{css_name}: {v};")

    # Identity Semantic Presentation Custom Properties (Derived from IdentityPresentationProjection)
    # 1. hierarchy_contrast
    if id_proj.hierarchy_contrast == "dramatic":
        css_lines.append("  --mm-heading-font-weight: 900;")
        css_lines.append("  --mm-heading-letter-spacing: 0.04em;")
    elif id_proj.hierarchy_contrast == "soft":
        css_lines.append("  --mm-heading-font-weight: 500;")
        css_lines.append("  --mm-heading-letter-spacing: normal;")
    else:
        css_lines.append("  --mm-heading-font-weight: 700;")
        css_lines.append("  --mm-heading-letter-spacing: normal;")

    # 2. border_stroke_style (PARTIAL shape character - valid CSS properties consumed in ui/style.css)
    css_lines.append("  --mm-shape-border-style: solid;")
    if id_proj.border_stroke_style == "crisp":
        css_lines.append("  --mm-shape-border-width: 1px;")
        css_lines.append("  --mm-shape-border-color: var(--mm-color-border);")
    elif id_proj.border_stroke_style == "soft":
        css_lines.append("  --mm-shape-border-width: 1px;")
        css_lines.append("  --mm-shape-border-color: var(--mm-color-border-subtle);")
    else:
        css_lines.append("  --mm-shape-border-width: 1px;")
        css_lines.append("  --mm-shape-border-color: var(--mm-color-border);")

    # 3. energy_emphasis (visual_energy hover transform/shadow)
    if id_proj.energy_emphasis == "aggressive":
        css_lines.append("  --mm-energy-hover-lift: translate(-1px, -1px);")
        css_lines.append("  --mm-energy-hover-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);")
    elif id_proj.energy_emphasis == "expressive":
        css_lines.append("  --mm-energy-hover-lift: translateY(-1px);")
        css_lines.append("  --mm-energy-hover-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);")
    elif id_proj.energy_emphasis == "quiet":
        css_lines.append("  --mm-energy-hover-lift: none;")
        css_lines.append("  --mm-energy-hover-shadow: none;")
    else:
        css_lines.append("  --mm-energy-hover-lift: translateY(-1px);")
        css_lines.append("  --mm-energy-hover-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);")

    # 4. surface_treatment (PARTIAL surface elevation shadow)
    if id_proj.surface_treatment in ("layered", "poster"):
        css_lines.append("  --mm-surface-elevation-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);")
    elif id_proj.surface_treatment == "atmospheric":
        css_lines.append("  --mm-surface-elevation-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);")
    else:
        css_lines.append("  --mm-surface-elevation-shadow: none;")

    # 5. transition_speed (interaction_intensity - preserves background-color transition)
    if id_proj.transition_speed == "assertive":
        css_lines.append("  --mm-transition-spec: background-color 0.1s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.1s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.1s cubic-bezier(0.4, 0, 0.2, 1), transform 0.1s cubic-bezier(0.4, 0, 0.2, 1);")
    elif id_proj.transition_speed == "gentle":
        css_lines.append("  --mm-transition-spec: background-color 0.35s ease, border-color 0.35s ease, box-shadow 0.35s ease, transform 0.35s ease;")
    else:
        css_lines.append("  --mm-transition-spec: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;")

    css_lines.append("}")

    # Typography class rules
    for role, props in typography.get("roles", {}).items():
        class_name = role.replace("_", "-")
        font_fam = "var(--mm-font-mono)" if role == "mono" else "var(--mm-font-base)"
        css_lines.append(f".mm-typo-{class_name} {{")
        css_lines.append(f"  font-family: {font_fam};")
        css_lines.append(f"  font-size: {props['size']};")
        css_lines.append(f"  font-weight: {props['weight']};")
        css_lines.append(f"  line-height: {props['line_height']};")
        css_lines.append("}")

    return "\n".join(css_lines)
