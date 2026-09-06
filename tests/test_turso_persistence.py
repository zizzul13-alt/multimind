import sqlite3

import pytest

from core.composition import build_database_for_user
from database.manager import DatabaseManager, validate_restore_candidate
from database.turso_manager import TursoDatabaseManager


def sqlite_remote_factory(path):
    def connect(_database_url, _auth_token):
        return sqlite3.connect(path)
    return connect


def build_remote(tmp_path, user_id):
    remote_path = str(tmp_path / "remote.db")
    return TursoDatabaseManager(
        "libsql://example.invalid",
        "test-token",
        user_id,
        connection_factory=sqlite_remote_factory(remote_path),
    )


def test_turso_adapter_scopes_sessions_and_chats_per_user(tmp_path):
    alice = build_remote(tmp_path, "alice")
    bob = build_remote(tmp_path, "bob")

    alice.create_session("shared-id", "alice-session")
    bob.create_session("shared-id", "bob-session")
    alice.save_chat("shared-id", {
        "id": "chat-1", "prompt": "alice prompt", "final_answer": "alice answer"
    })
    bob.save_chat("shared-id", {
        "id": "chat-1", "prompt": "bob prompt", "final_answer": "bob answer"
    })

    assert [row["name"] for row in alice.get_sessions()] == ["alice-session"]
    assert [row["name"] for row in bob.get_sessions()] == ["bob-session"]
    assert alice.get_session_chats_for_memory("shared-id")[0]["prompt"] == "alice prompt"
    assert bob.get_session_chats_for_memory("shared-id")[0]["prompt"] == "bob prompt"


def test_turso_export_remains_valid_portable_sqlite_backup(tmp_path):
    manager = build_remote(tmp_path, "alice")
    manager.create_session("s1", "portable")
    manager.save_chat("s1", {
        "id": "c1", "prompt": "hello", "final_answer": "world",
        "tokens_used": 3, "cost": 0.1,
    })

    backup = manager.export_bytes()
    backup_path = tmp_path / "export.db"
    backup_path.write_bytes(backup)
    validate_restore_candidate(backup_path)

    local = DatabaseManager(str(tmp_path / "local.db"))
    local.restore_from_bytes(backup)
    assert local.get_sessions()[0]["name"] == "portable"
    assert local.get_session_chats("s1")[0]["final_answer"] == "world"


def test_turso_restore_replaces_only_active_user_scope(tmp_path):
    alice = build_remote(tmp_path, "alice")
    bob = build_remote(tmp_path, "bob")
    alice.create_session("old", "old-alice")
    bob.create_session("keep", "keep-bob")

    source = DatabaseManager(str(tmp_path / "source.db"))
    source.create_session("new", "new-alice")
    source.save_chat("new", {
        "id": "new-chat", "prompt": "restored", "final_answer": "yes"
    })

    alice.restore_from_bytes(source.export_bytes())

    assert [row["name"] for row in alice.get_sessions()] == ["new-alice"]
    assert alice.get_session_chats("new")[0]["prompt"] == "restored"
    assert [row["name"] for row in bob.get_sessions()] == ["keep-bob"]


def test_composition_uses_sqlite_without_turso_credentials(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "core.composition.Config.get_db_path", lambda _user_id: str(tmp_path / "fallback.db")
    )
    db = build_database_for_user("alice", environ={})
    assert isinstance(db, DatabaseManager)


def test_composition_selects_turso_only_when_both_credentials_are_present():
    calls = []

    class FakeTurso:
        def __init__(self, url, token, user_id):
            calls.append((url, token, user_id))

    db = build_database_for_user(
        "alice",
        environ={"TURSO_DATABASE_URL": "libsql://db", "TURSO_AUTH_TOKEN": "secret"},
        turso_factory=FakeTurso,
    )
    assert isinstance(db, FakeTurso)
    assert calls == [("libsql://db", "secret", "alice")]


@pytest.mark.parametrize(
    "environ",
    [
        {"TURSO_DATABASE_URL": "libsql://db"},
        {"TURSO_AUTH_TOKEN": "secret"},
    ],
)
def test_composition_fails_closed_on_partial_turso_credentials(environ):
    with pytest.raises(RuntimeError, match="configured together"):
        build_database_for_user("alice", environ=environ)
