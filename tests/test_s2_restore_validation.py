import sqlite3

import pytest
import database.manager as manager_module

from database.manager import (
    DatabaseManager,
    RestoreOperationError,
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


def test_oversized_backup_is_rejected_before_temporary_write_or_active_mutation(tmp_path, monkeypatch):
    active = _active_database(tmp_path / "active.db")
    monkeypatch.setattr(manager_module, "MAX_RESTORE_CANDIDATE_BYTES", 4)

    def fail_if_temporary_candidate_is_created(*args, **kwargs):
        raise AssertionError("oversized backup must not create a candidate file")

    monkeypatch.setattr(manager_module.tempfile, "mkstemp", fail_if_temporary_candidate_is_created)

    with pytest.raises(RestoreValidationError):
        active.restore_from_bytes(b"12345")

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


def test_restore_stages_candidate_in_the_active_database_directory(tmp_path, monkeypatch):
    active_path = tmp_path / "active.db"
    active = _active_database(active_path)
    backup_bytes = _make_valid_backup(tmp_path / "valid-backup.db")
    original_mkstemp = manager_module.tempfile.mkstemp
    observed = {}

    def observe_mkstemp(*args, **kwargs):
        observed.update(kwargs)
        return original_mkstemp(*args, **kwargs)

    monkeypatch.setattr(manager_module.tempfile, "mkstemp", observe_mkstemp)

    assert active.restore_from_bytes(backup_bytes) is True
    assert observed["dir"] == str(tmp_path)
    assert _active_session_names(active) == ["Restored session"]


def test_s2_rejection_never_reaches_activation(tmp_path, monkeypatch):
    active = _active_database(tmp_path / "active.db")

    def fail_if_replaced(*_args, **_kwargs):
        raise AssertionError("S2-rejected candidate must not reach activation")

    monkeypatch.setattr(manager_module.os, "replace", fail_if_replaced)

    with pytest.raises(RestoreValidationError):
        active.restore_from_bytes(b"not a sqlite database")

    assert _active_session_names(active) == ["Active data"]


def test_staging_write_failure_leaves_active_database_unchanged(tmp_path, monkeypatch):
    active = _active_database(tmp_path / "active.db")
    backup_bytes = _make_valid_backup(tmp_path / "valid-backup.db")

    class FailingWriter:
        def __init__(self, descriptor):
            self.descriptor = descriptor

        def __enter__(self):
            return self

        def __exit__(self, *args):
            manager_module.os.close(self.descriptor)

        def write(self, _data):
            raise OSError("simulated staging write failure")

    monkeypatch.setattr(
        manager_module.os,
        "fdopen",
        lambda descriptor, _mode: FailingWriter(descriptor),
    )

    with pytest.raises(RestoreOperationError, match="staging"):
        active.restore_from_bytes(backup_bytes)

    assert _active_session_names(active) == ["Active data"]


def test_short_staging_write_never_reaches_activation(tmp_path, monkeypatch):
    active = _active_database(tmp_path / "active.db")
    backup_bytes = _make_valid_backup(tmp_path / "valid-backup.db")
    replace_called = False

    class ShortWriter:
        def __init__(self, descriptor):
            self.descriptor = descriptor

        def __enter__(self):
            return self

        def __exit__(self, *args):
            manager_module.os.close(self.descriptor)

        def write(self, data):
            return len(data) - 1

    def fail_if_replaced(*_args, **_kwargs):
        nonlocal replace_called
        replace_called = True
        raise AssertionError("short staging write must not activate")

    monkeypatch.setattr(manager_module.os, "fdopen", lambda fd, _mode: ShortWriter(fd))
    monkeypatch.setattr(manager_module.os, "replace", fail_if_replaced)

    with pytest.raises(RestoreOperationError, match="incomplete"):
        active.restore_from_bytes(backup_bytes)

    assert replace_called is False
    assert _active_session_names(active) == ["Active data"]


def test_activation_failure_leaves_active_database_valid_without_direct_overwrite(tmp_path, monkeypatch):
    active = _active_database(tmp_path / "active.db")
    backup_bytes = _make_valid_backup(tmp_path / "valid-backup.db")

    def fail_replace(*_args, **_kwargs):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(manager_module.os, "replace", fail_replace)

    with pytest.raises(RestoreOperationError, match="replacement failed"):
        active.restore_from_bytes(backup_bytes)

    validate_restore_candidate(active.db_path)
    assert _active_session_names(active) == ["Active data"]


def test_successful_replacement_is_reopened_and_validated(tmp_path):
    active = _active_database(tmp_path / "active.db")
    backup_bytes = _make_valid_backup(tmp_path / "valid-backup.db")

    assert active.restore_from_bytes(backup_bytes) is True
    validate_restore_candidate(active.db_path)
    assert _active_session_names(active) == ["Restored session"]


def test_post_replace_verification_failure_is_controlled_without_rollback(tmp_path, monkeypatch):
    active = _active_database(tmp_path / "active.db")
    backup_bytes = _make_valid_backup(tmp_path / "valid-backup.db")
    original_validate = manager_module.validate_restore_candidate

    def fail_only_for_active(path):
        if path == active.db_path:
            raise RestoreValidationError("simulated verification failure")
        return original_validate(path)

    monkeypatch.setattr(manager_module, "validate_restore_candidate", fail_only_for_active)

    with pytest.raises(RestoreOperationError, match="could not be verified") as exc_info:
        active.restore_from_bytes(backup_bytes)

    assert exc_info.value.database_replaced is True
    assert _active_session_names(active) == ["Restored session"]


def test_cleanup_failure_does_not_mask_activation_failure_or_damage_active_database(tmp_path, monkeypatch):
    active = _active_database(tmp_path / "active.db")
    backup_bytes = _make_valid_backup(tmp_path / "valid-backup.db")
    cleanup_called = False

    def fail_replace(*_args, **_kwargs):
        raise OSError("simulated replace failure")

    def fail_cleanup(*_args, **_kwargs):
        nonlocal cleanup_called
        cleanup_called = True
        raise OSError("simulated cleanup failure")

    monkeypatch.setattr(manager_module.os, "replace", fail_replace)
    monkeypatch.setattr(manager_module.os, "remove", fail_cleanup)

    with pytest.raises(RestoreOperationError, match="replacement failed"):
        active.restore_from_bytes(backup_bytes)

    assert cleanup_called is True
    validate_restore_candidate(active.db_path)
    assert _active_session_names(active) == ["Active data"]
