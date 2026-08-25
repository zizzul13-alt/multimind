"""
MultiMind AI - Brand & Material Presentation Seam
Provides generic presentation entry point for rendering active brand identity
and bound material assets using Streamlit image primitives with bounded sizing.
"""
from typing import Optional, Union
import streamlit as st

from ui.dna.resolver import resolve_material, resolve_source_dna, MaterialResolutionResult
from ui.dna.models import DesignDNA
from ui.themes import Theme


def _get_ornament_width(ornament_emphasis: Optional[str]) -> int:
    """Generic mapping from ornament_emphasis semantic intent to bounded image width."""
    if ornament_emphasis == "none":
        return 0
    elif ornament_emphasis == "subtle":
        return 24
    elif ornament_emphasis == "prominent":
        return 40
    # "selective" or None/default
    return 32


def render_brand_identity(
    theme_or_dna_input: Union[str, Theme, DesignDNA, None],
    user_label: str = "",
    container_kind: str = "sidebar"
) -> MaterialResolutionResult:
    """
    Authoritative brand & material presentation seam.
    Resolves material bound to active Theme/DNA and renders using safe Streamlit image primitives.
    Generic consumption of 'ornament_emphasis' determines bounded asset rendering size.
    Falls back gracefully to standard MultiMind identity if material is unavailable or invalid.

    Returns the MaterialResolutionResult payload for testing and verification.
    """
    res = resolve_material(theme_or_dna_input)
    source_dna = resolve_source_dna(theme_or_dna_input)
    ornament_emphasis = source_dna.ornament_emphasis if source_dna else None
    img_width = _get_ornament_width(ornament_emphasis)

    badge_html = f"<span class='mm-badge mm-badge-info'>👤 {user_label}</span>" if user_label else ""

    if res.is_resolved and res.resolved_path and img_width > 0:
        # Bounded Streamlit image asset rendering with generic ornament_emphasis width
        col1, col2 = st.columns([0.22, 1.0])
        with col1:
            st.image(res.resolved_path, width=img_width)
        with col2:
            if badge_html:
                st.markdown(
                    f"<div class='mm-flex-between' style='align-items: center; min-height: 32px;'>"
                    f"<span class='mm-typo-heading'>MultiMind</span>{badge_html}"
                    f"</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown("<span class='mm-typo-heading'>MultiMind</span>", unsafe_allow_html=True)
    else:
        # Safe existing fallback identity
        if badge_html:
            st.markdown(
                f"<div class='mm-flex-between'>"
                f"<span class='mm-typo-heading'>🤖 MultiMind</span>"
                f"{badge_html}"
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown("<span class='mm-typo-heading'>🤖 MultiMind</span>", unsafe_allow_html=True)

    return res
