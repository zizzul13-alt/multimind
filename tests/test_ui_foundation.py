"""
Unit tests for MultiMind UI Foundation (Design Tokens, CSS Foundation, and Primitives)
"""
import os
import unittest
from unittest.mock import patch, MagicMock
from ui.tokens import TYPOGRAPHY, SPACING, RADIUS, COLORS, SURFACES, BORDERS, generate_tokens_css
from ui.foundation import load_css, card_container, render_status_badge, CSS_PATH


class TestUIFoundation(unittest.TestCase):

    def test_restore_state_invalidation_keeps_authenticated_identity(self):
        from app import invalidate_restored_database_state

        state = type("StateMock", (dict,), {
            "__getattr__": lambda self, name: self.get(name),
            "__setattr__": lambda self, name, value: self.__setitem__(name, value),
        })({
            "user": "Alice",
            "user_id": "alice",
            "current_session": {"id": "old-session"},
            "sessions": {"old-session": {"id": "old-session"}},
            "memories": {"old-session": "hydrated memory"},
            "active_theme": "default",
        })

        invalidate_restored_database_state(state)

        self.assertEqual(state.user, "Alice")
        self.assertEqual(state.user_id, "alice")
        self.assertIsNone(state.current_session)
        self.assertEqual(state.sessions, {"old-session": {"id": "old-session"}})
        self.assertEqual(state.memories, {})
        self.assertEqual(state.active_theme, "default")

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
        """Test that load_css reads the CSS file and calls st.markdown with style tags for default and custom themes."""
        load_css()
        mock_markdown.assert_called_once()
        args, kwargs = mock_markdown.call_args
        self.assertTrue(args[0].startswith("<style>"))
        self.assertTrue(args[0].endswith("</style>"))
        self.assertIn("--mm-color-primary: #3B82F6;", args[0])
        self.assertIn(".stButton > button", args[0])
        self.assertTrue(kwargs.get("unsafe_allow_html"))

        mock_markdown.reset_mock()
        load_css("neutral-contrast-demo")
        mock_markdown.assert_called_once()
        args, kwargs = mock_markdown.call_args
        self.assertIn("--mm-color-primary: #D97706;", args[0])

        mock_markdown.reset_mock()
        load_css("nonexistent_invalid_theme_id")
        mock_markdown.assert_called_once()
        args, kwargs = mock_markdown.call_args
        self.assertIn("--mm-color-primary: #3B82F6;", args[0])

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



    @patch("streamlit.button")
    @patch("database.manager.DatabaseManager.get_sessions")
    def test_sidebar_session_button_api(self, mock_get_sessions, mock_button):
        """Test that sidebar session buttons call st.button with type= instead of invalid kind=."""
        import streamlit as st
        mock_get_sessions.return_value = [{"id": "session_12345678", "name": "Test Session Name", "mode": "coding"}]
        mock_button.return_value = False

        class StateMock(dict):
            def __getattr__(self, name):
                return self.get(name)
            def __setattr__(self, name, value):
                self[name] = value

        mock_st_state = StateMock({
            "user": "testuser",
            "user_id": "testuser",
            "current_session": None,
            "memories": {},
            "initialized": True
        })

        with patch("streamlit.session_state", mock_st_state), \
             patch("streamlit.sidebar"), \
             patch("streamlit.expander"), \
             patch("streamlit.text_input", return_value=""), \
             patch("streamlit.selectbox", return_value="coding"), \
             patch("streamlit.caption"), \
             patch("streamlit.divider"), \
             patch("streamlit.download_button"), \
             patch("streamlit.file_uploader"), \
             patch("os.path.exists", return_value=False):

            from app import show_sidebar
            show_sidebar()

        # Find session button calls
        session_button_calls = [
            call for call in mock_button.call_args_list
            if "key" in call.kwargs and call.kwargs["key"].startswith("sidebar_session_")
        ]

        # Must observe at least one session button call
        self.assertGreater(len(session_button_calls), 0, "No sidebar session button calls were made!")

        for call in session_button_calls:
            kwargs = call.kwargs
            self.assertNotIn("kind", kwargs, "st.button was called with invalid argument 'kind'")
            self.assertIn("type", kwargs, "st.button missing required 'type' argument")
            self.assertIn(kwargs["type"], ["primary", "secondary"])
            self.assertEqual(kwargs.get("help"), "Test Session Name", "st.button help parameter should preserve full session name")



    @patch("streamlit.rerun")
    @patch("streamlit.selectbox")
    @patch("database.manager.DatabaseManager.get_sessions")
    def test_theme_selector_switching(self, mock_get_sessions, mock_selectbox, mock_rerun):
        """Test that theme selectbox in sidebar receives registry options and updates active_theme state on change."""
        from ui.themes import list_themes, get_theme
        mock_get_sessions.return_value = []
        demo_theme = get_theme("neutral-contrast-demo")

        def selectbox_side_effect(*args, **kwargs):
            key = kwargs.get("key")
            if key == "settings_theme":
                return demo_theme
            elif key == "settings_archetype":
                return "chat_first"
            elif key == "settings_skill":
                return "default"
            return args[0][0] if args and isinstance(args[0], (list, tuple)) and len(args[0]) > 0 else None

        mock_selectbox.side_effect = selectbox_side_effect

        class StateMock(dict):
            def __getattr__(self, name):
                return self.get(name)
            def __setattr__(self, name, value):
                self[name] = value

        mock_st_state = StateMock({
            "user": "testuser",
            "user_id": "testuser",
            "active_theme": "default",
            "current_session": None,
            "memories": {},
            "initialized": True
        })

        with patch("streamlit.session_state", mock_st_state), \
             patch("streamlit.sidebar"), \
             patch("streamlit.expander"), \
             patch("streamlit.text_input", return_value=""), \
             patch("streamlit.caption"), \
             patch("streamlit.divider"), \
             patch("streamlit.button", return_value=False), \
             patch("streamlit.multiselect", return_value=[]), \
             patch("streamlit.toggle", return_value=False), \
             patch("streamlit.slider", return_value=1), \
             patch("streamlit.download_button"), \
             patch("streamlit.file_uploader"), \
             patch("os.path.exists", return_value=False):

            from app import show_sidebar
            show_sidebar()

        self.assertEqual(mock_st_state.active_theme, "neutral-contrast-demo")
        mock_rerun.assert_called_once()


    @patch("streamlit.markdown")
    def test_icon_font_preservation_regression(self, mock_markdown):
        """Test that Streamlit icon selectors are excluded from broad span typography and retain Material Symbols icon fonts across themes."""
        from ui.dna.bootstrap import ensure_proof_dna_and_themes_registered
        ensure_proof_dna_and_themes_registered()

        test_themes = ["default", "neutral-contrast-demo", "japan-print-ink", "chainsaw-man-inspired", "mushishi-inspired"]

        for theme_id in test_themes:
            mock_markdown.reset_mock()
            load_css(theme_id)
            mock_markdown.assert_called_once()
            args, _ = mock_markdown.call_args
            css = args[0]

            # Verify broad span typography rule excludes icon selectors
            self.assertIn(':not([data-testid="stIcon"])', css)
            self.assertIn(':not([data-testid="stExpanderToggleIcon"])', css)

            # Verify explicit Material Symbols icon font preservation exists for icon selectors
            self.assertIn('[data-testid="stIcon"]', css)
            self.assertIn('[data-testid="stExpanderToggleIcon"]', css)
            self.assertIn('"Material Symbols Rounded"', css)

if __name__ == "__main__":
    unittest.main()
