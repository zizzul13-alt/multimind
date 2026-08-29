import sqlite3

import pytest

from database.manager import (
    DatabaseManager,
    RestoreValidationError,
    validate_restore_candidate,
)


def _database_bytes(path):
    return path.read_bytes()


def _make_valid_backup(path, session_name="Restored session"):
    backup = DatabaseManager(str(path))
    backup.create_session("backup-session", session_name)
    backup.save_chat("backup-session", {
        "id": "backup-chat",
        "prompt": "backup prompt",
        "final_answer": "backup answer",
    })
    return _database_bytes(path)


def _active_database(path):
    active = DatabaseManager(str(path))
    active.create_session("active-session", "Active data")
    return active


def _active_session_names(manager):
    return [session["name"] for session in manager.get_sessions()]


def test_valid_multimind_backup_is_eligible_and_restores(tmp_path):
    active = _active_database(tmp_path / "active.db")
    backup_bytes = _make_valid_backup(tmp_path / "valid-backup.db")

    assert active.restore_from_bytes(backup_bytes) is True
    assert _active_session_names(active) == ["Restored session"]


@pytest.mark.parametrize("invalid_bytes", [b"not a sqlite database", b""])
def test_non_sqlite_or_empty_backup_is_rejected_without_mutating_active_database(tmp_path, invalid_bytes):
    active = _active_database(tmp_path / "active.db")

    with pytest.raises(RestoreValidationError):
        active.restore_from_bytes(invalid_bytes)

    assert _active_session_names(active) == ["Active data"]


def test_truncated_sqlite_backup_is_rejected_without_mutating_active_database(tmp_path):
    active = _active_database(tmp_path / "active.db")
    valid_backup = _make_valid_backup(tmp_path / "valid-backup.db")

    with pytest.raises(RestoreValidationError):
        active.restore_from_bytes(valid_backup[:100])

    assert _active_session_names(active) == ["Active data"]


def test_unrelated_sqlite_schema_is_rejected_without_mutating_active_database(tmp_path):
    active = _active_database(tmp_path / "active.db")
    unrelated_path = tmp_path / "unrelated.db"
    conn = sqlite3.connect(unrelated_path)
    conn.execute("CREATE TABLE unrelated (id TEXT)")
    conn.commit()
    conn.close()

    with pytest.raises(RestoreValidationError):
        active.restore_from_bytes(_database_bytes(unrelated_path))

    assert _active_session_names(active) == ["Active data"]


def test_partial_multimind_schema_is_rejected(tmp_path):
    active = _active_database(tmp_path / "active.db")
    partial_path = tmp_path / "partial.db"
    conn = sqlite3.connect(partial_path)
    conn.execute("CREATE TABLE sessions (id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

    with pytest.raises(RestoreValidationError):
        active.restore_from_bytes(_database_bytes(partial_path))

    assert _active_session_names(active) == ["Active data"]


def test_expected_tables_with_missing_required_columns_are_rejected(tmp_path):
    active = _active_database(tmp_path / "active.db")
    incompatible_path = tmp_path / "incompatible.db"
    conn = sqlite3.connect(incompatible_path)
    conn.execute("CREATE TABLE sessions (id TEXT PRIMARY KEY, name TEXT)")
    conn.execute("CREATE TABLE chats (id TEXT PRIMARY KEY, session_id TEXT)")
    conn.commit()
    conn.close()

    with pytest.raises(RestoreValidationError):
        active.restore_from_bytes(_database_bytes(incompatible_path))

    assert _active_session_names(active) == ["Active data"]


def test_direct_validation_enforces_the_same_rules_without_streamlit(tmp_path):
    valid_path = tmp_path / "valid.db"
    _make_valid_backup(valid_path)
    validate_restore_candidate(valid_path)

    invalid_path = tmp_path / "invalid.db"
    invalid_path.write_bytes(b"hostile bytes")
    with pytest.raises(RestoreValidationError):
        validate_restore_candidate(invalid_path)
