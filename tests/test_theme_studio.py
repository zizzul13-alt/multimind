"""
Unit and integration tests for Theme Studio (Draft state management, multi-session isolation, and surface rendering).
"""
import unittest
from unittest.mock import patch, MagicMock

import streamlit as st
from ui.themes import get_theme, list_themes
from ui.dna import get_dna
from ui.theme_studio.state import (
    ThemeStudioDraft,
    init_draft_from_base,
    get_or_create_draft,
    reset_draft_to_base,
    apply_draft_to_active_theme,
    SESSION_DRAFT_KEY
)
from ui.theme_studio.surface import render_theme_studio_surface


class TestThemeStudioState(unittest.TestCase):

    def setUp(self):
        # Clear session draft state and session custom themes before each test
        if SESSION_DRAFT_KEY in st.session_state:
            del st.session_state[SESSION_DRAFT_KEY]
        if "session_custom_themes" in st.session_state:
            del st.session_state["session_custom_themes"]

    def test_init_draft_from_theme_base(self):
        """Test initializing ThemeStudioDraft from a base Theme."""
        draft = init_draft_from_base("default", base_type="theme")
        self.assertEqual(draft.base_id, "default")
        self.assertEqual(draft.base_type, "theme")
        self.assertIn("primary", draft.colors)
        self.assertIn("font_family_base", draft.typography)
        self.assertIn("md", draft.radius)
        self.assertIn("md", draft.spacing)

    def test_init_draft_from_dna_base(self):
        """Test initializing ThemeStudioDraft from a base DesignDNA."""
        from ui.dna.bootstrap import ensure_proof_dna_and_themes_registered
        ensure_proof_dna_and_themes_registered()

        draft = init_draft_from_base("japan-print-ink", base_type="dna")
        self.assertEqual(draft.base_id, "japan-print-ink")
        self.assertEqual(draft.base_type, "dna")
        self.assertEqual(draft.display_name, "Japan Print / Ink")
        self.assertIn("primary", draft.colors)

    def test_draft_to_theme_conversion(self):
        """Test converting ThemeStudioDraft to a valid Theme dataclass instance."""
        draft = init_draft_from_base("default", base_type="theme")
        draft.colors["primary"] = "#FF0000"

        theme = draft.to_theme(custom_id="custom-test-theme")
        self.assertEqual(theme.id, "custom-test-theme")
        self.assertIn("Custom", theme.display_name)
        self.assertEqual(theme.colors["primary"], "#FF0000")
        self.assertEqual(theme.category, "custom")
        self.assertIsNotNone(theme.metadata)
        self.assertEqual(theme.metadata.author, "Theme Studio")

    def test_get_or_create_draft(self):
        """Test get_or_create_draft session state lifecycle."""
        self.assertNotIn(SESSION_DRAFT_KEY, st.session_state)
        draft = get_or_create_draft(default_base_id="default")
        self.assertIn(SESSION_DRAFT_KEY, st.session_state)
        self.assertEqual(draft.base_id, "default")

        # Mutate draft in session state and verify retrieval returns modified instance
        draft.colors["primary"] = "#123456"
        retrieved = get_or_create_draft()
        self.assertEqual(retrieved.colors["primary"], "#123456")

    def test_reset_draft_to_base(self):
        """Test resetting draft to base theme defaults."""
        draft = get_or_create_draft(default_base_id="default")
        draft.colors["primary"] = "#999999"

        reset_draft = reset_draft_to_base("default", base_type="theme")
        self.assertNotEqual(reset_draft.colors["primary"], "#999999")
        self.assertEqual(st.session_state[SESSION_DRAFT_KEY].colors["primary"], reset_draft.colors["primary"])

    def test_apply_draft_to_active_theme(self):
        """Test explicit Apply promotes draft to ThemeRegistry and sets active_theme."""
        draft = get_or_create_draft(default_base_id="default")
        draft.colors["primary"] = "#00FF00"

        active_theme_before = st.session_state.get("active_theme", "default")
        applied_theme = apply_draft_to_active_theme(draft)

        self.assertTrue(applied_theme.id.startswith("custom-default-"))
        self.assertEqual(st.session_state.active_theme, applied_theme.id)

        # Verify applied theme is now registered in global ThemeRegistry
        registered_theme = get_theme(applied_theme.id)
        self.assertEqual(registered_theme.id, applied_theme.id)
        self.assertEqual(registered_theme.colors["primary"], "#00FF00")

    def test_multi_session_custom_theme_isolation(self):
        """Regression test proving two independent session/user identities applying drafts derived from
        the same base receive distinct theme IDs AND complete discovery/visibility isolation in list_themes().
        """
        # Session A setup and apply
        st.session_state.session_custom_themes = set()
        draft_a = init_draft_from_base("default", base_type="theme")
        draft_a.colors["primary"] = "#FF0000"
        applied_theme_a = apply_draft_to_active_theme(draft_a)
        session_a_custom_themes = set(st.session_state.session_custom_themes)

        # Session B setup and apply (simulate independent session_state)
        st.session_state.session_custom_themes = set()
        draft_b = init_draft_from_base("default", base_type="theme")
        draft_b.colors["primary"] = "#0000FF"
        applied_theme_b = apply_draft_to_active_theme(draft_b)
        session_b_custom_themes = set(st.session_state.session_custom_themes)

        # Assert unique theme IDs generated per applied draft
        self.assertNotEqual(applied_theme_a.id, applied_theme_b.id)

        # Verify Session A visibility isolation: list_themes() in Session A context shows theme_a but NOT theme_b
        st.session_state.session_custom_themes = session_a_custom_themes
        visible_in_session_a = [t.id for t in list_themes()]
        self.assertIn(applied_theme_a.id, visible_in_session_a)
        self.assertNotIn(applied_theme_b.id, visible_in_session_a)

        # Verify Session B visibility isolation: list_themes() in Session B context shows theme_b but NOT theme_a
        st.session_state.session_custom_themes = session_b_custom_themes
        visible_in_session_b = [t.id for t in list_themes()]
        self.assertIn(applied_theme_b.id, visible_in_session_b)
        self.assertNotIn(applied_theme_a.id, visible_in_session_b)

        # Verify fresh Session C visibility isolation: list_themes() shows built-ins but NEITHER custom theme
        st.session_state.session_custom_themes = set()
        visible_in_session_c = [t.id for t in list_themes()]
        self.assertIn("default", visible_in_session_c)
        self.assertNotIn(applied_theme_a.id, visible_in_session_c)
        self.assertNotIn(applied_theme_b.id, visible_in_session_c)

    @patch("streamlit.rerun")
    @patch("streamlit.color_picker")
    @patch("streamlit.selectbox")
    @patch("streamlit.select_slider")
    @patch("streamlit.button")
    def test_render_theme_studio_surface(
        self,
        mock_button,
        mock_select_slider,
        mock_selectbox,
        mock_color_picker,
        mock_rerun
    ):
        """Test rendering the Theme Studio UI surface without errors."""
        mock_button.return_value = False
        mock_color_picker.side_effect = lambda label, value, key: value
        mock_select_slider.side_effect = lambda label, options, value, key: value
        mock_selectbox.side_effect = lambda label, options, **kwargs: options[0] if options else None

        # Render Theme Studio surface
        render_theme_studio_surface()

        # Confirm draft state was initialized during render
        self.assertIn(SESSION_DRAFT_KEY, st.session_state)


if __name__ == "__main__":
    unittest.main()
