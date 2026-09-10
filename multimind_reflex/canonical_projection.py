"""Pure projection from canonical host vocabulary to Reflex-consumable tokens.

The mapper knows only the finite host-realization vocabulary exposed by the
public bridge. It never branches on a DNA/reference ID, title, family, or
private directive prose. Colors stay a conservative accessible neutral set for
this structural EQ4 proving slice; asset/color enrichment is deliberately out
of scope.

The first proving renderer exposed only micro-style differences (gap, border,
radius). Real mobile browser evidence showed that technically distinct plans
could still look nearly identical. The projection therefore includes a finite
*structural template* vocabulary as well as style scalars. The Reflex host may
branch on these template tokens, but never on reference identity.
"""
from __future__ import annotations

from dataclasses import dataclass

from ui.canonical_dna_bridge import CanonicalHostRealizationPlan


@dataclass(frozen=True)
class CanonicalReflexTokens:
    fixture_template: str
    desktop_columns: str
    support_columns: str
    gap: str
    group_gap: str
    card_padding: str
    group_padding: str
    card_radius: str
    group_radius: str
    heading_size: str
    heading_weight: str
    heading_tracking: str
    secondary_offset: str
    secondary_inset: str
    secondary_width: str
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


# Canonical layout-flow vocabulary maps to a bounded renderer-neutral host
# template. This is intentionally not a reference-ID map.
_LAYOUT = {
    "grid": ("matrix", "repeat(3, minmax(0, 1fr))", "repeat(2, minmax(0, 1fr))"),
    "components": ("component_hierarchy", "repeat(2, minmax(0, 1fr))", "repeat(3, minmax(0, 1fr))"),
    "grouped": ("group_bands", "repeat(2, minmax(0, 1fr))", "repeat(2, minmax(0, 1fr))"),
    "paired": ("paired_blocks", "repeat(2, minmax(0, 1fr))", "repeat(2, minmax(0, 1fr))"),
    "continuous": ("continuous_surface", "1fr", "1fr"),
    "directional": ("directional_path", "1fr", "1fr"),
    "trace": ("trace_timeline", "1fr", "1fr"),
}
_DENSITY = {
    "compact": ("0.55rem", "0.8rem", "0.65rem", "0.85rem"),
    "comfortable": ("0.85rem", "1rem", "0.9rem", "1.1rem"),
    "spacious": ("1.25rem", "1.35rem", "1.25rem", "1.4rem"),
}
_HIERARCHY = {
    "soft": ("1.25rem", "500", "0"),
    "measured": ("1.35rem", "650", "0.01em"),
    "strong": ("1.5rem", "750", "0"),
    "dramatic": ("1.7rem", "850", "0.035em"),
    "task_first": ("1.45rem", "750", "-0.01em"),
}
# Inset/width changes are layout-safe on mobile. The original transform-only
# treatment barely changed perceived composition and could overflow narrow
# screens.
_BALANCE = {
    "ordered": ("none", "0rem", "100%"),
    "asymmetric": ("none", "1.35rem", "calc(100% - 1.35rem)"),
    "organic": ("none", "0.7rem", "calc(100% - 0.7rem)"),
}
_FLOW_RADIUS = {
    "grid": ("3px", "3px"),
    "components": ("8px", "12px"),
    "grouped": ("6px", "14px"),
    "paired": ("6px", "10px"),
    "continuous": ("18px", "22px"),
    "directional": ("2px", "8px"),
    "trace": ("5px", "8px"),
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
    """Project typed canonical host vocabulary into bounded host tokens."""
    if not isinstance(plan, CanonicalHostRealizationPlan):
        raise TypeError("plan must be CanonicalHostRealizationPlan")
    try:
        fixture_template, desktop_columns, support_columns = _LAYOUT[plan.layout_flow]
        gap, card_padding, group_gap, group_padding = _DENSITY[plan.density]
        heading_size, heading_weight, heading_tracking = _HIERARCHY[plan.hierarchy]
        secondary_offset, secondary_inset, secondary_width = _BALANCE[plan.balance]
        card_radius, group_radius = _FLOW_RADIUS[plan.layout_flow]
        continuity_border = _CONTINUITY_BORDER[plan.continuity]
        transition, hover_transform = _MOTION[plan.motion]
        font_family, line_height = _TYPOGRAPHY[plan.typography]
    except KeyError as exc:
        raise ValueError(f"unsupported canonical host vocabulary: {exc.args[0]}") from exc

    return CanonicalReflexTokens(
        fixture_template=fixture_template,
        desktop_columns=desktop_columns,
        support_columns=support_columns,
        gap=gap,
        group_gap=group_gap,
        card_padding=card_padding,
        group_padding=group_padding,
        card_radius=card_radius,
        group_radius=group_radius,
        heading_size=heading_size,
        heading_weight=heading_weight,
        heading_tracking=heading_tracking,
        secondary_offset=secondary_offset,
        secondary_inset=secondary_inset,
        secondary_width=secondary_width,
        continuity_border=continuity_border,
        transition=transition,
        hover_transform=hover_transform,
        font_family=font_family,
        line_height=line_height,
    )


__all__ = ["CanonicalReflexTokens", "project_reflex_tokens"]