from pathlib import Path

import pytest

from utils.config import Config, InvalidUserIdError
from utils.identity_state import reset_identity_bound_state


def test_valid_identity_resolves_to_contained_user_database(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "DB_DIR", str(tmp_path / "data"))

    db_path = Path(Config.get_db_path("Alice-01"))
    users_root = (tmp_path / "data" / "users").resolve()

    assert db_path == users_root / "alice-01.db"
    assert db_path.is_relative_to(users_root)


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
