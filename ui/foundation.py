"""
MultiMind AI - UI Foundation Utilities & Helpers
Provides lightweight helpers for injecting foundation CSS and rendering reusable primitives.
"""
import os
import streamlit as st
from ui.themes import generate_theme_css

CSS_PATH = os.path.join(os.path.dirname(__file__), "style.css")


def load_css():
    """Dynamically loads token CSS custom properties and foundation CSS rules into Streamlit via Theme Engine."""
    token_css = generate_theme_css()
    static_css = ""
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            static_css = f.read()

    combined_css = f"{token_css}\n\n{static_css}"
    st.markdown(f"<style>{combined_css}</style>", unsafe_allow_html=True)


def card_container(content_html: str, variant: str = "default"):
    """Renders a card container surface using token-backed primitive styling.

    Variants: default, elevated, muted
    """
    valid_variants = {
        "default": "mm-card",
        "elevated": "mm-card-elevated",
        "muted": "mm-card-muted"
    }
    css_class = valid_variants.get(variant, "mm-card")
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
