"""
Unit tests for MultiMind UI Foundation (Design Tokens, CSS Foundation, and Primitives)
"""
import os
import unittest
from unittest.mock import patch, MagicMock
from ui.tokens import TYPOGRAPHY, SPACING, RADIUS, COLORS, SURFACES, BORDERS, generate_tokens_css
from ui.foundation import load_css, card_container, render_status_badge, CSS_PATH


class TestUIFoundation(unittest.TestCase):

    def test_design_tokens_structure(self):
        """Test that essential design tokens exist and contain mandatory semantic roles."""
        # Typography
        self.assertIn("roles", TYPOGRAPHY)
        expected_typo_roles = ["display", "heading", "subheading", "body", "body_small", "caption", "label", "mono"]
        for role in expected_typo_roles:
            self.assertIn(role, TYPOGRAPHY["roles"])
            self.assertIn("size", TYPOGRAPHY["roles"][role])

        # Spacing
        expected_spacing = ["xs", "sm", "md", "lg", "xl", "2xl"]
        for s in expected_spacing:
            self.assertIn(s, SPACING)

        # Radius
        expected_radius = ["none", "sm", "md", "lg", "pill"]
        for r in expected_radius:
            self.assertIn(r, RADIUS)

        # Semantic Colors (including refined interaction state and input tokens)
        expected_colors = [
            "primary", "primary_hover", "primary_active", "secondary", "secondary_hover",
            "accent", "background", "surface", "surface_elevated", "surface_muted",
            "surface_hover", "surface_input", "text", "text_muted", "text_disabled",
            "border", "border_subtle", "border_hover", "border_focus", "focus_ring",
            "success", "warning", "danger", "info"
        ]
        for c in expected_colors:
            self.assertIn(c, COLORS)

        # Surfaces & Borders
        self.assertIn("surface", SURFACES)
        self.assertIn("surface_hover", SURFACES)
        self.assertIn("surface_input", SURFACES)
        self.assertIn("default", BORDERS)
        self.assertIn("hover", BORDERS)
        self.assertIn("focus", BORDERS)

    def test_generate_tokens_css(self):
        """Test that generate_tokens_css produces CSS custom properties and typography classes."""
        css = generate_tokens_css()
        self.assertIn(":root {", css)
        self.assertIn("--mm-color-primary:", css)
        self.assertIn("--mm-color-surface-input:", css)
        self.assertIn("--mm-color-focus-ring:", css)
        self.assertIn("--mm-space-md:", css)
        self.assertIn(".mm-typo-display {", css)
        self.assertIn(".mm-typo-body-small {", css)

    def test_css_foundation_file_exists(self):
        """Test that the CSS foundation file exists at the expected path."""
        self.assertTrue(os.path.exists(CSS_PATH), f"CSS file not found at {CSS_PATH}")

    @patch("streamlit.markdown")
    def test_load_css(self, mock_markdown):
        """Test that load_css reads the CSS file and calls st.markdown with style tags."""
        load_css()
        mock_markdown.assert_called_once()
        args, kwargs = mock_markdown.call_args
        self.assertTrue(args[0].startswith("<style>"))
        self.assertTrue(args[0].endswith("</style>"))
        self.assertIn("--mm-color-primary:", args[0])
        self.assertIn(".stButton > button", args[0])
        self.assertTrue(kwargs.get("unsafe_allow_html"))

    @patch("streamlit.markdown")
    def test_card_container_rendering(self, mock_markdown):
        """Test card_container helper renders correct HTML wrapper classes."""
        card_container("<span>Test Content</span>", variant="default")
        mock_markdown.assert_called_with('<div class="mm-card"><span>Test Content</span></div>', unsafe_allow_html=True)

        card_container("<span>Elevated Content</span>", variant="elevated")
        mock_markdown.assert_called_with('<div class="mm-card-elevated"><span>Elevated Content</span></div>', unsafe_allow_html=True)

        card_container("<span>Muted Content</span>", variant="muted")
        mock_markdown.assert_called_with('<div class="mm-card-muted"><span>Muted Content</span></div>', unsafe_allow_html=True)

    @patch("streamlit.markdown")
    def test_render_status_badge(self, mock_markdown):
        """Test status badge rendering for valid and fallback variants."""
        render_status_badge("Success Badge", variant="success")
        mock_markdown.assert_called_with(
            '<span class="mm-badge mm-badge-success">Success Badge</span>',
            unsafe_allow_html=True
        )

        render_status_badge("Invalid Badge", variant="invalid_variant")
        mock_markdown.assert_called_with(
            '<span class="mm-badge mm-badge-info">Invalid Badge</span>',
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    unittest.main()
