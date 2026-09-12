from pathlib import Path

import rxconfig
from multimind_reflex import mobile_entry
from multimind_reflex import multimind_reflex as surface
from multimind_reflex import verdict_entry
from multimind_reflex.identity_state import IdentityVerdictHostState
from multimind_reflex.verdict_state import VerdictHostState


ROOT = Path(__file__).resolve().parents[1]
VERDICT_STATE = (ROOT / "multimind_reflex" / "verdict_state.py").read_text(encoding="utf-8")
VERDICT_ENTRY = (ROOT / "multimind_reflex" / "verdict_entry.py").read_text(encoding="utf-8")


def test_accepted_mobile_entry_keeps_single_app_and_installs_verdict_state():
    assert rxconfig.config.app_module_import == "multimind_reflex.mobile_entry"
    assert mobile_entry.app is surface.app
    assert verdict_entry.app is surface.app
    assert surface.HostState is IdentityVerdictHostState
    assert issubclass(IdentityVerdictHostState, VerdictHostState)
    assert surface._participant_card is verdict_entry._participant_card
    assert surface._history_panel is verdict_entry._history_panel


def test_verdict_target_is_exact_chat_result_not_inferred_history_latest():
    assert "self.current_chat_id = result.chat_id" in VERDICT_STATE
    assert "result.persisted" in VERDICT_STATE
    assert "self.current_session_id,\n            self.current_chat_id" in VERDICT_STATE
    assert "history[-1]" not in VERDICT_STATE
    assert "latest persisted chat" not in VERDICT_STATE


def test_reflex_wiring_exposes_only_successful_participant_actions_and_separate_history_truth():
    assert 'participant["status"] == "success"' in VERDICT_ENTRY
    assert '"My winner"' in VERDICT_ENTRY
    assert '"Clear my winner"' in VERDICT_ENTRY
    assert 'row["system_verdict"]' in VERDICT_ENTRY
    assert 'row["user_verdict"]' in VERDICT_ENTRY
    assert "set_current_user_verdict" in VERDICT_ENTRY


def test_identity_first_surface_keeps_provider_route_secondary():
    assert '"AI participants"' in VERDICT_ENTRY
    assert '"Requested AI: "' in VERDICT_ENTRY
    assert '"Effective AI: "' in VERDICT_ENTRY
    assert '"Route: "' in VERDICT_ENTRY
    assert "AI_IDENTITY_OPTIONS" in VERDICT_ENTRY
    assert "OpenRouter" not in VERDICT_ENTRY
    assert "Cloudflare" not in VERDICT_ENTRY


def test_verdict_presentation_does_not_create_second_app_or_route_business_logic():
    assert "rx.App(" not in VERDICT_ENTRY
    for forbidden in (
        "sqlite3.connect(",
        "DebateOrchestrator",
        "requests.post(",
        "httpx.post(",
        "FastAPI",
    ):
        assert forbidden not in VERDICT_ENTRY
