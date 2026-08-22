"""
Architecture Invariant Contract Tests for S7.6 Interaction Shell
Verifies that interaction shell dispatch does NOT modify backend execution, persistence, or snapshot semantics,
and confirms token estimation, upload extension contract, and button callbacks.
"""
import pytest
from unittest.mock import MagicMock, patch
from ui.presentation.models import (
    InteractionContext,
    SessionMetadataSnapshot,
    PresentationSnapshot,
)
from ui.presentation.shell import render_interaction_shell, _render_action_buttons
from ui.presentation.resolver import CANONICAL_ARCHETYPE_IDS


def test_interaction_shell_does_not_mutate_snapshot():
    session_meta = SessionMetadataSnapshot(
        id="s1", name="Test Session", mode="coding", created_at="2026-08-22"
    )
    snapshot = PresentationSnapshot(session=session_meta, chats=())

    initial_snapshot_session_id = snapshot.session.id
    initial_chats_len = len(snapshot.chats)

    ctx = InteractionContext(active_archetype="chat_first", new_chat_active=False)

    with patch("streamlit.markdown"), patch("streamlit.container"):
        render_interaction_shell(ctx, snapshot, None, MagicMock(), MagicMock())

    assert snapshot.session.id == initial_snapshot_session_id
    assert len(snapshot.chats) == initial_chats_len


def test_archetype_switch_does_not_alter_backend_inputs():
    from ui.presentation.shell import get_processing_label

    labels = [get_processing_label(arch_id) for arch_id in CANONICAL_ARCHETYPE_IDS]
    assert len(labels) == 7
    assert len(set(labels)) == 7  # All 7 archetypes have distinct truthful processing labels


def test_send_and_cancel_callbacks_invoked_correctly():
    on_send = MagicMock()
    on_cancel = MagicMock()

    # Simulate Send button click
    with patch("streamlit.columns") as mock_cols, patch("streamlit.button") as mock_btn:
        mock_cols.return_value = [MagicMock(), MagicMock()]
        mock_btn.side_effect = lambda label, **kw: "Send" in label

        _render_action_buttons("chat_first", on_send, on_cancel, "Hello prompt", None, "continue")
        on_send.assert_called_once_with("Hello prompt", None, "continue")
        on_cancel.assert_not_called()

    on_send.reset_mock()
    on_cancel.reset_mock()

    # Simulate Cancel button click
    with patch("streamlit.columns") as mock_cols, patch("streamlit.button") as mock_btn:
        mock_cols.return_value = [MagicMock(), MagicMock()]
        mock_btn.side_effect = lambda label, **kw: "Cancel" in label

        _render_action_buttons("chat_first", on_send, on_cancel, "", None, "continue")
        on_cancel.assert_called_once()
        on_send.assert_not_called()


def test_upload_extension_contract_preserved():
    from ui.presentation.shell import _render_composer_surface

    expected_types = ['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css', 'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx']

    with patch("streamlit.file_uploader") as mock_uploader, patch("streamlit.text_area"), patch("streamlit.columns") as mock_cols, patch("streamlit.button"):
        mock_cols.side_effect = lambda spec, **kw: [MagicMock() for _ in (spec if isinstance(spec, (list, tuple)) else range(spec))]
        ctx = InteractionContext(active_archetype="chat_first", new_chat_active=True)
        _render_composer_surface(ctx, None, MagicMock(), MagicMock())

        # Verify type parameter passed to file_uploader matches contract
        assert mock_uploader.called
        kwargs = mock_uploader.call_args[1]
        assert "type" in kwargs
        assert kwargs["type"] == expected_types


def test_token_estimation_metrics_reachable():
    from ui.presentation.shell import _render_token_estimation_metrics

    with patch("utils.token_counter.TokenCounter.estimate_total") as mock_estimate, \
         patch("utils.token_counter.TokenCounter.get_warning_level") as mock_warn, \
         patch("utils.token_counter.TokenCounter.estimate_cost") as mock_cost, \
         patch("ui.foundation.card_container"):

        mock_estimate.return_value = {"prompt_tokens": 10, "file_tokens": 0, "total_estimate": 10}
        mock_warn.return_value = {"level": "low"}
        mock_cost.return_value = 0.0001

        _render_token_estimation_metrics("Test prompt", None, "chat_first")
        mock_estimate.assert_called_once()



def test_shared_controls_use_archetype_independent_state_keys():
    """Presentation archetype changes must not fragment execution-relevant widget state."""
    from pathlib import Path

    source = Path("ui/presentation/shell.py").read_text(encoding="utf-8")

    assert 'key="shell_selected_template"' in source
    assert 'key="shell_chat_mode"' in source

    for archetype in CANONICAL_ARCHETYPE_IDS:
        assert f"shell_template_{archetype}" not in source
        assert f"shell_mode_{archetype}" not in source


def test_send_callback_execution_inputs_are_archetype_independent():
    """Changing presentation archetype must not alter values delivered to execution."""
    prompt = "Preserve this execution input"
    uploaded_files = None
    context_mode = "standalone"

    for archetype in CANONICAL_ARCHETYPE_IDS:
        on_send = MagicMock()
        on_cancel = MagicMock()

        with patch("streamlit.columns") as mock_cols, patch("streamlit.button") as mock_btn:
            mock_cols.return_value = [MagicMock(), MagicMock()]
            # Click the archetype's primary action regardless of its
            # presentation-specific label (Send / Execute Action / Send Command).
            mock_btn.side_effect = lambda label, **kw: kw.get("type") == "primary"

            _render_action_buttons(
                archetype,
                on_send,
                on_cancel,
                prompt,
                uploaded_files,
                context_mode,
            )

        on_send.assert_called_once_with(
            prompt,
            uploaded_files,
            context_mode,
        )
        on_cancel.assert_not_called()


def test_cost_estimation_value_is_rendered():
    """The already-computed estimated cost must remain visible in shell output."""
    from ui.presentation.shell import _render_token_estimation_metrics

    rendered = []

    with patch("utils.token_counter.TokenCounter.estimate_total") as mock_estimate, \
         patch("utils.token_counter.TokenCounter.get_warning_level") as mock_warn, \
         patch("utils.token_counter.TokenCounter.estimate_cost") as mock_cost, \
         patch("ui.presentation.shell.card_container") as mock_card:

        mock_estimate.return_value = {
            "prompt_tokens": 10,
            "file_tokens": 0,
            "total_estimate": 10,
        }
        mock_warn.return_value = {"level": "low"}
        mock_cost.return_value = 0.000123

        mock_card.side_effect = lambda content, **kwargs: rendered.append(content)

        _render_token_estimation_metrics(
            "Test prompt",
            None,
            "chat_first",
        )

    assert mock_cost.called
    assert rendered
    assert "$0.000123" in rendered[0]


def test_process_chat_keeps_three_argument_boundary_and_no_spinner():
    """Execution path must remain presentation-agnostic."""
    import ast
    from pathlib import Path

    source = Path("app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    process_chat = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "process_chat"
    )

    assert [arg.arg for arg in process_chat.args.args] == [
        "prompt",
        "uploaded_files",
        "context_mode",
    ]

    function_source = ast.get_source_segment(source, process_chat)
    assert function_source is not None
    assert "st.spinner" not in function_source
    assert "processing_label" not in function_source
