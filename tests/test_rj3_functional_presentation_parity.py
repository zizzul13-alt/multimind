from pathlib import Path

from multimind_reflex.state import ARCHETYPES, TEMPLATE_OPTIONS
from core.templates import TemplateManager


ROOT = Path(__file__).resolve().parents[1]
STATE = (ROOT / "multimind_reflex" / "state.py").read_text(encoding="utf-8")
SURFACE = (ROOT / "multimind_reflex" / "multimind_reflex.py").read_text(encoding="utf-8")


def test_all_seven_locked_archetypes_are_exposed():
    assert ARCHETYPES == [
        "chat_first",
        "command_center",
        "ai_workspace",
        "ai_research_lab",
        "agent_canvas",
        "terminal_hacker",
        "minimal_saas",
    ]


def test_locked_preworkspace_theme_handoff_and_studio_reentry_exist():
    for token in (
        'current_surface: str = "theme"',
        "def apply_theme",
        'self.current_surface = "workspace"',
        "def open_theme_studio",
        "def discard_theme",
        "def reset_theme",
    ):
        assert token in STATE
    assert 'rx.button("Theme Studio"' in SURFACE
    assert 'rx.button("Apply Composition"' in SURFACE


def test_theme_draft_is_host_owned_and_private_dna_is_optional():
    assert "from ui.dna_bridge import" in STATE
    assert "dna_available" in STATE
    assert "theme_studio_available" in STATE
    assert "design_dna" not in STATE
    assert "dna_quarantine" not in STATE
    assert "database.manager" not in STATE


def test_composer_parity_controls_are_present():
    for token in (
        "selected_template",
        "template_description",
        "template_variables",
        "template_preview",
        "context_mode",
        "compressor_enabled",
        "active_agents",
        "debate_rounds",
        "selected_skill",
    ):
        assert token in STATE
    for label in (
        "Prompt template",
        "Use preview as editable prompt",
        "Compressor",
        "Agents",
        "Rounds",
        "Skill",
    ):
        assert label in SURFACE


def test_default_templates_are_exposed_without_reimplementing_template_truth():
    manager = TemplateManager()
    expected = [item[0] for item in manager.get_template_names()]
    assert TEMPLATE_OPTIONS[0] == ""
    assert TEMPLATE_OPTIONS[1:] == expected


def test_presend_usage_feedback_uses_existing_token_counter_contract():
    assert "TokenCounter.estimate_total" in STATE
    assert "TokenCounter.get_warning_level" in STATE
    assert "TokenCounter.estimate_cost" in STATE
    for token in (
        "estimated_prompt_tokens",
        "estimated_file_tokens",
        "estimated_total_tokens",
        "estimated_cost",
        "token_warning_level",
    ):
        assert token in STATE


def test_persisted_result_lifecycle_and_data_operations_use_application_boundary():
    assert "application.execute_chat" in STATE
    assert "application.get_session_chats" in STATE
    assert "self._application().export_database()" in STATE
    assert "self._application().restore_database" in STATE
    assert "Config.get_db_path" not in STATE
    assert "sqlite3" not in STATE


def test_busy_duplicate_guard_and_session_switch_guard_remain_present():
    assert "if self.busy:" in STATE
    assert "Finish the active run before switching sessions." in STATE
    assert "@rx.event(background=True)" in STATE


def test_surface_keeps_phone_tablet_desktop_breakpoints():
    assert 'rx.breakpoints(initial="1", lg="3fr 7fr")' in SURFACE
    assert 'padding=rx.breakpoints(initial="0.75rem", sm="1rem", md="1.5rem")' in SURFACE


def test_rj3_does_not_introduce_network_glue_or_core_truth_duplication():
    combined = STATE + SURFACE
    for forbidden in ("FastAPI", "requests.post(", "http://", "https://"):
        assert forbidden not in combined
