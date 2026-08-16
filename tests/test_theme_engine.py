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
        # Empty id should raise ValueError
        invalid_theme_id = Theme(id="", display_name="Test Theme")
        with self.assertRaises(ValueError):
            invalid_theme_id.validate()

        # Empty display name should raise ValueError
        invalid_theme_name = Theme(id="test-theme", display_name="")
        with self.assertRaises(ValueError):
            invalid_theme_name.validate()

        # Registering non-Theme instance should raise TypeError
        with self.assertRaises(TypeError):
            self.registry.register_theme({"id": "not_a_theme_instance"})

    def test_partial_override_resolution(self):
        """Tests that partial overrides merge onto base tokens without mutating defaults."""
        custom_theme = Theme(
            id="test-neutral-override",
            display_name="Test Neutral Override",
            category="custom",
            description="Internal test override for contract verification.",
            colors={
                "primary": "#1068EB",
                "surface": "#111827"
            },
            radius={
                "md": "0.6rem"
            }
        )
        self.registry.register_theme(custom_theme)

        # Resolve the custom theme
        resolved_theme, token_groups = self.registry.resolve_theme("test-neutral-override")
        self.assertEqual(resolved_theme.id, "test-neutral-override")

        # Overridden values must be present
        self.assertEqual(token_groups["colors"]["primary"], "#1068EB")
        self.assertEqual(token_groups["colors"]["surface"], "#111827")
        self.assertEqual(token_groups["radius"]["md"], "0.6rem")

        # Unspecified values must inherit base token values
        self.assertEqual(token_groups["colors"]["text"], tokens.COLORS["text"])
        self.assertEqual(token_groups["colors"]["secondary"], tokens.COLORS["secondary"])
        self.assertEqual(token_groups["colors"]["success"], tokens.COLORS["success"])
        self.assertEqual(token_groups["spacing"]["md"], tokens.SPACING["md"])
        self.assertEqual(token_groups["radius"]["lg"], tokens.RADIUS["lg"])

        # Base tokens must remain unmutated
        self.assertEqual(tokens.COLORS["primary"], "#3B82F6")
        self.assertEqual(tokens.COLORS["surface"], "#1E293B")
        self.assertEqual(tokens.RADIUS["md"], "0.5rem")

    def test_theme_css_generation(self):
        """Tests CSS property generation for default theme and partial override theme."""
        css_default = generate_theme_css(DEFAULT_THEME_ID)
        self.assertIn(":root {", css_default)
        self.assertIn(f"--mm-color-primary: {tokens.COLORS['primary']};", css_default)
        self.assertIn(f"--mm-color-surface: {tokens.COLORS['surface']};", css_default)
        self.assertIn(".mm-typo-display {", css_default)

        # Register test override in global registry and verify custom CSS generation
        test_theme = Theme(
            id="test-neutral-override",
            display_name="Test Neutral Override",
            colors={"primary": "#1068EB"}
        )
        register_theme(test_theme)

        css_override = generate_theme_css("test-neutral-override")
        self.assertIn("--mm-color-primary: #1068EB;", css_override)
        self.assertIn(f"--mm-color-surface: {tokens.COLORS['surface']};", css_override)

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
