"""
MultiMind AI - UI Design Tokens
Semantic tokens serving as the single source of truth for visual styling and themeability.
"""

# Typography Tokens
TYPOGRAPHY = {
    "font_family_base": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif",
    "font_family_mono": "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace",
    "roles": {
        "display": {"size": "2rem", "weight": "700", "line_height": "1.2"},
        "heading": {"size": "1.5rem", "weight": "600", "line_height": "1.3"},
        "subheading": {"size": "1.25rem", "weight": "600", "line_height": "1.4"},
        "body": {"size": "1rem", "weight": "400", "line_height": "1.5"},
        "body_small": {"size": "0.875rem", "weight": "400", "line_height": "1.4"},
        "caption": {"size": "0.75rem", "weight": "400", "line_height": "1.4"},
        "label": {"size": "0.875rem", "weight": "500", "line_height": "1.2"},
        "mono": {"size": "0.875rem", "weight": "400", "line_height": "1.4"}
    }
}

# Spacing Tokens (Scale)
SPACING = {
    "xs": "0.25rem",   # 4px
    "sm": "0.5rem",    # 8px
    "md": "1rem",      # 16px
    "lg": "1.5rem",    # 24px
    "xl": "2rem",      # 32px
    "2xl": "3rem"      # 48px
}

# Radius Tokens
RADIUS = {
    "none": "0px",
    "sm": "0.25rem",   # 4px
    "md": "0.5rem",    # 8px
    "lg": "0.75rem",   # 12px
    "pill": "9999px"
}

# Semantic Color Roles
COLORS = {
    "primary": "#3B82F6",
    "primary_hover": "#2563EB",
    "secondary": "#64748B",
    "accent": "#8B5CF6",
    "background": "#0F172A",
    "surface": "#1E293B",
    "surface_elevated": "#334155",
    "surface_muted": "#0F172A",
    "text": "#F8FAFC",
    "text_muted": "#94A3B8",
    "border": "#334155",
    "border_subtle": "#1E293B",
    "success": "#10B981",
    "success_bg": "rgba(16, 185, 129, 0.12)",
    "warning": "#F59E0B",
    "warning_bg": "rgba(245, 158, 11, 0.12)",
    "danger": "#EF4444",
    "danger_bg": "rgba(239, 68, 68, 0.12)",
    "info": "#3B82F6",
    "info_bg": "rgba(59, 130, 246, 0.12)"
}

# Surface Tokens
SURFACES = {
    "background": COLORS["background"],
    "surface": COLORS["surface"],
    "surface_elevated": COLORS["surface_elevated"],
    "surface_muted": COLORS["surface_muted"]
}

# Border Tokens
BORDERS = {
    "default": f"1px solid {COLORS['border']}",
    "subtle": f"1px solid {COLORS['border_subtle']}",
    "focus": f"2px solid {COLORS['primary']}"
}


def generate_tokens_css() -> str:
    """Generates CSS custom properties and typography utility rules from Python tokens."""
    css_lines = [":root {"]

    # Fonts
    css_lines.append(f"  --mm-font-base: {TYPOGRAPHY['font_family_base']};")
    css_lines.append(f"  --mm-font-mono: {TYPOGRAPHY['font_family_mono']};")

    # Spacing
    for k, v in SPACING.items():
        css_lines.append(f"  --mm-space-{k}: {v};")

    # Radius
    for k, v in RADIUS.items():
        css_lines.append(f"  --mm-radius-{k}: {v};")

    # Colors
    for k, v in COLORS.items():
        css_name = k.replace("_", "-")
        css_lines.append(f"  --mm-color-{css_name}: {v};")

    css_lines.append("}")

    # Typography classes representation
    for role, props in TYPOGRAPHY["roles"].items():
        class_name = role.replace("_", "-")
        font_fam = "var(--mm-font-mono)" if role == "mono" else "var(--mm-font-base)"
        css_lines.append(f".mm-typo-{class_name} {{")
        css_lines.append(f"  font-family: {font_fam};")
        css_lines.append(f"  font-size: {props['size']};")
        css_lines.append(f"  font-weight: {props['weight']};")
        css_lines.append(f"  line-height: {props['line_height']};")
        css_lines.append("}")

    return "\n".join(css_lines)
