"""RJ-3 Reflex production presentation surface."""

import reflex as rx

from multimind_reflex.state import AGENT_OPTIONS, ARCHETYPES, SKILL_OPTIONS, TEMPLATE_OPTIONS
from multimind_reflex.workspace_dna_state import WorkspaceDnaState as HostState


UPLOAD_ID = "rj3_upload"
RESTORE_ID = "rj3_restore"
RESTORE_ACCEPT = {
    "application/octet-stream": [".db", ".sqlite", ".sqlite3"],
    "application/x-sqlite3": [".db", ".sqlite", ".sqlite3"],
    "application/vnd.sqlite3": [".db", ".sqlite", ".sqlite3"],
}
SESSION_MODES = ["coding", "research", "thinking", "custom"]


def _login_panel() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("MultiMind AI", size="7"),
                rx.text("Reflex production host"),
                rx.input(
                    placeholder="Username",
                    value=HostState.username,
                    on_change=HostState.set_username,
                    width="100%",
                ),
                rx.button("Login", on_click=HostState.login, width="100%", class_name="mm-touch-target"),
                rx.cond(
                    HostState.error_message != "",
                    rx.callout(HostState.error_message, icon="triangle_alert"),
                ),
                spacing="4",
                width="100%",
            ),
            width="min(92vw, 28rem)",
        ),
        min_height="100vh",
        padding="1.5rem",
    )


def _theme_studio() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.vstack(
                rx.heading("Studio Tema", size="7"),
                rx.text("MusicDNA × Architecture → preview → Apply → MultiMind"),
                align="start",
                width="100%",
            ),
            rx.callout(
                rx.cond(
                    HostState.dna_runtime_available,
                    "MusicDNA berasal dari private Design-DNA. MultiMind hanya mengonsumsi projection hasil realization.",
                    "Private Design-DNA unavailable; safe neutral presentation remains operational.",
                ),
                icon="info",
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.heading("MusicDNA", size="5"),
                    rx.text("Pilih dunia musik yang menjadi identitas utama."),
                    rx.select(
                        HostState.music_dna_choices,
                        value=HostState.draft_identity_choice,
                        on_change=HostState.set_composed_identity_choice,
                        width="100%",
                    ),
                    rx.heading("Architecture", size="5"),
                    rx.text("Pilih bentuk pengalaman MultiMind untuk track tersebut."),
                    rx.select(
                        ARCHETYPES,
                        value=HostState.draft_archetype,
                        on_change=HostState.set_composed_archetype,
                        width="100%",
                    ),
                    rx.separator(),
                    rx.badge("COMBINATION"),
                    rx.text(
                        HostState.draft_identity_display_name,
                        " × ",
                        HostState.draft_archetype,
                        weight="bold",
                        size="4",
                    ),
                    width="100%",
                    spacing="3",
                ),
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.heading("Live preview", size="5"),
                    rx.badge("Draft only — active workspace unchanged"),
                    rx.text("Music: ", HostState.draft_identity_display_name),
                    rx.text("Architecture: ", HostState.draft_archetype),
                    rx.text(
                        "Preview berasal dari MusicDNA × Architecture realization.",
                        color=HostState.draft_text_color,
                    ),
                    rx.hstack(
                        rx.button(
                            "Primary action",
                            background_color=HostState.draft_primary,
                            color=HostState.draft_background,
                            border_radius=HostState.draft_radius_value,
                            class_name="mm-touch-target",
                        ),
                        rx.button(
                            "Accent action",
                            variant="outline",
                            color=HostState.draft_accent,
                            border=f"1px solid {HostState.draft_accent}",
                            border_radius=HostState.draft_radius_value,
                            class_name="mm-touch-target",
                        ),
                        wrap="wrap",
                    ),
                    rx.text(
                        "Density: ", HostState.draft_density,
                        " · spacing ", HostState.draft_spacing_value,
                        size="2",
                        color=HostState.draft_text_color,
                    ),
                    rx.separator(),
                    rx.heading("MusicDNA × Architecture contract", size="4"),
                    rx.vstack(
                        rx.text("Topology: ", HostState.draft_music_topology, size="2"),
                        rx.text("World: ", HostState.draft_music_world, size="2"),
                        rx.text("Signature: ", HostState.draft_music_signature, size="2"),
                        rx.text("Layout flow: ", HostState.draft_music_layout_flow, size="2"),
                        rx.text("Mobile strategy: ", HostState.draft_music_mobile_strategy, size="2"),
                        rx.text("Primary object: ", HostState.draft_music_primary_object, size="2"),
                        rx.text("Primary action: ", HostState.draft_music_primary_action, size="2"),
                        rx.text("Composer label: ", HostState.draft_music_composer_label, size="2"),
                        rx.text("Combination: ", HostState.draft_music_combination_id, size="2"),
                        spacing="1", align="start", width="100%",
                    ),
                    width="100%",
                    spacing="3",
                ),
                width="100%",
                background_color=HostState.draft_background,
                color=HostState.draft_text_color,
                font_family=HostState.draft_font_family,
                border=f"1px solid {HostState.draft_border}",
                border_radius=HostState.draft_radius_value,
                padding=HostState.draft_spacing_value,
            ),
            rx.hstack(
                rx.button("Apply Composition", on_click=HostState.apply_composed_theme, size="3", class_name="mm-touch-target"),
                rx.button("Discard", on_click=HostState.discard_composed_theme, variant="soft", class_name="mm-touch-target"),
                rx.button("Reset", on_click=HostState.reset_composed_theme, variant="ghost", class_name="mm-touch-target"),
                rx.cond(
                    HostState.current_session_id != "",
                    rx.button("Back to workspace", on_click=HostState.return_to_workspace, variant="outline", class_name="mm-touch-target"),
                ),
                wrap="wrap",
                width="100%",
            ),
            rx.cond(
                HostState.success_message != "",
                rx.callout(HostState.success_message, icon="circle_check", width="100%"),
            ),
            width="100%",
            spacing="4",
        ),
        max_width="52rem",
        padding=rx.breakpoints(initial="0.75rem", sm="1rem", md="1.5rem"),
        class_name="mm-theme-studio",
    )

def _session_panel() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Sessions", size="5"),
            rx.spacer(),
            rx.button("Logout", on_click=HostState.logout_composed, variant="soft", class_name="mm-touch-target"),
            width="100%",
            align="center",
        ),
        rx.input(
            placeholder="New session",
            value=HostState.new_session_name,
            on_change=HostState.set_new_session_name,
            width="100%",
        ),
        rx.select(
            SESSION_MODES,
            value=HostState.new_session_mode,
            on_change=HostState.set_new_session_mode,
            width="100%",
        ),
        rx.button("Create session", on_click=HostState.create_session, width="100%", class_name="mm-touch-target"),
        rx.separator(),
        rx.foreach(
            HostState.sessions,
            lambda session: rx.button(
                rx.vstack(
                    rx.text(session["name"], weight="bold"),
                    rx.text(session["mode"], size="1"),
                    align="start",
                    spacing="1",
                ),
                on_click=HostState.select_session(session["id"]),
                width="100%",
                variant="soft",
                class_name="mm-touch-target",
            ),
        ),
        spacing="3",
        width="100%",
    )


def _template_panel() -> rx.Component:
    return rx.vstack(
        rx.heading("Prompt template", size="4"),
        rx.select(
            TEMPLATE_OPTIONS,
            value=HostState.selected_template,
            on_change=HostState.select_template,
            placeholder="No template",
            width="100%",
        ),
        rx.cond(
            HostState.template_description != "",
            rx.text(HostState.template_description, size="2"),
        ),
        rx.cond(
            HostState.template_variables.length() > 0,
            rx.vstack(
                rx.text("Variables: ", HostState.template_variables.to_string(), size="2"),
                rx.text_area(
                    placeholder='{"topic":"..."}',
                    value=HostState.template_variables_json,
                    on_change=HostState.set_template_variables_json,
                    width="100%",
                    min_height="5rem",
                ),
                rx.text_area(
                    value=HostState.template_preview,
                    read_only=True,
                    width="100%",
                    min_height="7rem",
                ),
                rx.button("Use preview as editable prompt", on_click=HostState.use_template_preview, variant="soft", class_name="mm-touch-target"),
                width="100%",
            ),
        ),
        spacing="2",
        width="100%",
    )


def _execution_controls() -> rx.Component:
    return rx.vstack(
        rx.heading("Execution", size="4"),
        rx.hstack(
            rx.radio(
                ["continue", "standalone"],
                value=HostState.context_mode,
                on_change=HostState.set_context_mode,
            ),
            rx.spacer(),
            rx.checkbox(
                "Compressor",
                checked=HostState.compressor_enabled,
                on_change=HostState.set_compressor_enabled,
            ),
            width="100%",
            align="center",
            wrap="wrap",
        ),
        rx.text("Agents", size="2", weight="bold"),
        rx.hstack(
            *[
                rx.checkbox(
                    agent,
                    checked=HostState.active_agents.contains(agent),
                    on_change=lambda enabled, agent=agent: HostState.set_agent_enabled(agent, enabled),
                )
                for agent in AGENT_OPTIONS
            ],
            wrap="wrap",
            width="100%",
        ),
        rx.hstack(
            rx.vstack(
                rx.text("Rounds", size="2"),
                rx.select(
                    ["1", "2", "3", "4", "5"],
                    value=HostState.debate_rounds.to_string(),
                    on_change=HostState.set_debate_rounds,
                ),
                align="start",
            ),
            rx.vstack(
                rx.text("Skill", size="2"),
                rx.select(
                    SKILL_OPTIONS,
                    value=HostState.selected_skill,
                    on_change=HostState.set_selected_skill,
                ),
                align="start",
            ),
            width="100%",
            wrap="wrap",
        ),
        spacing="3",
        width="100%",
    )


def _upload_panel() -> rx.Component:
    return rx.vstack(
        rx.upload(
            rx.vstack(
                rx.text("Drop files here or click to select"),
                rx.foreach(rx.selected_files(UPLOAD_ID), rx.text),
                align="center",
                width="100%",
            ),
            id=UPLOAD_ID,
            multiple=True,
            max_files=5,
            border="1px dashed var(--gray-a8)",
            padding="1rem",
            width="100%",
        ),
        rx.hstack(
            rx.button(
                "Stage files",
                on_click=HostState.stage_uploads(rx.upload_files(upload_id=UPLOAD_ID)),
                variant="soft",
                class_name="mm-touch-target",
            ),
            rx.button(
                "Clear",
                on_click=[HostState.clear_uploads, rx.clear_selected_files(UPLOAD_ID)],
                variant="ghost",
                class_name="mm-touch-target",
            ),
            wrap="wrap",
        ),
        rx.cond(
            HostState.upload_names.length() > 0,
            rx.text("Staged: ", HostState.upload_names.to_string(), class_name="mm-readable"),
        ),
        width="100%",
        spacing="2",
    )


def _estimate_panel() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Pre-send estimate", size="3"),
            rx.hstack(
                rx.text("Participants: ", HostState.active_agents.length()),
                rx.text("Provider calls: ~", HostState.estimated_provider_calls),
                rx.text("Prompt: ", HostState.estimated_prompt_tokens, " tok"),
                rx.text("Files: ", HostState.estimated_file_tokens, " tok"),
                rx.text("Total: ", HostState.estimated_total_tokens, " tok"),
                rx.text("Cost hint: $", HostState.estimated_cost),
                wrap="wrap",
            ),
            rx.cond(
                HostState.token_warning_level == "high",
                rx.callout("High estimated token usage", icon="triangle_alert"),
                rx.cond(
                    HostState.token_warning_level == "medium",
                    rx.callout("Moderate estimated token usage", icon="info"),
                ),
            ),
            width="100%",
            spacing="2",
        ),
        width="100%",
    )


def _participant_card(participant) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(participant["participant_id"], weight="bold"),
                rx.badge(participant["status"]),
                wrap="wrap",
            ),
            rx.text("Selected: ", participant["requested_provider"], size="2"),
            rx.text(
                "Actual: ",
                rx.cond(participant["actual_provider"] != "", participant["actual_provider"], "not executed"),
                size="2",
            ),
            rx.cond(participant["model"] != "", rx.text("Model: ", participant["model"], size="2")),
            rx.cond(participant["role"] != "", rx.text("Role: ", participant["role"], size="2")),
            rx.cond(
                participant["text"] != "",
                rx.text(participant["text"], white_space="pre-wrap", class_name="mm-readable"),
                rx.text("No contribution returned.", size="2"),
            ),
            rx.cond(
                participant["failure_category"] != "",
                rx.callout(participant["failure_category"], icon="triangle_alert", width="100%"),
            ),
            align="start",
            width="100%",
        ),
        width="100%",
        class_name="mm-participant-card",
    )


def _critique_card(critique) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text("Round ", critique["round"], weight="bold"),
                rx.text(critique["participant_id"]),
                rx.badge(critique["status"]),
                wrap="wrap",
            ),
            rx.text("Actual provider: ", critique["actual_provider"], size="2"),
            rx.cond(
                critique["text"] != "",
                rx.text(critique["text"], white_space="pre-wrap", class_name="mm-readable"),
                rx.text("No critique returned.", size="2"),
            ),
            align="start",
            width="100%",
        ),
        width="100%",
        class_name="mm-critique-card",
    )


def _deliberation_panel() -> rx.Component:
    return rx.cond(
        HostState.current_participants.length() > 0,
        rx.card(
            rx.vstack(
                rx.heading("Multi-mind deliberation", size="4"),
                rx.text("Every selected participant remains independently attributable.", size="2"),
                rx.foreach(HostState.current_participants, _participant_card),
                rx.cond(
                    HostState.current_critiques.length() > 0,
                    rx.vstack(
                        rx.heading("Deliberation critiques", size="3"),
                        rx.foreach(HostState.current_critiques, _critique_card),
                        width="100%",
                    ),
                ),
                rx.separator(),
                rx.hstack(
                    rx.text(
                        "Judge: ",
                        rx.cond(HostState.current_judge_provider != "", HostState.current_judge_provider, "unavailable"),
                    ),
                    rx.cond(
                        HostState.current_judge_status != "",
                        rx.badge(HostState.current_judge_status),
                    ),
                    wrap="wrap",
                ),
                rx.cond(
                    HostState.current_system_verdict != "",
                    rx.text("System winner: ", HostState.current_system_verdict, weight="bold", class_name="mm-readable"),
                    rx.text("System winner: no valid winner marker recorded.", size="2"),
                ),
                align="start",
                width="100%",
                spacing="3",
            ),
            width="100%",
        ),
    )


def _history_panel() -> rx.Component:
    return rx.vstack(
        rx.heading("Session history", size="4"),
        rx.foreach(
            HostState.history,
            lambda row: rx.card(
                rx.vstack(
                    rx.text(row["prompt"], weight="bold", white_space="pre-wrap", class_name="mm-readable"),
                    rx.text(row["final_answer"], white_space="pre-wrap", class_name="mm-readable"),
                    rx.cond(
                        row["participant_summary"] != "",
                        rx.text("Participants: ", row["participant_summary"], size="2"),
                    ),
                    rx.cond(
                        row["judge_provider"] != "",
                        rx.text("Judge provider: ", row["judge_provider"], size="2"),
                    ),
                    rx.cond(
                        row["system_verdict"] != "",
                        rx.text("System winner: ", row["system_verdict"], size="2", weight="bold"),
                    ),
                    align="start",
                    width="100%",
                ),
                width="100%",
                class_name="mm-history-card",
            ),
        ),
        width="100%",
        spacing="2",
    )


def _data_ops() -> rx.Component:
    return rx.vstack(
        rx.heading("Backup / Restore", size="4"),
        rx.button("Export SQLite backup", on_click=HostState.export_database, variant="soft", class_name="mm-touch-target"),
        rx.text(
            "Restore accepts MultiMind SQLite backups (.db/.sqlite/.sqlite3). "
            "Tap the area below, choose one backup, confirm its filename appears, then stage it.",
            size="2",
        ),
        rx.upload(
            rx.vstack(
                rx.text("Tap to select one SQLite backup"),
                rx.foreach(rx.selected_files(RESTORE_ID), rx.text),
                align="center",
                width="100%",
            ),
            id=RESTORE_ID,
            accept=RESTORE_ACCEPT,
            multiple=False,
            max_files=1,
            width="100%",
            border="1px dashed var(--gray-a8)",
            padding="0.75rem",
        ),
        rx.hstack(
            rx.button(
                "Stage selected backup",
                on_click=HostState.stage_restore(rx.upload_files(upload_id=RESTORE_ID)),
                variant="soft",
                class_name="mm-touch-target",
            ),
            rx.button("Restore safely", on_click=HostState.restore_database, variant="outline", class_name="mm-touch-target"),
            wrap="wrap",
        ),
        rx.cond(HostState.restore_name != "", rx.text("Staged: ", HostState.restore_name, class_name="mm-readable")),
        width="100%",
        spacing="2",
    )


def _music_workspace_desktop_columns():
    return rx.cond(
        HostState.active_music_layout_flow == "state_control_matrix",
        "minmax(0, 1fr) minmax(0, 1fr)",
        rx.cond(
            HostState.active_music_layout_flow in ["multi_object_desk", "relationship_field"],
            "minmax(16rem, 0.8fr) minmax(0, 1.2fr)",
            "minmax(16rem, 1fr) minmax(0, 1.6fr)",
        ),
    )


def _music_workspace_desktop_areas():
    return rx.cond(
        HostState.active_music_layout_flow == "state_control_matrix",
        '"result result" "utility composer" "history history"',
        rx.cond(
            HostState.active_music_layout_flow == "evidence_synthesis",
            '"result utility" "result composer" "history history"',
            rx.cond(
                HostState.active_music_layout_flow == "relationship_field",
                '"composer result" "utility result" "history history"',
                rx.cond(
                    HostState.active_music_layout_flow == "instruction_execution",
                    '"composer" "result" "history" "utility"',
                    '"utility composer" "utility result" "history history"',
                ),
            ),
        ),
    )


def _music_workspace_mobile_areas():
    return rx.cond(
        HostState.active_music_mobile_strategy == "stacked_control",
        '"result" "composer" "history" "utility"',
        rx.cond(
            HostState.active_music_mobile_strategy == "serial_evidence",
            '"result" "history" "composer" "utility"',
            rx.cond(
                HostState.active_music_mobile_strategy == "stacked_entities",
                '"composer" "result" "utility" "history"',
                rx.cond(
                    HostState.active_music_mobile_strategy == "terminal_stack",
                    '"composer" "result" "history" "utility"',
                    '"composer" "result" "history" "utility"',
                ),
            ),
        ),
    )


def _workspace_desktop_columns():
    """Finite archetype vocabulary → desktop workspace columns."""
    return rx.cond(
        HostState.active_archetype == "chat_first",
        "minmax(16rem, 3fr) minmax(0, 7fr)",
        rx.cond(
            HostState.active_archetype == "command_center",
            "minmax(0, 1fr) minmax(0, 1fr)",
            rx.cond(
                HostState.active_archetype == "ai_workspace",
                "minmax(16rem, 0.8fr) minmax(0, 1.4fr)",
                rx.cond(
                    HostState.active_archetype == "ai_research_lab",
                    "minmax(0, 1.45fr) minmax(16rem, 0.65fr)",
                    rx.cond(
                        HostState.active_archetype == "agent_canvas",
                        "minmax(16rem, 0.75fr) minmax(0, 1.25fr)",
                        "minmax(0, 1fr)",
                    ),
                ),
            ),
        ),
    )


def _workspace_desktop_areas():
    """Map semantic zones without duplicating application-owned controls."""
    return rx.cond(
        HostState.active_archetype == "chat_first",
        '"utility composer" "utility result" "utility history"',
        rx.cond(
            HostState.active_archetype == "command_center",
            '"result result" "utility composer" "history history"',
            rx.cond(
                HostState.active_archetype == "ai_workspace",
                '"utility composer" "utility result" "history history"',
                rx.cond(
                    HostState.active_archetype == "ai_research_lab",
                    '"result utility" "result composer" "history history"',
                    rx.cond(
                        HostState.active_archetype == "agent_canvas",
                        '"composer result" "utility result" "history history"',
                        rx.cond(
                            HostState.active_archetype == "terminal_hacker",
                            '"composer" "result" "history" "utility"',
                            '"composer" "result" "history" "utility"',
                        ),
                    ),
                ),
            ),
        ),
    )


def _workspace_mobile_areas():
    """Mobile order follows archetype meaning instead of desktop cropping."""
    return rx.cond(
        HostState.active_archetype == "command_center",
        '"result" "composer" "history" "utility"',
        rx.cond(
            HostState.active_archetype == "ai_research_lab",
            '"result" "history" "composer" "utility"',
            rx.cond(
                HostState.active_archetype == "agent_canvas",
                '"composer" "result" "utility" "history"',
                '"composer" "result" "history" "utility"',
            ),
        ),
    )


def _canonical_workspace_desktop_columns():
    """Canonical layout-flow vocabulary → real workspace desktop columns."""
    return rx.cond(
        HostState.active_canonical_layout_flow == "grid",
        "repeat(2, minmax(0, 1fr))",
        rx.cond(
            HostState.active_canonical_layout_flow == "components",
            "minmax(16rem, 0.8fr) minmax(0, 1.2fr)",
            rx.cond(
                HostState.active_canonical_layout_flow == "grouped",
                "minmax(16rem, 0.85fr) minmax(0, 1.15fr)",
                rx.cond(
                    HostState.active_canonical_layout_flow == "paired",
                    "repeat(2, minmax(0, 1fr))",
                    "minmax(0, 1fr)",
                ),
            ),
        ),
    )


def _canonical_workspace_desktop_areas():
    """Canonical structural grammar over the same four real semantic zones."""
    return rx.cond(
        HostState.active_canonical_layout_flow == "grid",
        '"composer result" "utility history"',
        rx.cond(
            HostState.active_canonical_layout_flow == "components",
            '"composer result" "utility result" "history history"',
            rx.cond(
                HostState.active_canonical_layout_flow == "grouped",
                '"utility composer" "utility result" "history history"',
                rx.cond(
                    HostState.active_canonical_layout_flow == "paired",
                    '"composer result" "utility history"',
                    rx.cond(
                        HostState.active_canonical_layout_flow == "continuous",
                        '"composer" "result" "history" "utility"',
                        rx.cond(
                            HostState.active_canonical_layout_flow == "directional",
                            '"utility" "composer" "result" "history"',
                            '"utility" "composer" "result" "history"',
                        ),
                    ),
                ),
            ),
        ),
    )


def _canonical_workspace_mobile_areas():
    """Canonical mobile strategy changes real mobile order, never desktop crop."""
    return rx.cond(
        HostState.active_canonical_mobile_strategy == "ordered_flow",
        '"composer" "result" "history" "utility"',
        rx.cond(
            HostState.active_canonical_mobile_strategy == "component_reflow",
            '"composer" "utility" "result" "history"',
            rx.cond(
                HostState.active_canonical_mobile_strategy == "serial_groups",
                '"utility" "composer" "result" "history"',
                rx.cond(
                    HostState.active_canonical_mobile_strategy == "serial_clusters",
                    '"result" "composer" "utility" "history"',
                    rx.cond(
                        HostState.active_canonical_mobile_strategy == "stack_pairs",
                        '"composer" "result" "utility" "history"',
                        rx.cond(
                            HostState.active_canonical_mobile_strategy == "ordered_asymmetry",
                            '"composer" "utility" "result" "history"',
                            rx.cond(
                                HostState.active_canonical_mobile_strategy == "reduced_continuity",
                                '"composer" "result" "history" "utility"',
                                rx.cond(
                                    HostState.active_canonical_mobile_strategy == "vertical_punctuation",
                                    '"utility" "composer" "result" "history"',
                                    '"utility" "composer" "result" "history"',
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


def _workspace_zone_card(child: rx.Component, area: str) -> rx.Component:
    return rx.card(
        child,
        grid_area=area,
        min_width="0",
        width="100%",
        background_color=HostState.active_surface,
        color=HostState.active_text_color,
        border=f"1px solid {HostState.active_border}",
        border_radius=rx.cond(
            HostState.active_dna_mode == "canonical",
            HostState.active_canonical_card_radius,
            HostState.active_radius_value,
        ),
        padding=rx.cond(
            HostState.active_dna_mode == "canonical",
            HostState.active_canonical_card_padding,
            HostState.active_spacing_value,
        ),
        class_name=f"mm-zone mm-zone-{area}",
    )


def _workspace_utility_zone() -> rx.Component:
    return _workspace_zone_card(
        rx.vstack(
            _session_panel(),
            rx.separator(),
            _data_ops(),
            width="100%",
            spacing="4",
        ),
        "utility",
    )


def _workspace_composer_zone() -> rx.Component:
    return _workspace_zone_card(
        rx.vstack(
            rx.heading(
                rx.cond(
                    HostState.current_session_name != "",
                    HostState.current_session_name,
                    "Select or create a session",
                ),
                size="5",
                color=HostState.active_primary,
            ),
            _template_panel(),
            rx.text_area(
                placeholder="Prompt",
                value=HostState.prompt,
                on_change=HostState.set_prompt,
                min_height="10rem",
                width="100%",
                class_name="mm-prompt",
            ),
            _execution_controls(),
            _upload_panel(),
            _estimate_panel(),
            rx.button(
                rx.cond(
                    HostState.active_dna_mode == "music",
                    HostState.active_music_primary_action,
                    rx.cond(HostState.busy, "Running…", "Run"),
                ),
                on_click=HostState.run_chat,
                disabled=HostState.busy,
                width="100%",
                size="3",
                background_color=HostState.active_primary,
                color=HostState.active_background,
                border_radius=HostState.active_radius_value,
                class_name="mm-run-button",
            ),
            rx.cond(HostState.status_message != "", rx.text(HostState.status_message, class_name="mm-readable")),
            rx.cond(
                HostState.error_message != "",
                rx.callout(HostState.error_message, icon="triangle_alert", width="100%"),
            ),
            rx.cond(
                HostState.success_message != "",
                rx.callout(HostState.success_message, icon="circle_check", width="100%"),
            ),
            rx.foreach(HostState.warnings, lambda warning: rx.callout(warning, icon="info", width="100%")),
            width="100%",
            spacing="3",
        ),
        "composer",
    )


def _workspace_result_zone() -> rx.Component:
    return _workspace_zone_card(
        rx.vstack(
            rx.heading(
                rx.cond(
                    HostState.active_dna_mode == "music",
                    HostState.active_music_primary_object,
                    rx.cond(
                        HostState.active_archetype == "command_center",
                    "Operational result",
                    rx.cond(
                        HostState.active_archetype == "ai_research_lab",
                        "Synthesis / evidence",
                        rx.cond(
                            HostState.active_archetype == "agent_canvas",
                            "Execution topology / result",
                            rx.cond(
                                HostState.active_archetype == "terminal_hacker",
                                "Execution output",
                                "Result / deliberation",
                            ),
                            ),
                        ),
                    ),
                ),
                size="4",
                color=HostState.active_primary,
            ),
            rx.cond(
                HostState.final_answer != "",
                rx.card(
                    rx.vstack(
                        rx.heading("Final answer", size="4"),
                        rx.text(HostState.final_answer, white_space="pre-wrap", class_name="mm-readable"),
                        align="start",
                    ),
                    width="100%",
                    class_name="mm-result-card",
                ),
                rx.text("No result yet.", size="2"),
            ),
            _deliberation_panel(),
            width="100%",
            spacing="3",
        ),
        "result",
    )


def _workspace_history_zone() -> rx.Component:
    return _workspace_zone_card(_history_panel(), "history")


def _workspace() -> rx.Component:
    # The four real semantic zones are instantiated exactly once. Archetype and
    # canonical DNA change only presentation composition; application/provider/
    # persistence truth remains behind the same event and application paths.
    return rx.container(
        rx.vstack(
            rx.card(
                rx.hstack(
                    rx.vstack(
                        rx.heading("MultiMind", size="7", color=HostState.active_primary),
                        rx.text("Logged in as ", HostState.display_username),
                        rx.text("Archetype: ", HostState.active_archetype, size="2"),
                        rx.cond(
                            HostState.active_dna_mode == "canonical",
                            rx.text(
                                "Canonical DNA: ",
                                HostState.active_canonical_display_name,
                                " · ",
                                HostState.active_canonical_reference_id,
                                size="2",
                                class_name="mm-readable",
                            ),
                            rx.text(
                                "Active DNA: ",
                                HostState.active_identity_display_name,
                                " + ",
                                HostState.active_web_display_name,
                                size="2",
                                class_name="mm-readable",
                            ),
                        ),
                        align="start",
                    ),
                    rx.spacer(),
                    rx.badge(rx.cond(HostState.busy, "BUSY", "READY")),
                    rx.button(
                        "Theme Studio",
                        on_click=HostState.open_theme_studio,
                        variant="soft",
                        color=HostState.active_accent,
                        class_name="mm-touch-target",
                    ),
                    width="100%",
                    align="center",
                    wrap="wrap",
                ),
                width="100%",
                background_color=HostState.active_surface,
                color=HostState.active_text_color,
                border=f"1px solid {HostState.active_border}",
                border_radius=rx.cond(
                    HostState.active_dna_mode == "canonical",
                    HostState.active_canonical_card_radius,
                    HostState.active_radius_value,
                ),
                class_name="mm-workspace-header",
            ),
            rx.grid(
                _workspace_utility_zone(),
                _workspace_composer_zone(),
                _workspace_result_zone(),
                _workspace_history_zone(),
                grid_template_columns=rx.breakpoints(
                    initial="minmax(0, 1fr)",
                    lg=rx.cond(
                        HostState.active_dna_mode == "music",
                        _music_workspace_desktop_columns(),
                        rx.cond(
                            HostState.active_dna_mode == "canonical",
                            _canonical_workspace_desktop_columns(),
                            _workspace_desktop_columns(),
                        ),
                    ),
                ),
                grid_template_areas=rx.breakpoints(
                    initial=rx.cond(
                        HostState.active_dna_mode == "music",
                        _music_workspace_mobile_areas(),
                        rx.cond(
                            HostState.active_dna_mode == "canonical",
                            _canonical_workspace_mobile_areas(),
                            _workspace_mobile_areas(),
                        ),
                    ),
                    lg=rx.cond(
                        HostState.active_dna_mode == "music",
                        _music_workspace_desktop_areas(),
                        rx.cond(
                            HostState.active_dna_mode == "canonical",
                            _canonical_workspace_desktop_areas(),
                            _workspace_desktop_areas(),
                        ),
                    ),
                ),
                gap=rx.cond(
                    HostState.active_dna_mode == "music",
                    HostState.active_spacing_value,
                    rx.cond(
                        HostState.active_dna_mode == "canonical",
                        HostState.active_canonical_gap,
                        "1rem",
                    ),
                ),
                width="100%",
                align_items="start",
                class_name="mm-workspace-grid",
            ),
            width="100%",
            spacing="4",
        ),
        max_width=rx.cond(
            HostState.active_archetype == "minimal_saas",
            "68rem",
            rx.cond(HostState.active_archetype == "terminal_hacker", "76rem", "88rem"),
        ),
        padding=rx.breakpoints(initial="0.75rem", sm="1rem", md="1.5rem"),
        background_color=HostState.active_background,
        color=HostState.active_text_color,
        font_family=rx.cond(
            HostState.active_archetype == "terminal_hacker",
            HostState.active_mono_font,
            rx.cond(
                HostState.active_dna_mode == "canonical",
                HostState.active_canonical_font_family,
                HostState.active_font_family,
            ),
        ),
        line_height=rx.cond(
            HostState.active_dna_mode == "canonical",
            HostState.active_canonical_line_height,
            "1.5",
        ),
        min_height="100vh",
        class_name="mm-workspace",
    )


def _authenticated_surface() -> rx.Component:
    return rx.cond(HostState.current_surface == "theme", _theme_studio(), _workspace())


def index() -> rx.Component:
    return rx.cond(HostState.logged_in, _authenticated_surface(), _login_panel())


app = rx.App(stylesheets=["/mobile-workspace-polish.css"])
app.add_page(index, title="MultiMind AI — Reflex Host")
