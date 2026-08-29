from unittest.mock import MagicMock, patch

import streamlit as st

from ui.presentation import shell


class TemplateWithUserVariable:
    def get_template(self, template_id):
        return {"prompt": "Review this value: {{value}}", "description": "Test template"}

    def apply_template(self, template_id, variables):
        return {"prompt": "Review this value: " + variables["value"]}


def test_template_preview_escapes_user_controlled_markup_but_keeps_prompt_raw():
    payload = "<b>owned</b>"
    st.session_state.clear()
    columns = [MagicMock()]

    try:
        with patch.object(shell.st, "caption"), \
             patch.object(shell.st, "columns", return_value=columns), \
             patch.object(shell.st, "text_input", return_value=payload), \
             patch.object(shell, "card_container") as card:
            prompt = shell._render_template_variables_and_preview(
                TemplateWithUserVariable(), "template-id"
            )
    finally:
        st.session_state.clear()

    rendered_html = card.call_args.args[0]
    assert prompt == "Review this value: <b>owned</b>"
    assert "<pre class='mm-typo-mono'>Review this value: &lt;b&gt;owned&lt;/b&gt;</pre>" in rendered_html
    assert "<pre class='mm-typo-mono'>Review this value: <b>owned</b></pre>" not in rendered_html


def test_template_preview_preserves_normal_plain_text():
    st.session_state.clear()
    columns = [MagicMock()]

    try:
        with patch.object(shell.st, "caption"), \
             patch.object(shell.st, "columns", return_value=columns), \
             patch.object(shell.st, "text_input", return_value="normal value"), \
             patch.object(shell, "card_container") as card:
            shell._render_template_variables_and_preview(TemplateWithUserVariable(), "template-id")
    finally:
        st.session_state.clear()

    assert "Review this value: normal value" in card.call_args.args[0]
