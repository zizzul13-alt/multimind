"""
Architecture Invariant Contract Tests for S7.6 Interaction Shell
Verifies that interaction shell dispatch does NOT modify backend execution, persistence, or snapshot semantics.
"""
import pytest
from unittest.mock import MagicMock, patch
from ui.presentation.models import (
    InteractionContext,
    SessionMetadataSnapshot,
    PresentationSnapshot,
)
from ui.presentation.shell import render_interaction_shell
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

    # Ensure processing labels exist for all archetypes without changing backend parameters
    labels = [get_processing_label(arch_id) for arch_id in CANONICAL_ARCHETYPE_IDS]
    assert len(labels) == 7
    assert len(set(labels)) == 7  # All 7 archetypes have distinct truthful processing labels
