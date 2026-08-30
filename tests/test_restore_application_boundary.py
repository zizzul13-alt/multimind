"""Restore lifecycle coverage for the plain-Python application boundary."""
from pathlib import Path

from core.application import ApplicationRuntime, MultiMindApplication
from database.manager import RestoreOperationError, RestoreValidationError


class RecordingRestoreDatabase:
    def __init__(self, outcome=None):
        self.outcome = outcome
        self.backups = []

    def restore_from_bytes(self, backup_bytes):
        self.backups.append(backup_bytes)
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return True


def _runtime():
    return ApplicationRuntime(
        current_session={"id": "old-session"},
        memories={"old-session": "hydrated memory"},
    )


def test_plain_python_restore_success_invalidates_database_derived_runtime():
    database = RecordingRestoreDatabase()
    runtime = _runtime()

    result = MultiMindApplication(db=database, runtime=runtime).restore_database(b"backup")

    assert result.status == "success"
    assert result.runtime_invalidated is True
    assert database.backups == [b"backup"]
    assert runtime.current_session is None
    assert runtime.memories == {}


def test_s2_validation_failure_does_not_invalidate_runtime():
    database = RecordingRestoreDatabase(RestoreValidationError("invalid"))
    runtime = _runtime()

    result = MultiMindApplication(db=database, runtime=runtime).restore_database(b"invalid")

    assert result.status == "invalid_backup"
    assert result.runtime_invalidated is False
    assert runtime.current_session == {"id": "old-session"}
    assert runtime.memories == {"old-session": "hydrated memory"}


def test_post_replacement_verification_failure_invalidates_stale_runtime():
    database = RecordingRestoreDatabase(
        RestoreOperationError("verification failed", database_replaced=True)
    )
    runtime = _runtime()

    result = MultiMindApplication(db=database, runtime=runtime).restore_database(b"backup")

    assert result.status == "operation_failed"
    assert result.runtime_invalidated is True
    assert runtime.current_session is None
    assert runtime.memories == {}


def test_pre_activation_operation_failure_does_not_invalidate_runtime():
    database = RecordingRestoreDatabase(RestoreOperationError("staging failed"))
    runtime = _runtime()

    result = MultiMindApplication(db=database, runtime=runtime).restore_database(b"backup")

    assert result.status == "operation_failed"
    assert result.runtime_invalidated is False
    assert runtime.current_session == {"id": "old-session"}


def test_streamlit_host_delegates_restore_lifecycle_to_application_boundary():
    source = Path("app.py").read_text(encoding="utf-8")

    assert "def invalidate_restored_database_state" not in source
    assert "db.restore_from_bytes" not in source
    assert ".restore_database(uploaded_db.getvalue())" in source
