"""
MultiMind AI - UI Foundation Utilities & Helpers
Provides lightweight helpers for injecting foundation CSS and rendering reusable primitives.
"""
import os
import streamlit as st
from ui.tokens import COLORS, SPACING, RADIUS

# Path to CSS file relative to this module
CSS_PATH = os.path.join(os.path.dirname(__file__), "style.css")


def load_css():
    """Reads CSS foundation file and injects it into Streamlit."""
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def card_container(content_html: str, elevated: bool = False):
    """Renders a card container surface using token-backed primitive styling."""
    css_class = "mm-card-elevated" if elevated else "mm-card"
    st.markdown(f'<div class="{css_class}">{content_html}</div>', unsafe_allow_html=True)


def render_status_badge(text: str, variant: str = "info"):
    """Renders a semantic status badge primitive.

    Variants: success, warning, danger, info
    """
    valid_variants = ("success", "warning", "danger", "info")
    badge_variant = variant if variant in valid_variants else "info"
    st.markdown(
        f'<span class="mm-badge mm-badge-{badge_variant}">{text}</span>',
        unsafe_allow_html=True
    )
