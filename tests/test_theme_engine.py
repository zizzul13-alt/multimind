"""
Unit tests for MultiMind AI Theme Engine Core (S5.1)
"""
import unittest
from ui import tokens
from ui.themes import (
    Theme,
    ThemeMetadata,
    ThemeRegistry,
    DEFAULT_THEME_ID,
    get_registry,
    register_theme,
    list_themes,
    get_theme,
    resolve_theme,
    generate_theme_css,
)


class TestThemeEngineCore(unittest.TestCase):

    def setUp(self):
        """Creates a fresh ThemeRegistry instance for isolated test runs."""
        self.registry = ThemeRegistry()

    def test_default_theme_registration_and_lookup(self):
        """Tests that default theme is registered automatically and resolves correctly."""
        themes = self.registry.list_themes()
        self.assertEqual(len(themes), 1)
        self.assertEqual(themes[0].id, DEFAULT_THEME_ID)

        default_theme = self.registry.get_theme(DEFAULT_THEME_ID)
        self.assertEqual(default_theme.id, DEFAULT_THEME_ID)
        self.assertEqual(default_theme.display_name, "MultiMind Default")
        self.assertEqual(default_theme.colors["primary"], tokens.COLORS["primary"])

    def test_unknown_or_invalid_theme_id_fallback(self):
        """Tests that unknown, None, or empty theme IDs fall back safely to default theme."""
        fallback_unknown = self.registry.get_theme("unknown-nonexistent-theme")
        self.assertEqual(fallback_unknown.id, DEFAULT_THEME_ID)

        fallback_none = self.registry.get_theme(None)
        self.assertEqual(fallback_none.id, DEFAULT_THEME_ID)

        fallback_empty = self.registry.get_theme("   ")
        self.assertEqual(fallback_empty.id, DEFAULT_THEME_ID)

    def test_theme_registration_validation(self):
        """Tests validation rules during theme instantiation and registration."""
        invalid_theme_id = Theme(id="", display_name="Test Theme")
        with self.assertRaises(ValueError):
            invalid_theme_id.validate()

        invalid_theme_name = Theme(id="test-theme", display_name="")
        with self.assertRaises(ValueError):
            invalid_theme_name.validate()

        with self.assertRaises(TypeError):
            self.registry.register_theme({"id": "not_a_theme_instance"})

    def test_partial_override_resolution_for_all_override_groups(self):
        """Tests that every supported override group (colors, typography, spacing, radius) merges without mutating defaults."""
        custom_theme = Theme(
            id="test-neutral-override",
            display_name="Test Neutral Override",
            category="custom",
            description="Internal test override for contract verification.",
            colors={
                "primary": "#1068EB",
                "surface": "#111827",
                "border": "#374151",
            },
            typography={
                "font_family_base": "CustomFont, sans-serif",
                "roles": {
                    "heading": {"size": "1.75rem", "weight": "700", "line_height": "1.3"}
                }
            },
            spacing={
                "md": "1.25rem"
            },
            radius={
                "md": "0.6rem"
            }
        )
        self.registry.register_theme(custom_theme)

        resolved_theme, token_groups = self.registry.resolve_theme("test-neutral-override")
        self.assertEqual(resolved_theme.id, "test-neutral-override")

        # Check every overridden group
        self.assertEqual(token_groups["colors"]["primary"], "#1068EB")
        self.assertEqual(token_groups["colors"]["surface"], "#111827")
        self.assertEqual(token_groups["colors"]["border"], "#374151")
        self.assertEqual(token_groups["typography"]["font_family_base"], "CustomFont, sans-serif")
        self.assertEqual(token_groups["typography"]["roles"]["heading"]["size"], "1.75rem")
        self.assertEqual(token_groups["spacing"]["md"], "1.25rem")
        self.assertEqual(token_groups["radius"]["md"], "0.6rem")

        # Unspecified values must inherit base token values
        self.assertEqual(token_groups["colors"]["text"], tokens.COLORS["text"])
        self.assertEqual(token_groups["spacing"]["lg"], tokens.SPACING["lg"])
        self.assertEqual(token_groups["radius"]["lg"], tokens.RADIUS["lg"])

        # Base tokens must remain unmutated
        self.assertEqual(tokens.COLORS["primary"], "#3B82F6")
        self.assertEqual(tokens.COLORS["surface"], "#1E293B")
        self.assertEqual(tokens.TYPOGRAPHY["font_family_base"], "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif")
        self.assertEqual(tokens.SPACING["md"], "1rem")
        self.assertEqual(tokens.RADIUS["md"], "0.5rem")

    def test_observable_css_generation_for_all_override_groups(self):
        """Verifies that every supported override group directly affects generated CSS custom properties."""
        test_theme = Theme(
            id="test-neutral-css-override",
            display_name="Test Neutral CSS Override",
            colors={
                "primary": "#1068EB",
                "surface_input": "#050B1A",
                "border_focus": "#2563EB",
            },
            typography={
                "font_family_base": "Roboto, sans-serif",
                "roles": {
                    "body": {"size": "1.1rem", "weight": "400", "line_height": "1.6"}
                }
            },
            spacing={
                "lg": "1.75rem"
            },
            radius={
                "sm": "0.3rem"
            }
        )
        register_theme(test_theme)

        css_output = generate_theme_css("test-neutral-css-override")

        # Check that colors (including surface and border roles) affect CSS
        self.assertIn("--mm-color-primary: #1068EB;", css_output)
        self.assertIn("--mm-color-surface-input: #050B1A;", css_output)
        self.assertIn("--mm-color-border-focus: #2563EB;", css_output)

        # Check typography affects CSS
        self.assertIn("--mm-font-base: Roboto, sans-serif;", css_output)
        self.assertIn("font-size: 1.1rem;", css_output)

        # Check spacing affects CSS
        self.assertIn("--mm-space-lg: 1.75rem;", css_output)

        # Check radius affects CSS
        self.assertIn("--mm-radius-sm: 0.3rem;", css_output)

    def test_theme_metadata_and_category_contract(self):
        """Tests that ThemeMetadata and category fields store architectural contract metadata cleanly."""
        meta = ThemeMetadata(
            description="Test metadata",
            author="Jules Agent",
            license="MIT",
            source="Internal Test",
            attribution="MultiMind Test Suite"
        )
        theme = Theme(
            id="test-meta-theme",
            display_name="Meta Test Theme",
            category="environment",
            metadata=meta
        )
        self.assertEqual(theme.category, "environment")
        self.assertIsNotNone(theme.metadata)
        self.assertEqual(theme.metadata.author, "Jules Agent")
        self.assertEqual(theme.metadata.license, "MIT")


if __name__ == "__main__":
    unittest.main()
