"""Pure projection from canonical host vocabulary to Reflex-consumable scalars.

The mapper knows only the finite host-realization vocabulary exposed by the
public bridge. It never branches on a DNA/reference ID, title, family, or
private directive prose. Colors stay a conservative accessible neutral set for
this structural EQ4 proving slice; asset/color enrichment is deliberately out
of scope.
"""
from __future__ import annotations

from dataclasses import dataclass

from ui.canonical_dna_bridge import CanonicalHostRealizationPlan


@dataclass(frozen=True)
class CanonicalReflexTokens:
    desktop_columns: str
    gap: str
    card_padding: str
    card_radius: str
    heading_size: str
    heading_weight: str
    heading_tracking: str
    secondary_offset: str
    continuity_border: str
    transition: str
    hover_transform: str
    font_family: str
    line_height: str
    background: str = "#F8FAFC"
    surface: str = "#FFFFFF"
    surface_alt: str = "#F1F5F9"
    text: str = "#0F172A"
    text_muted: str = "#475569"
    accent: str = "#334155"
    border: str = "#94A3B8"


_LAYOUT_COLUMNS = {
    "grid": "repeat(3, minmax(0, 1fr))",
    "components": "repeat(2, minmax(0, 1fr))",
    "grouped": "repeat(3, minmax(0, 1fr))",
    "paired": "repeat(2, minmax(0, 1fr))",
    "continuous": "repeat(2, minmax(0, 1fr))",
    "directional": "repeat(2, minmax(0, 1fr))",
    "trace": "repeat(2, minmax(0, 1fr))",
}
_DENSITY = {
    "compact": ("0.55rem", "0.7rem"),
    "comfortable": ("0.85rem", "1rem"),
    "spacious": ("1.25rem", "1.35rem"),
}
_HIERARCHY = {
    "soft": ("1.25rem", "500", "0"),
    "measured": ("1.35rem", "650", "0.01em"),
    "strong": ("1.5rem", "750", "0"),
    "dramatic": ("1.7rem", "850", "0.035em"),
    "task_first": ("1.45rem", "750", "-0.01em"),
}
_BALANCE_OFFSET = {
    "ordered": "none",
    "asymmetric": "translateY(0.45rem)",
    "organic": "translateX(0.3rem)",
}
_FLOW_RADIUS = {
    "grid": "3px",
    "components": "8px",
    "grouped": "6px",
    "paired": "6px",
    "continuous": "18px",
    "directional": "2px",
    "trace": "5px",
}
_CONTINUITY_BORDER = {
    "none": "0px solid transparent",
    "state": "3px solid #64748B",
    "service": "3px dashed #64748B",
    "language": "4px double #64748B",
    "knowledge": "2px dashed #475569",
}
_MOTION = {
    "static": ("none", "none"),
    "deliberate": ("transform 180ms ease, box-shadow 180ms ease", "translateY(-1px)"),
    "directional": ("transform 140ms ease", "translate(2px, -2px)"),
}
_TYPOGRAPHY = {
    "system": ("system-ui, -apple-system, sans-serif", "1.5"),
    "measured": ("Arial, Helvetica, sans-serif", "1.45"),
    "paired": ("system-ui, -apple-system, sans-serif", "1.65"),
    "directional": ("Arial, Helvetica, sans-serif", "1.35"),
}


def project_reflex_tokens(plan: CanonicalHostRealizationPlan) -> CanonicalReflexTokens:
    """Project typed canonical host vocabulary into bounded style scalars."""
    if not isinstance(plan, CanonicalHostRealizationPlan):
        raise TypeError("plan must be CanonicalHostRealizationPlan")
    try:
        desktop_columns = _LAYOUT_COLUMNS[plan.layout_flow]
        gap, card_padding = _DENSITY[plan.density]
        heading_size, heading_weight, heading_tracking = _HIERARCHY[plan.hierarchy]
        secondary_offset = _BALANCE_OFFSET[plan.balance]
        card_radius = _FLOW_RADIUS[plan.layout_flow]
        continuity_border = _CONTINUITY_BORDER[plan.continuity]
        transition, hover_transform = _MOTION[plan.motion]
        font_family, line_height = _TYPOGRAPHY[plan.typography]
    except KeyError as exc:
        raise ValueError(f"unsupported canonical host vocabulary: {exc.args[0]}") from exc

    return CanonicalReflexTokens(
        desktop_columns=desktop_columns,
        gap=gap,
        card_padding=card_padding,
        card_radius=card_radius,
        heading_size=heading_size,
        heading_weight=heading_weight,
        heading_tracking=heading_tracking,
        secondary_offset=secondary_offset,
        continuity_border=continuity_border,
        transition=transition,
        hover_transform=hover_transform,
        font_family=font_family,
        line_height=line_height,
    )


__all__ = ["CanonicalReflexTokens", "project_reflex_tokens"]
