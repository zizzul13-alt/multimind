"""
MultiMind AI - Brand & Material Presentation Seam
Provides generic presentation entry point for rendering active brand identity
and bound material assets using Streamlit image primitives with bounded sizing.
"""
from typing import Any, Optional
import streamlit as st

from ui.dna_bridge import BridgeMaterialResult, resolve_brand_material


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
    theme_or_dna_input: Any,
    user_label: str = "",
    container_kind: str = "sidebar"
) -> BridgeMaterialResult:
    """
    Authoritative brand & material presentation seam.
    Resolves optional DNA material through the small public bridge and renders
    using safe Streamlit image primitives. If private DNA is unavailable, the
    bridge returns a deterministic fallback and standard MultiMind identity is
    rendered without importing private/quarantined types here.
    """
    res = resolve_brand_material(theme_or_dna_input)
    img_width = _get_ornament_width(res.ornament_emphasis)

    badge_html = f"<span class='mm-badge mm-badge-info'>👤 {user_label}</span>" if user_label else ""

    if res.is_resolved and res.resolved_path and img_width > 0:
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
