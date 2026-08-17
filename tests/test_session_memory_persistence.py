import sqlite3

import pytest

from core.memory import (
    SessionMemory,
    get_or_hydrate_session_memory,
    persist_chat_and_update_memory,
)
from database.manager import DatabaseManager


def _chat(chat_id, prompt, answer):
    return {
        "id": chat_id,
        "prompt": prompt,
        "final_answer": answer,
    }


def _database_with_history(tmp_path, chats):
    db = DatabaseManager(str(tmp_path / "session.db"))
    session_id = "session-1"
    db.create_session(session_id, "Session")
    for chat in chats:
        db.save_chat(session_id, chat)
    return db, session_id


def test_hydrates_memory_from_complete_persisted_history(tmp_path):
    chats = [
        _chat("chat-1", "first prompt", "first answer"),
        _chat("chat-2", "second prompt", "second answer"),
        _chat("chat-3", "third prompt", "third answer"),
        _chat("chat-4", "fourth prompt", "fourth answer"),
    ]
    db, session_id = _database_with_history(tmp_path, chats)

    memory = get_or_hydrate_session_memory({}, db, session_id)

    assert "first prompt" in memory.long_term
    assert "first answer" in memory.long_term
    assert [entry["prompt"] for entry in memory.short_term] == [
        "second prompt",
        "third prompt",
        "fourth prompt",
    ]
    assert [entry["response"] for entry in memory.short_term] == [
        "second answer",
        "third answer",
        "fourth answer",
    ]


def test_fresh_runtime_reopen_reconstructs_equivalent_memory(tmp_path):
    chats = [
        _chat("chat-1", "first prompt", "first answer"),
        _chat("chat-2", "second prompt", "second answer"),
    ]
    db, session_id = _database_with_history(tmp_path, chats)

    original_runtime = {}
    reopened_runtime = {}
    original = get_or_hydrate_session_memory(original_runtime, db, session_id)
    reopened = get_or_hydrate_session_memory(reopened_runtime, db, session_id)

    assert original is not reopened
    assert reopened.get_context() == original.get_context()


def test_memory_hydration_replays_same_second_in_insertion_order(tmp_path):
    chats = [
        _chat("chat-1", "inserted first", "answer one"),
        _chat("chat-2", "inserted second", "answer two"),
        _chat("chat-3", "inserted third", "answer three"),
    ]
    db, session_id = _database_with_history(tmp_path, chats)
    forced_timestamp = "2026-01-01 00:00:00"
    conn = sqlite3.connect(db.db_path)
    conn.execute(
        "UPDATE chats SET created_at = ? WHERE session_id = ?",
        (forced_timestamp, session_id),
    )
    conn.commit()
    conn.close()

    persisted = db.get_session_chats_for_memory(session_id)
    memory = get_or_hydrate_session_memory({}, db, session_id)

    assert {chat["created_at"] for chat in persisted} == {forced_timestamp}
    assert [chat["prompt"] for chat in persisted] == [
        "inserted first",
        "inserted second",
        "inserted third",
    ]
    assert [entry["prompt"] for entry in memory.short_term] == [
        "inserted first",
        "inserted second",
        "inserted third",
    ]


def test_hydrating_empty_session_creates_empty_memory(tmp_path):
    db, session_id = _database_with_history(tmp_path, [])

    memory = get_or_hydrate_session_memory({}, db, session_id)

    assert memory.short_term == []
    assert memory.long_term == ""
    assert memory.decisions == []


def test_existing_runtime_memory_is_not_hydrated_twice():
    class CountingDatabase:
        def __init__(self):
            self.calls = 0

        def get_session_chats_for_memory(self, session_id):
            self.calls += 1
            return [_chat("chat-1", "prompt", "answer")]

    db = CountingDatabase()
    memories = {}

    first = get_or_hydrate_session_memory(memories, db, "session-1")
    second = get_or_hydrate_session_memory(memories, db, "session-1")

    assert first is second
    assert db.calls == 1
    assert len(first.short_term) == 1


def test_database_save_failure_does_not_contaminate_runtime_memory():
    class FailingDatabase:
        def save_chat(self, session_id, chat_data):
            raise sqlite3.Error("write failed")

    existing_memory = SessionMemory()
    existing_memory.add_chat("saved prompt", "saved answer")
    memories = {"session-1": existing_memory}

    with pytest.raises(sqlite3.Error, match="write failed"):
        persist_chat_and_update_memory(
            FailingDatabase(),
            "session-1",
            memories,
            _chat("chat-2", "unsaved prompt", "unsaved answer"),
        )

    assert memories["session-1"] is existing_memory
    assert [entry["prompt"] for entry in existing_memory.short_term] == ["saved prompt"]


def test_false_database_save_does_not_contaminate_runtime_memory():
    class UnsuccessfulDatabase:
        def save_chat(self, session_id, chat_data):
            return False

    existing_memory = SessionMemory()
    existing_memory.add_chat("saved prompt", "saved answer")
    memories = {"session-1": existing_memory}

    saved = persist_chat_and_update_memory(
        UnsuccessfulDatabase(),
        "session-1",
        memories,
        _chat("chat-2", "unsaved prompt", "unsaved answer"),
    )

    assert saved is False
    assert memories["session-1"] is existing_memory
    assert [entry["prompt"] for entry in existing_memory.short_term] == ["saved prompt"]
