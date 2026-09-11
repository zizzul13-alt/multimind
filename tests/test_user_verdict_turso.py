import json
import sqlite3

from core.application import MultiMindApplication
from database.turso_manager import TursoDatabaseManager


def _factory(path):
    def connect(_database_url, _auth_token):
        return sqlite3.connect(path)
    return connect


def _manager(path, user_id):
    return TursoDatabaseManager(
        "libsql://example.invalid",
        "test-token",
        user_id,
        connection_factory=_factory(path),
    )


def _seed(manager, system_verdict):
    manager.create_session("shared-session", f"session-{manager.user_id}")
    manager.save_chat(
        "shared-session",
        {
            "id": "shared-chat",
            "prompt": "q",
            "final_answer": "a",
            "debate_data": json.dumps(
                {
                    "participants": [
                        {
                            "participant_id": "participant-1-gemini",
                            "status": "success",
                            "requested_provider": "gemini",
                            "actual_provider": "gemini-model",
                            "model": "gemini-model",
                            "role": "Researcher",
                        },
                        {
                            "participant_id": "participant-2-groq",
                            "status": "success",
                            "requested_provider": "groq",
                            "actual_provider": "groq-model",
                            "model": "groq-model",
                            "role": "Fact checker",
                        },
                    ],
                    "system_verdict": system_verdict,
                }
            ),
        },
    )


def test_turso_user_verdict_update_never_crosses_user_scope(tmp_path):
    remote = str(tmp_path / "remote.db")
    alice = _manager(remote, "alice")
    bob = _manager(remote, "bob")
    _seed(alice, "participant-1-gemini")
    _seed(bob, "participant-2-groq")

    result = MultiMindApplication(db=alice).record_user_verdict(
        "shared-session", "shared-chat", "participant-2-groq"
    )
    assert result.status == "success"

    alice_data = json.loads(alice.get_chat("shared-session", "shared-chat")["debate_data"])
    bob_data = json.loads(bob.get_chat("shared-session", "shared-chat")["debate_data"])

    assert alice_data["system_verdict"] == "participant-1-gemini"
    assert alice_data["user_verdict"]["participant_id"] == "participant-2-groq"
    assert bob_data["system_verdict"] == "participant-2-groq"
    assert "user_verdict" not in bob_data


def test_turso_user_verdict_cross_session_lookup_fails_closed(tmp_path):
    remote = str(tmp_path / "remote.db")
    alice = _manager(remote, "alice")
    _seed(alice, "participant-1-gemini")

    result = MultiMindApplication(db=alice).record_user_verdict(
        "wrong-session", "shared-chat", "participant-1-gemini"
    )
    assert result.status == "not_found"
    stored = json.loads(alice.get_chat("shared-session", "shared-chat")["debate_data"])
    assert "user_verdict" not in stored
