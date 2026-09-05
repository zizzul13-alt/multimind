from pathlib import Path
from unittest.mock import patch

import pytest
import streamlit as st

import app
from database.manager import DatabaseManager
from utils.config import Config, InvalidUserIdError
from utils.identity_state import reset_identity_bound_state


def test_valid_identity_resolves_to_contained_user_database(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "DB_DIR", str(tmp_path / "data"))

    db_path = Path(Config.get_db_path("Alice-01"))
    users_root = (tmp_path / "data" / "users").resolve()

    assert db_path == users_root / "alice-01.db"
    assert db_path.is_relative_to(users_root)


def test_login_identity_trims_harmless_whitespace_before_validation():
    display_username, user_id = Config.resolve_supplied_identity(" Alice ")

    assert display_username == "Alice"
    assert user_id == "alice"


@pytest.mark.parametrize(
    "hostile_id",
    ["..", "../alice", "foo/bar", r"foo\\bar", "/tmp/alice", r"C:\\Users\\alice", r"\\\\server\\share\\alice"],
)
def test_direct_storage_resolver_rejects_path_like_user_ids(hostile_id, tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "DB_DIR", str(tmp_path / "data"))

    with pytest.raises(InvalidUserIdError):
        Config.get_db_path(hostile_id)


def test_invalid_identity_is_not_silently_rewritten(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "DB_DIR", str(tmp_path / "data"))

    with pytest.raises(InvalidUserIdError):
        Config.get_db_path("../alice")

    assert not (tmp_path / "data" / "users" / "alice.db").exists()


def test_trimmed_hostile_path_identity_remains_rejected():
    with pytest.raises(InvalidUserIdError):
        Config.resolve_supplied_identity(" ../alice ")


def test_identity_transition_removes_sensitive_state_and_keeps_presentation_state():
    state = {
        "user": "alice",
        "user_id": "alice",
        "current_session": {"id": "alice-session"},
        "sessions": {"alice-session": {"prompt": "secret"}},
        "memories": {"alice-session": "private memory"},
        "prompt_main": "private draft",
        "last_generated": "private generated result",
        "template_variables": {"client": "Alice secret"},
        "var_client_template": "Alice secret",
        "new_chat_files": ["private-upload"],
        "login_username_input": "alice",
        "active_theme": "midnight",
        "active_navigation": "theme_studio",
        "active_archetype": "command_center",
        "theme_studio_draft": {"color": "#123456"},
    }

    reset_identity_bound_state(state)

    assert state["user"] is None
    assert state["user_id"] is None
    assert state["current_session"] is None
    assert state["sessions"] == {}
    assert state["memories"] == {}
    assert state["prompt_main"] == ""
    assert state["last_generated"] == ""
    assert state["template_variables"] == {}
    assert "var_client_template" not in state
    assert "new_chat_files" not in state
    assert "login_username_input" not in state
    assert state["active_theme"] == "midnight"
    assert state["active_navigation"] == "theme_studio"
    assert state["active_archetype"] == "command_center"
    assert state["theme_studio_draft"] == {"color": "#123456"}


def test_login_transition_from_alice_to_bob_does_not_reuse_alice_runtime_state_or_storage(tmp_path, monkeypatch):
    """Exercise the login boundary, rather than only the reset helper."""
    monkeypatch.setattr(Config, "DB_DIR", str(tmp_path / "data"))
    alice_database = DatabaseManager(Config.get_db_path("alice"))
    alice_database.create_session("alice-session", "Alice private session")

    st.session_state.clear()
    st.session_state.update({
        "user": "Alice",
        "user_id": "alice",
        "current_session": {"id": "alice-session"},
        "sessions": {"alice-session": {"prompt": "Alice secret"}},
        "memories": {"alice-session": "Alice private memory"},
        "prompt_main": "Alice private draft",
        "last_generated": "Alice private result",
        "new_chat_files": ["Alice upload"],
        "active_theme": "midnight",
    })

    try:
        with patch.object(app, "card_container"), \
             patch.object(app.st, "subheader"), \
             patch.object(app.st, "divider"), \
             patch.object(app.st, "text_input", return_value="Bob"), \
             patch.object(app.st, "button", return_value=True), \
             patch.object(app.st, "rerun") as rerun:
            app.show_login_page()

        assert st.session_state.user == "Bob"
        assert st.session_state.user_id == "bob"
        assert st.session_state.current_session is None
        assert st.session_state.sessions == {}
        assert st.session_state.memories == {}
        assert st.session_state.prompt_main == ""
        assert st.session_state.last_generated == ""
        assert "new_chat_files" not in st.session_state
        assert st.session_state.active_theme == "midnight"
        assert DatabaseManager(Config.get_db_path(st.session_state.user_id)).get_sessions() == []
        assert [session["name"] for session in alice_database.get_sessions()] == ["Alice private session"]
        rerun.assert_called_once()
    finally:
        st.session_state.clear()
