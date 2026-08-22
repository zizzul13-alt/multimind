"""
Tests for MultiMind AI S7.6 Archetype-Aware Interaction Shell
"""
import pytest
from unittest.mock import MagicMock, patch
from ui.presentation.models import (
    InteractionContext,
    SessionMetadataSnapshot,
    PresentationSnapshot,
    ChatMessageSnapshot,
)
from ui.presentation.shell import (
    render_interaction_shell,
    get_processing_label,
)
from ui.presentation.resolver import CANONICAL_ARCHETYPE_IDS


def test_interaction_context_immutability():
    session_meta = SessionMetadataSnapshot(
        id="sess-123",
        name="Test Session",
        mode="coding",
        created_at="2026-08-22 00:00:00"
    )
    ctx = InteractionContext(
        active_archetype="chat_first",
        new_chat_active=True,
        session=session_meta,
        prompt_text="Hello world",
        selected_template="code_review",
        chat_mode="continue",
        uploaded_files_count=2,
        uploaded_file_names=("file1.py", "file2.js"),
        is_processing=False
    )

    assert ctx.active_archetype == "chat_first"
    assert ctx.new_chat_active is True
    assert ctx.uploaded_files_count == 2
    assert ctx.uploaded_file_names == ("file1.py", "file2.js")

    with pytest.raises(Exception):
        ctx.active_archetype = "terminal_hacker"


def test_processing_labels_for_all_canonical_archetypes():
    for arch_id in CANONICAL_ARCHETYPE_IDS:
        label = get_processing_label(arch_id)
        assert isinstance(label, str)
        assert len(label) > 0

    # Test unknown fallback
    unknown_label = get_processing_label("unknown_archetype_xyz")
    assert unknown_label == "🤖 Agents debating..."


@patch("streamlit.markdown")
@patch("streamlit.button")
@patch("streamlit.text_area")
@patch("streamlit.file_uploader")
@patch("streamlit.selectbox")
@patch("streamlit.radio")
@patch("streamlit.columns")
@patch("streamlit.container")
@patch("streamlit.expander")
def test_all_seven_archetypes_render_interaction_shell(
    mock_expander,
    mock_container,
    mock_columns,
    mock_radio,
    mock_selectbox,
    mock_uploader,
    mock_text_area,
    mock_button,
    mock_markdown,
):
    # Setup mocks
    mock_columns.side_effect = lambda spec, **kw: [MagicMock() for _ in (spec if isinstance(spec, (list, tuple)) else range(spec))]
    mock_container.return_value.__enter__ = MagicMock()
    mock_container.return_value.__exit__ = MagicMock()
    mock_expander.return_value.__enter__ = MagicMock()
    mock_expander.return_value.__exit__ = MagicMock()
    mock_button.return_value = False
    mock_text_area.return_value = "Test prompt"
    mock_radio.return_value = "🧵 Continue"
    mock_selectbox.return_value = ""

    session_meta = SessionMetadataSnapshot(
        id="s1", name="Test Session", mode="coding", created_at="2026-08-22"
    )
    snapshot = PresentationSnapshot(
        session=session_meta,
        chats=(
            ChatMessageSnapshot(
                id="c1",
                prompt="Hi",
                mode="continue",
                final_answer="Hello!",
                tokens_used=100,
                cost=0.001,
            ),
        ),
    )

    dummy_send = MagicMock()
    dummy_cancel = MagicMock()

    for arch_id in CANONICAL_ARCHETYPE_IDS:
        ctx = InteractionContext(
            active_archetype=arch_id,
            new_chat_active=True,
            session=session_meta,
        )
        # Verify render completes without exception
        render_interaction_shell(ctx, snapshot, None, dummy_send, dummy_cancel)


def test_unknown_archetype_safe_fallback_in_shell():
    session_meta = SessionMetadataSnapshot(
        id="s1", name="Test Session", mode="coding", created_at="2026-08-22"
    )
    snapshot = PresentationSnapshot(session=session_meta)
    ctx = InteractionContext(
        active_archetype="non_existent_archetype_abc",
        new_chat_active=False,
    )

    with patch("ui.presentation.projections.render_chat_first") as mock_fallback:
        render_interaction_shell(ctx, snapshot, None, MagicMock(), MagicMock())
        mock_fallback.assert_called_once_with(snapshot)
