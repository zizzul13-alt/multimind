import json
import sqlite3

from core.application import MultiMindApplication
from database.manager import DatabaseManager
from database.turso_manager import TursoDatabaseManager
from multimind_reflex.deliberation_projection import history_snapshots, run_summary


def debate_payload(system="participant-1-a"):
    return {
        "status": "success",
        "system_verdict": system,
        "participants": [
            {
                "participant_id": "participant-1-a",
                "requested_provider": "a",
                "actual_provider": "a-model",
                "status": "success",
                "text": "A answer",
            },
            {
                "participant_id": "participant-2-b",
                "requested_provider": "b",
                "actual_provider": "b-model",
                "status": "success",
                "text": "B answer",
            },
            {
                "participant_id": "participant-3-c",
                "requested_provider": "c",
                "actual_provider": "c-model",
                "status": "error",
                "text": "",
            },
        ],
        "judge": {"status": "success", "actual_provider": "a-model"},
    }


def seed_chat(db, session="s1", chat="c1", payload=None):
    db.create_session(session, "Session")
    db.save_chat(
        session,
        {
            "id": chat,
            "prompt": "Choose the better answer",
            "final_answer": "Synthesized answer",
            "debate_data": json.dumps(payload or debate_payload()),
        },
    )


def test_system_and_user_verdict_are_independent_and_reloadable(tmp_path):
    path = str(tmp_path / "user.db")
    db = DatabaseManager(path)
    seed_chat(db)
    app = MultiMindApplication(db=db)

    result = app.set_user_verdict("s1", "c1", "participant-2-b")
    assert result.status == "success"
    assert result.system_verdict == "participant-1-a"
    assert result.user_verdict == "participant-2-b"

    rebuilt = MultiMindApplication(db=DatabaseManager(path))
    persisted = json.loads(rebuilt.get_session_chats("s1")[0]["debate_data"])
    assert persisted["system_verdict"] == "participant-1-a"
    assert persisted["user_verdict"] == "participant-2-b"


def test_user_can_replace_and_clear_verdict_without_mutating_system_verdict(tmp_path):
    db = DatabaseManager(str(tmp_path / "user.db"))
    seed_chat(db)
    app = MultiMindApplication(db=db)

    assert app.set_user_verdict("s1", "c1", "participant-2-b").status == "success"
    replaced = app.set_user_verdict("s1", "c1", "participant-1-a")
    assert replaced.user_verdict == "participant-1-a"
    cleared = app.set_user_verdict("s1", "c1", "")
    assert cleared.status == "success"
    assert cleared.user_verdict == ""

    payload = json.loads(db.get_chat("s1", "c1")["debate_data"])
    assert payload["system_verdict"] == "participant-1-a"
    assert "user_verdict" not in payload


def test_failed_unknown_or_wrong_session_participant_fails_closed(tmp_path):
    db = DatabaseManager(str(tmp_path / "user.db"))
    seed_chat(db)
    app = MultiMindApplication(db=db)
    original = db.get_chat("s1", "c1")["debate_data"]

    failed = app.set_user_verdict("s1", "c1", "participant-3-c")
    unknown = app.set_user_verdict("s1", "c1", "participant-99-x")
    foreign_session = app.set_user_verdict("different-session", "c1", "participant-1-a")

    assert failed.status == "invalid_participant"
    assert unknown.status == "invalid_participant"
    assert foreign_session.status == "chat_not_found"
    assert db.get_chat("s1", "c1")["debate_data"] == original


def test_malformed_debate_data_is_not_overwritten(tmp_path):
    db = DatabaseManager(str(tmp_path / "user.db"))
    db.create_session("s1", "Session")
    db.save_chat(
        "s1",
        {"id": "c1", "prompt": "bad", "final_answer": "x", "debate_data": "not-json"},
    )
    app = MultiMindApplication(db=db)
    result = app.set_user_verdict("s1", "c1", "participant-1-a")
    assert result.status == "invalid_debate_data"
    assert db.get_chat("s1", "c1")["debate_data"] == "not-json"


def test_backup_restore_preserves_user_verdict_without_schema_migration(tmp_path):
    source = DatabaseManager(str(tmp_path / "source.db"))
    seed_chat(source)
    app = MultiMindApplication(db=source)
    assert app.set_user_verdict("s1", "c1", "participant-2-b").status == "success"

    backup = source.export_bytes()
    restored = DatabaseManager(str(tmp_path / "restored.db"))
    restored.restore_from_bytes(backup)
    payload = json.loads(restored.get_chat("s1", "c1")["debate_data"])
    assert payload["system_verdict"] == "participant-1-a"
    assert payload["user_verdict"] == "participant-2-b"


def sqlite_remote_factory(path):
    def factory(_url, _token):
        return sqlite3.connect(path)
    return factory


def test_turso_user_scope_prevents_cross_user_verdict_mutation(tmp_path):
    remote = str(tmp_path / "remote.db")
    factory = sqlite_remote_factory(remote)
    alice = TursoDatabaseManager("libsql://example.invalid", "token", "alice", factory)
    bob = TursoDatabaseManager("libsql://example.invalid", "token", "bob", factory)

    seed_chat(alice, payload=debate_payload())
    seed_chat(bob, payload=debate_payload(system="participant-2-b"))

    result = MultiMindApplication(db=alice).set_user_verdict(
        "s1", "c1", "participant-2-b"
    )
    assert result.status == "success"

    alice_payload = json.loads(alice.get_chat("s1", "c1")["debate_data"])
    bob_payload = json.loads(bob.get_chat("s1", "c1")["debate_data"])
    assert alice_payload["user_verdict"] == "participant-2-b"
    assert bob_payload["system_verdict"] == "participant-2-b"
    assert "user_verdict" not in bob_payload


def test_projection_keeps_system_and_user_verdict_separate():
    payload = debate_payload()
    payload["user_verdict"] = "participant-2-b"
    summary = run_summary(payload)
    assert summary["system_verdict"] == "participant-1-a"
    assert summary["user_verdict"] == "participant-2-b"

    rows = [{
        "id": "c1",
        "prompt": "p",
        "final_answer": "f",
        "debate_data": json.dumps(payload),
    }]
    snapshot = history_snapshots(rows)[0]
    assert snapshot["system_verdict"] == "participant-1-a"
    assert snapshot["user_verdict"] == "participant-2-b"
