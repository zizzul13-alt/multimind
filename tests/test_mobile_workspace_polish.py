from pathlib import Path

import rxconfig
from multimind_reflex import mobile_entry
from multimind_reflex import multimind_reflex as surface


ROOT = Path(__file__).resolve().parents[1]
ENTRY = (ROOT / "multimind_reflex" / "mobile_entry.py").read_text(encoding="utf-8")


def test_reflex_uses_mobile_polish_entry_without_replacing_app_instance():
    assert rxconfig.config.app_module_import == "multimind_reflex.mobile_entry"
    assert mobile_entry.app is surface.app


def test_mobile_polish_keeps_touch_targets_and_text_inputs_phone_safe():
    style = mobile_entry.app.style
    assert style["button"]["min_height"] == "2.75rem"
    assert style["input"]["font_size"] == "1rem"
    assert style["textarea"]["font_size"] == "1rem"
    assert style["select"]["font_size"] == "1rem"
    assert style["body"]["overflow_x"] == "hidden"
    assert style["p"]["overflow_wrap"] == "anywhere"
    assert "@media (max-width: 48em)" in style


def test_mobile_polish_is_presentation_only():
    for forbidden in (
        "MultiMindApplication",
        "DebateOrchestrator",
        "sqlite3",
        "build_host_application",
        "execute_chat",
        "restore_database",
        "requests.post(",
        "httpx.post(",
    ):
        assert forbidden not in ENTRY


def test_existing_workspace_and_theme_studio_remain_owners():
    assert "from multimind_reflex.multimind_reflex import app" in ENTRY
    source = (ROOT / "multimind_reflex" / "multimind_reflex.py").read_text(encoding="utf-8")
    assert "def _workspace()" in source
    assert "def _theme_studio()" in source
    assert "WorkspaceDnaState as HostState" in source
