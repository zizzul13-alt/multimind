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
    assert '"Theme Studio"' in SURFACE
    assert "on_click=HostState.open_theme_studio" in SURFACE
    assert 'rx.button("Apply Composition"' in SURFACE


def test_theme_draft_is_host_owned_and_private_dna_is_optional():
    assert "from ui.dna_bridge import" in STATE
    assert "dna_available" in STATE
    assert "theme_studio_available" in STATE
    assert "list_theme_studio_dna_options" in STATE
    assert "resolve_theme_studio_composition" in STATE
    assert "design_dna" not in STATE
    assert "dna_quarantine" not in STATE
    assert "database.manager" not in STATE


def test_theme_studio_uses_role_catalogs_not_raw_private_ids():
    assert "Optional private DNA reference" not in SURFACE
    for token in (
        "identity_dna_choices",
        "web_dna_choices",
        "draft_identity_choice",
        "draft_web_choice",
        "set_draft_identity_choice",
        "set_draft_web_choice",
    ):
        assert token in STATE or token in SURFACE
    assert "HostState.identity_dna_choices" in SURFACE
    assert "HostState.web_dna_choices" in SURFACE


def test_theme_studio_live_preview_consumes_resolved_draft_tokens():
    for token in (
        "HostState.draft_background",
        "HostState.draft_surface",
        "HostState.draft_text_color",
        "HostState.draft_primary",
        "HostState.draft_accent",
        "HostState.draft_border",
        "HostState.draft_font_family",
        "HostState.draft_radius_value",
        "HostState.draft_spacing_value",
        "HostState.draft_identity_display_name",
        "HostState.draft_web_display_name",
        "HostState.draft_metadata_prominence",
        "HostState.draft_status_richness",
        "HostState.draft_navigation_density",
    ):
        assert token in SURFACE
    assert "Isolated composed live preview" in SURFACE
    assert "Draft only — active workspace unchanged" in SURFACE


def test_apply_promotes_full_composition_and_workspace_consumes_active_tokens():
    assert "self._copy_draft_to_active()" in STATE
    for token in (
        "HostState.active_background",
        "HostState.active_surface",
        "HostState.active_text_color",
        "HostState.active_primary",
        "HostState.active_accent",
        "HostState.active_border",
        "HostState.active_font_family",
        "HostState.active_radius_value",
        "HostState.active_identity_display_name",
        "HostState.active_web_display_name",
    ):
        assert token in SURFACE
    assert "Active DNA: " in SURFACE


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
    # Responsive parity is the invariant. Canonical migration adds a second
    # presentation grammar inside the same breakpoints rather than replacing
    # phone/desktop behavior or creating a second workspace.
    assert 'initial="minmax(0, 1fr)"' in SURFACE
    assert "grid_template_columns=rx.breakpoints" in SURFACE
    assert "grid_template_areas=rx.breakpoints" in SURFACE
    assert "HostState.active_dna_mode == \"canonical\"" in SURFACE
    for helper in (
        "_workspace_mobile_areas()",
        "_canonical_workspace_mobile_areas()",
        "_workspace_desktop_columns()",
        "_canonical_workspace_desktop_columns()",
        "_workspace_desktop_areas()",
        "_canonical_workspace_desktop_areas()",
    ):
        assert helper in SURFACE
    assert 'padding=rx.breakpoints(initial="0.75rem", sm="1rem", md="1.5rem")' in SURFACE


def test_rj3_does_not_introduce_network_glue_or_core_truth_duplication():
    combined = STATE + SURFACE
    for forbidden in ("FastAPI", "requests.post(", "http://", "https://"):
        assert forbidden not in combined
