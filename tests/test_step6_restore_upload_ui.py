"""Regression contracts for the real Step-6 restore-upload residual."""

import inspect

from multimind_reflex.multimind_reflex import RESTORE_ACCEPT, RESTORE_ID, _data_ops


def test_restore_upload_component_builds_with_current_reflex():
    """The repair must remain valid for the Reflex version pinned by the repo."""
    component = _data_ops()
    assert component is not None


def test_restore_picker_exposes_selection_before_staging():
    """A selected backup must be visible before the separate staging action."""
    source = inspect.getsource(_data_ops)
    assert "rx.selected_files(RESTORE_ID)" in source
    assert "max_files=1" in source
    assert "Stage selected backup" in source
    assert "rx.upload_files(upload_id=RESTORE_ID)" in source


def test_restore_picker_advertises_portable_sqlite_extensions():
    accepted_extensions = {
        extension
        for extensions in RESTORE_ACCEPT.values()
        for extension in extensions
    }
    assert RESTORE_ID == "rj3_restore"
    assert {".db", ".sqlite", ".sqlite3"}.issubset(accepted_extensions)
