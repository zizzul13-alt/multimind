"""
Tests for S7.1 Theme Expression Completion & Custom Component Theme Preview Spike
"""
import os
import pytest
from ui.components.theme_preview_spike.preview_spike import (
    normalize_payload,
    DEFAULT_PREVIEW_PAYLOAD,
    render_theme_preview_spike
)


def test_normalize_payload_defaults():
    """Verify normalize_payload returns valid defaults for non-dict or empty inputs."""
    assert normalize_payload(None) == DEFAULT_PREVIEW_PAYLOAD
    assert normalize_payload([]) == DEFAULT_PREVIEW_PAYLOAD
    assert normalize_payload("invalid") == DEFAULT_PREVIEW_PAYLOAD


def test_normalize_payload_valid():
    """Verify normalize_payload validates and accepts valid structured payloads."""
    valid_data = {
        "primary": "#EF4444",
        "radius": "12px",
        "density": "compact",
        "applied_at": "2026-08-17T00:00:00Z"
    }
    normalized = normalize_payload(valid_data)
    assert normalized["primary"] == "#EF4444"
    assert normalized["radius"] == "12px"
    assert normalized["density"] == "compact"
    assert normalized["applied_at"] == "2026-08-17T00:00:00Z"


def test_normalize_payload_malformed_fields():
    """Verify malformed payload fields fall back safely to defaults."""
    malformed_data = {
        "primary": "invalid-color",
        "radius": "not-a-radius",
        "density": "super-dense"
    }
    normalized = normalize_payload(malformed_data)
    assert normalized["primary"] == DEFAULT_PREVIEW_PAYLOAD["primary"]
    assert normalized["radius"] == DEFAULT_PREVIEW_PAYLOAD["radius"]
    assert normalized["density"] == DEFAULT_PREVIEW_PAYLOAD["density"]


def test_css_token_consumption_rules():
    """Verify ui/style.css contains expected semantic variable overrides for native elements."""
    css_path = os.path.join("ui", "style.css")
    assert os.path.exists(css_path), "ui/style.css must exist"

    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    # Headings mapping check
    assert ".stApp h1, .stApp h2, .stApp h3" in css_content or ".stApp h1" in css_content
    assert "font-family: var(--mm-font-base);" in css_content
    assert "color: var(--mm-color-text);" in css_content

    # Chat Message Container & Content
    assert '[data-testid="stChatMessage"]' in css_content
    assert "background-color: var(--mm-color-surface);" in css_content
    assert "border: 1px solid var(--mm-color-border);" in css_content
    assert "border-radius: var(--mm-radius-md);" in css_content

    # Metric
    assert '[data-testid="stMetric"]' in css_content
    assert '[data-testid="stMetricLabel"]' in css_content
    assert "color: var(--mm-color-text-muted);" in css_content

    # Radio
    assert ".stRadio label" in css_content or '[data-testid="stRadio"] label' in css_content

    # Ensure no theme-specific hardcoded CSS classes or theme names exist
    assert "japan-print" not in css_content.lower()
    assert "chainsaw" not in css_content.lower()
    assert "mushishi" not in css_content.lower()
