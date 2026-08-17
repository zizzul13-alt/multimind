"""
MultiMind AI - Custom Component Theme Preview Spike (S7.1 Recovery)
Provides an isolated, bidirectional custom component wrapper with payload normalization & fallback safety.
"""
import os
import logging
from typing import Dict, Any, Optional
import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger(__name__)

_PARENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Declare static component using st.components.v1
_theme_preview_component = components.declare_component(
    "theme_preview_spike",
    path=_PARENT_DIR
)

DEFAULT_PREVIEW_PAYLOAD: Dict[str, Any] = {
    "primary": "#3B82F6",
    "radius": "8px",
    "density": "comfortable"
}


def normalize_payload(data: Any) -> Dict[str, Any]:
    """Validates and normalizes structured component payload safely.

    Guarantees non-null dict output conforming to expected schema.
    """
    if not isinstance(data, dict):
        logger.warning(f"Component return payload is not a dict: {type(data)}. Using defaults.")
        return dict(DEFAULT_PREVIEW_PAYLOAD)

    primary = str(data.get("primary", DEFAULT_PREVIEW_PAYLOAD["primary"]))
    if not (primary.startswith("#") and len(primary) in (4, 7, 9)):
        primary = DEFAULT_PREVIEW_PAYLOAD["primary"]

    radius = str(data.get("radius", DEFAULT_PREVIEW_PAYLOAD["radius"]))
    if not radius.endswith("px") and not radius.endswith("rem"):
        radius = DEFAULT_PREVIEW_PAYLOAD["radius"]

    density = str(data.get("density", DEFAULT_PREVIEW_PAYLOAD["density"]))
    if density not in ("compact", "comfortable", "spacious"):
        density = DEFAULT_PREVIEW_PAYLOAD["density"]

    normalized = {
        "primary": primary,
        "radius": radius,
        "density": density
    }
    if "applied_at" in data:
        normalized["applied_at"] = str(data["applied_at"])

    return normalized


def render_theme_preview_spike(
    initial_payload: Optional[Dict[str, Any]] = None,
    key: Optional[str] = "theme_preview_spike_comp"
) -> Dict[str, Any]:
    """Renders the theme preview custom component spike safely behind a dev gate.

    Returns normalized structured data sent from client upon explicit Apply click,
    or default fallback dict if missing/uninitialized/failed.
    """
    safe_initial = normalize_payload(initial_payload) if initial_payload else dict(DEFAULT_PREVIEW_PAYLOAD)

    try:
        raw_result = _theme_preview_component(
            initial_payload=safe_initial,
            key=key,
            default=safe_initial
        )
        return normalize_payload(raw_result)
    except Exception as e:
        logger.error(f"Error rendering theme_preview_spike component: {e}")
        return dict(DEFAULT_PREVIEW_PAYLOAD)
