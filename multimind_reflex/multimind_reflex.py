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
                rx.button("Login", on_click=HostState.login, width="100%", min_height="2.75rem"),
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
        padding="1rem",
    )


def _canonical_reference_result(item) -> rx.Component:
    return rx.button(
        rx.vstack(
            rx.text(
                item["display_name"],
                weight="bold",
                text_align="left",
                white_space="normal",
                overflow_wrap="anywhere",
            ),
            rx.text(
                item["id"],
                " · ",
                item["category"],
                size="1",
                text_align="left",
                white_space="normal",
                overflow_wrap="anywhere",
            ),
            align="start",
            spacing="1",
            width="100%",
        ),
        on_click=HostState.select_canonical_reference(item["id"]),
        width="100%",
        min_height="3.25rem",
        variant="soft",
        justify_content="flex-start",
        white_space="normal",
    )


def _theme_studio_actions() -> rx.Component:
    # One action surface only. It becomes sticky on narrow screens so Apply /
    # Discard / Reset stay reachable after scrolling a long catalog or preview.
    return rx.box(
        rx.hstack(
            rx.button(
                "Apply Composition",
                on_click=HostState.apply_composed_theme,
                size="3",
                min_height="2.75rem",
            ),
            rx.button(
                "Discard",
                on_click=HostState.discard_composed_theme,
                variant="soft",
                min_height="2.75rem",
            ),
            rx.button(
                "Reset",
                on_click=HostState.reset_composed_theme,
                variant="ghost",
                min_height="2.75rem",
            ),
            rx.cond(
                HostState.current_session_id != "",
                rx.button(
                    "Back to workspace",
                    on_click=HostState.return_to_workspace,
                    variant="outline",
                    min_height="2.75rem",
                ),
            ),
            wrap="wrap",
            width="100%",
            spacing="2",
        ),
        position=rx.breakpoints(initial="sticky", md="static"),
        bottom=rx.breakpoints(initial="0.5rem", md="auto"),
        z_index="20",
        width="100%",
        padding=rx.breakpoints(initial="0.6rem", md="0"),
        background_color=rx.breakpoints(initial="var(--color-panel-solid)", md="transparent"),
        border=rx.breakpoints(initial="1px solid var(--gray-a5)", md="none"),
        border_radius=rx.breakpoints(initial="0.75rem", md="0"),
        box_shadow=rx.breakpoints(initial="0 8px 24px var(--black-a4)", md="none"),
    )


def _theme_studio() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.heading("Theme Studio", size="7"),
                    rx.text("Choose DNA → preview → explicit Apply → workspace", size="2"),
                    align="start",
                    spacing="1",
                    min_width="0",
                ),
                rx.spacer(),
                rx.badge(HostState.theme_status),
                width="100%",
                align="center",
                wrap="wrap",
                gap="0.75rem",
            ),
            rx.callout(
                rx.cond(
                    HostState.dna_runtime_available,
                    "Private Design-DNA is available server-side. Canonical references are preferred; the legacy role-based composition remains an explicit rollback path.",
                    "Private Design-DNA unavailable; safe neutral presentation remains operational.",
                ),
                icon="info",
                width="100%",
            ),
            rx.grid(
                rx.card(
                    rx.vstack(
                        rx.heading("Composition draft", size="5"),
                        rx.text("UI / UX Archetype", size="2", weight="bold"),
                        rx.select(
                            ARCHETYPES,
                            value=HostState.draft_archetype,
                            on_change=HostState.set_composed_archetype,
                            width="100%",
                        ),
                        rx.separator(),
                        rx.heading("Canonical Reference DNA", size="4"),
                        rx.hstack(
                            rx.badge("Canonical 160", variant="soft"),
                            rx.text("Catalog: ", HostState.canonical_catalog_total, size="2"),
                            rx.text("Host-ready: ", HostState.canonical_host_ready_total, size="2"),
                            wrap="wrap",
                            spacing="2",
                        ),
                        rx.input(
                            placeholder="Search name, family, category, lineage, or ID",
                            value=HostState.canonical_query,
                            on_change=HostState.set_canonical_query,
                            width="100%",
                        ),
                        rx.cond(
                            HostState.canonical_catalog_total > 0,
                            rx.vstack(
                                rx.foreach(HostState.filtered_canonical_catalog, _canonical_reference_result),
                                width="100%",
                                spacing="2",
                                max_height=rx.breakpoints(initial="14rem", md="20rem"),
                                overflow_y="auto",
                                padding_right="0.15rem",
                            ),
                            rx.callout(
                                "Canonical package unavailable in this host; legacy/neutral presentation remains safe.",
                                icon="info",
                                width="100%",
                            ),
                        ),
                        rx.cond(
                            HostState.draft_dna_mode == "canonical",
                            rx.card(
                                rx.vstack(
                                    rx.hstack(
                                        rx.badge("CANONICAL", variant="solid"),
                                        rx.text(
                                            HostState.draft_canonical_reference_id,
                                            weight="bold",
                                            overflow_wrap="anywhere",
                                        ),
                                        wrap="wrap",
                                    ),
                                    rx.text(
                                        HostState.draft_canonical_display_name,
                                        weight="bold",
                                        overflow_wrap="anywhere",
                                    ),
                                    rx.text(
                                        "Layout ",
                                        HostState.draft_canonical_layout_flow,
                                        " · mobile ",
                                        HostState.draft_canonical_mobile_strategy,
                                        size="2",
                                        overflow_wrap="anywhere",
                                    ),
                                    rx.text(
                                        "Density ",
                                        HostState.draft_canonical_density,
                                        " · hierarchy ",
                                        HostState.draft_canonical_hierarchy,
                                        " · balance ",
                                        HostState.draft_canonical_balance,
                                        size="2",
                                        overflow_wrap="anywhere",
                                    ),
                                    width="100%",
                                    spacing="2",
                                    align="start",
                                ),
                                width="100%",
                            ),
                        ),
                        rx.button(
                            "Use legacy role-based composition",
                            on_click=HostState.use_legacy_dna,
                            variant="outline",
                            width="100%",
                            min_height="2.75rem",
                        ),
                        rx.separator(),
                        rx.heading("Legacy rollback composition", size="4"),
                        rx.text("Identity / Cultural DNA", size="2", weight="bold"),
                        rx.select(
                            HostState.identity_dna_choices,
                            value=HostState.draft_identity_choice,
                            on_change=HostState.set_composed_identity_choice,
                            width="100%",
                        ),
                        rx.text("Web / Information DNA", size="2", weight="bold"),
                        rx.select(
                            HostState.web_dna_choices,
                            value=HostState.draft_web_choice,
                            on_change=HostState.set_composed_web_choice,
                            width="100%",
                        ),
                        rx.separator(),
                        rx.heading("Editable presentation controls", size="4"),
                        rx.text("Semantic colors", size="2", weight="bold"),
                        rx.grid(
                            rx.input(
                                placeholder="#RRGGBB background",
                                value=HostState.draft_background,
                                on_change=HostState.set_draft_background,
                                width="100%",
                            ),
                            rx.input(
                                placeholder="#RRGGBB surface",
                                value=HostState.draft_surface,
                                on_change=HostState.set_draft_surface,
                                width="100%",
                            ),
                            rx.input(
                                placeholder="#RRGGBB text",
                                value=HostState.draft_text_color,
                                on_change=HostState.set_draft_text_color,
                                width="100%",
                            ),
                            rx.input(
                                placeholder="#RRGGBB primary",
                                value=HostState.draft_primary,
                                on_change=HostState.set_draft_primary,
                                width="100%",
                            ),
                            rx.input(
                                placeholder="#RRGGBB accent",
                                value=HostState.draft_accent,
                                on_change=HostState.set_draft_accent,
                                width="100%",
                            ),
                            rx.input(
                                placeholder="#RRGGBB border",
                                value=HostState.draft_border,
                                on_change=HostState.set_draft_border,
                                width="100%",
                            ),
                            columns=rx.breakpoints(initial="1", sm="2"),
                            spacing="2",
                            width="100%",
                        ),
                        rx.text("Typography", size="2", weight="bold"),
                        rx.input(
                            placeholder="Base font stack",
                            value=HostState.draft_font_family,
                            on_change=HostState.set_draft_font_family,
                            width="100%",
                        ),
                        rx.input(
                            placeholder="Monospace font stack",
                            value=HostState.draft_mono_font,
                            on_change=HostState.set_draft_mono_font,
                            width="100%",
                        ),
                        rx.grid(
                            rx.vstack(
                                rx.text("Density", size="2", weight="bold"),
                                rx.select(
                                    ["compact", "comfortable", "spacious"],
                                    value=HostState.draft_density,
                                    on_change=HostState.set_draft_density,
                                    width="100%",
                                ),
                                width="100%",
                                spacing="1",
                            ),
                            rx.vstack(
                                rx.text("Radius", size="2", weight="bold"),
                                rx.select(
                                    ["none", "small", "medium", "large"],
                                    value=HostState.draft_radius,
                                    on_change=HostState.set_draft_radius,
                                    width="100%",
                                ),
                                width="100%",
                                spacing="1",
                            ),
                            columns=rx.breakpoints(initial="1", sm="2"),
                            spacing="2",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.card(
                    rx.vstack(
                        rx.heading("Isolated composed live preview", size="5"),
                        rx.badge("Draft only — active workspace unchanged", variant="soft"),
                        rx.hstack(
                            rx.text("Archetype: ", HostState.draft_archetype, size="2"),
                            rx.text("DNA mode: ", HostState.draft_dna_mode, size="2"),
                            wrap="wrap",
                            spacing="2",
                        ),
                        rx.cond(
                            HostState.draft_dna_mode == "canonical",
                            rx.vstack(
                                rx.text(
                                    "Canonical reference: ",
                                    HostState.draft_canonical_display_name,
                                    overflow_wrap="anywhere",
                                ),
                                rx.text(
                                    "Host grammar: ",
                                    HostState.draft_canonical_layout_flow,
                                    " · ",
                                    HostState.draft_canonical_mobile_strategy,
                                    size="2",
                                    overflow_wrap="anywhere",
                                ),
                                width="100%",
                                align="start",
                                spacing="1",
                            ),
                            rx.vstack(
                                rx.text("Identity: ", HostState.draft_identity_display_name),
                                rx.text("Web DNA: ", HostState.draft_web_display_name),
                                width="100%",
                                align="start",
                                spacing="1",
                            ),
                        ),
                        rx.text(
                            "Information policy: metadata ",
                            HostState.draft_metadata_prominence,
                            " · status ",
                            HostState.draft_status_richness,
                            " · navigation ",
                            HostState.draft_navigation_density,
                            size="2",
                            overflow_wrap="anywhere",
                        ),
                        rx.text(
                            "Identity semantics: hierarchy ",
                            HostState.draft_hierarchy_contrast,
                            " · surface ",
                            HostState.draft_surface_treatment,
                            " · energy ",
                            HostState.draft_energy_emphasis,
                            size="2",
                            overflow_wrap="anywhere",
                        ),
                        rx.separator(),
                        rx.card(
                            rx.vstack(
                                rx.heading("MultiMind", size="6", color=HostState.draft_primary),
                                rx.text(
                                    "This preview is rendered from the selected presentation composition. Application/session truth stays unchanged until Apply.",
                                    color=HostState.draft_text_color,
                                    overflow_wrap="anywhere",
                                ),
                                rx.hstack(
                                    rx.button(
                                        "Primary action",
                                        background_color=HostState.draft_primary,
                                        color=HostState.draft_background,
                                        border_radius=HostState.draft_radius_value,
                                        min_height="2.75rem",
                                    ),
                                    rx.button(
                                        "Accent action",
                                        variant="outline",
                                        color=HostState.draft_accent,
                                        border=f"1px solid {HostState.draft_accent}",
                                        border_radius=HostState.draft_radius_value,
                                        min_height="2.75rem",
                                    ),
                                    wrap="wrap",
                                ),
                                rx.text(
                                    "Density preview: ",
                                    HostState.draft_density,
                                    " · spacing ",
                                    HostState.draft_spacing_value,
                                    size="2",
                                    color=HostState.draft_text_color,
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            width="100%",
                            background_color=HostState.draft_surface,
                            border=f"1px solid {HostState.draft_border}",
                            border_radius=HostState.draft_radius_value,
                            padding=HostState.draft_spacing_value,
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    width="100%",
                    min_width="0",
                    background_color=HostState.draft_background,
                    color=HostState.draft_text_color,
                    font_family=HostState.draft_font_family,
                    border=f"1px solid {HostState.draft_border}",
                    border_radius=HostState.draft_radius_value,
                ),
                columns=rx.breakpoints(initial="1", md="1fr 1fr"),
                spacing=rx.breakpoints(initial="3", md="4"),
                width="100%",
            ),
            _theme_studio_actions(),
            rx.cond(
                HostState.success_message != "",
                rx.callout(HostState.success_message, icon="circle_check", width="100%"),
            ),
            width="100%",
            spacing=rx.breakpoints(initial="3", md="4"),
        ),
        max_width="72rem",
        padding=rx.breakpoints(initial="0.5rem", sm="1rem", md="1.5rem"),
    )


def _session_panel() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Sessions", size="5"),
            rx.spacer(),
            rx.button(
                "Logout",
                on_click=HostState.logout_composed,
                variant="soft",
                min_height="2.6rem",
            ),
            width="100%",
            align="center",
        ),
        rx.grid(
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
            columns=rx.breakpoints(initial="1", sm="2"),
            spacing="2",
            width="100%",
        ),
        rx.button(
            "Create session",
            on_click=HostState.create_session,
            width="100%",
            min_height="2.75rem",
        ),
        rx.separator(),
        rx.foreach(
            HostState.sessions,
            lambda session: rx.button(
                rx.vstack(
                    rx.text(session["name"], weight="bold", overflow_wrap="anywhere"),
                    rx.text(session["mode"], size="1"),
                    align="start",
                    spacing="1",
                ),
                on_click=HostState.select_session(session["id"]),
                width="100%",
                min_height="2.75rem",
                variant="soft",
                white_space="normal",
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
            rx.text(HostState.template_description, size="2", overflow_wrap="anywhere"),
        ),
        rx.cond(
            HostState.template_variables.length() > 0,
            rx.vstack(
                rx.text(
                    "Variables: ",
                    HostState.template_variables.to_string(),
                    size="2",
                    overflow_wrap="anywhere",
                ),
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
                rx.button(
                    "Use preview as editable prompt",
                    on_click=HostState.use_template_preview,
                    variant="soft",
                    min_height="2.75rem",
                    width=rx.breakpoints(initial="100%", sm="auto"),
                ),
                width="100%",
            ),
        ),
        spacing="2",
        width="100%",
    )


def _execution_controls() -> rx.Component:
    return rx.vstack(
        rx.heading("Execution", size="4"),
        rx.flex(
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
            gap="0.75rem",
        ),
        rx.text("Agents", size="2", weight="bold"),
        rx.flex(
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
            gap="0.65rem 1rem",
        ),
        rx.grid(
            rx.vstack(
                rx.text("Rounds", size="2", weight="bold"),
                rx.select(
                    ["1", "2", "3", "4", "5"],
                    value=HostState.debate_rounds.to_string(),
                    on_change=HostState.set_debate_rounds,
                    width="100%",
                ),
                align="start",
                width="100%",
                spacing="1",
            ),
            rx.vstack(
                rx.text("Skill", size="2", weight="bold"),
                rx.select(
                    SKILL_OPTIONS,
                    value=HostState.selected_skill,
                    on_change=HostState.set_selected_skill,
                    width="100%",
                ),
                align="start",
                width="100%",
                spacing="1",
            ),
            columns=rx.breakpoints(initial="1", sm="2"),
            spacing="2",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


def _upload_panel() -> rx.Component:
    return rx.vstack(
        rx.upload(
            rx.vstack(
                rx.text("Add files · up to 5", weight="bold"),
                rx.text("Tap to choose or drop files here", size="2"),
                rx.foreach(rx.selected_files(UPLOAD_ID), rx.text),
                align="center",
                width="100%",
                spacing="1",
            ),
            id=UPLOAD_ID,
            multiple=True,
            max_files=5,
            border="1px dashed var(--gray-a8)",
            padding=rx.breakpoints(initial="0.75rem", md="1rem"),
            width="100%",
        ),
        rx.hstack(
            rx.button(
                "Stage files",
                on_click=HostState.stage_uploads(rx.upload_files(upload_id=UPLOAD_ID)),
                variant="soft",
                min_height="2.6rem",
            ),
            rx.button(
                "Clear",
                on_click=[HostState.clear_uploads, rx.clear_selected_files(UPLOAD_ID)],
                variant="ghost",
                min_height="2.6rem",
            ),
            wrap="wrap",
        ),
        rx.cond(
            HostState.upload_names.length() > 0,
            rx.text("Staged: ", HostState.upload_names.to_string(), size="2", overflow_wrap="anywhere"),
        ),
        width="100%",
        spacing="2",
    )


def _estimate_panel() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Pre-send estimate", size="3"),
            rx.grid(
                rx.text("Participants: ", HostState.active_agents.length(), size="2"),
                rx.text("Provider calls: ~", HostState.estimated_provider_calls, size="2"),
                rx.text("Prompt: ", HostState.estimated_prompt_tokens, " tok", size="2"),
                rx.text("Files: ", HostState.estimated_file_tokens, " tok", size="2"),
                rx.text("Total: ", HostState.estimated_total_tokens, " tok", size="2"),
                rx.text("Cost hint: $", HostState.estimated_cost, size="2"),
                columns=rx.breakpoints(initial="2", sm="3"),
                spacing="2",
                width="100%",
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
            rx.flex(
                rx.text(participant["participant_id"], weight="bold", overflow_wrap="anywhere"),
                rx.badge(participant["status"]),
                wrap="wrap",
                gap="0.5rem",
                align="center",
                width="100%",
            ),
            rx.grid(
                rx.text("Selected: ", participant["requested_provider"], size="2", overflow_wrap="anywhere"),
                rx.text(
                    "Actual: ",
                    rx.cond(participant["actual_provider"] != "", participant["actual_provider"], "not executed"),
                    size="2",
                    overflow_wrap="anywhere",
                ),
                rx.cond(participant["model"] != "", rx.text("Model: ", participant["model"], size="2", overflow_wrap="anywhere")),
                rx.cond(participant["role"] != "", rx.text("Role: ", participant["role"], size="2", overflow_wrap="anywhere")),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="1",
                width="100%",
            ),
            rx.cond(
                participant["text"] != "",
                rx.text(
                    participant["text"],
                    white_space="pre-wrap",
                    overflow_wrap="anywhere",
                    line_height="1.6",
                ),
                rx.text("No contribution returned.", size="2"),
            ),
            rx.cond(
                participant["failure_category"] != "",
                rx.callout(participant["failure_category"], icon="triangle_alert", width="100%"),
            ),
            align="start",
            width="100%",
            spacing="2",
        ),
        width="100%",
        min_width="0",
    )


def _critique_card(critique) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.flex(
                rx.text("Round ", critique["round"], weight="bold"),
                rx.text(critique["participant_id"], overflow_wrap="anywhere"),
                rx.badge(critique["status"]),
                wrap="wrap",
                gap="0.5rem",
            ),
            rx.text("Actual provider: ", critique["actual_provider"], size="2", overflow_wrap="anywhere"),
            rx.cond(
                critique["text"] != "",
                rx.text(
                    critique["text"],
                    white_space="pre-wrap",
                    overflow_wrap="anywhere",
                    line_height="1.6",
                ),
                rx.text("No critique returned.", size="2"),
            ),
            align="start",
            width="100%",
            spacing="2",
        ),
        width="100%",
        min_width="0",
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
                        spacing="2",
                    ),
                ),
                rx.separator(),
                rx.flex(
                    rx.text(
                        "Judge: ",
                        rx.cond(HostState.current_judge_provider != "", HostState.current_judge_provider, "unavailable"),
                        overflow_wrap="anywhere",
                    ),
                    rx.cond(
                        HostState.current_judge_status != "",
                        rx.badge(HostState.current_judge_status),
                    ),
                    wrap="wrap",
                    gap="0.5rem",
                    align="center",
                ),
                rx.cond(
                    HostState.current_system_verdict != "",
                    rx.text("System winner: ", HostState.current_system_verdict, weight="bold", overflow_wrap="anywhere"),
                    rx.text("System winner: no valid winner marker recorded.", size="2"),
                ),
                align="start",
                width="100%",
                spacing="3",
            ),
            width="100%",
            min_width="0",
        ),
    )


def _history_panel() -> rx.Component:
    return rx.vstack(
        rx.heading("Session history", size="4"),
        rx.foreach(
            HostState.history,
            lambda row: rx.card(
                rx.vstack(
                    rx.text(
                        row["prompt"],
                        weight="bold",
                        white_space="pre-wrap",
                        overflow_wrap="anywhere",
                    ),
                    rx.text(
                        row["final_answer"],
                        white_space="pre-wrap",
                        overflow_wrap="anywhere",
                        line_height="1.6",
                    ),
                    rx.cond(
                        row["participant_summary"] != "",
                        rx.text("Participants: ", row["participant_summary"], size="2", overflow_wrap="anywhere"),
                    ),
                    rx.cond(
                        row["judge_provider"] != "",
                        rx.text("Judge provider: ", row["judge_provider"], size="2", overflow_wrap="anywhere"),
                    ),
                    rx.cond(
                        row["system_verdict"] != "",
                        rx.text("System winner: ", row["system_verdict"], size="2", weight="bold", overflow_wrap="anywhere"),
                    ),
                    align="start",
                    width="100%",
                    spacing="2",
                ),
                width="100%",
                min_width="0",
            ),
        ),
        width="100%",
        spacing="2",
    )


def _data_ops() -> rx.Component:
    return rx.vstack(
        rx.heading("Backup / Restore", size="4"),
        rx.button(
            "Export SQLite backup",
            on_click=HostState.export_database,
            variant="soft",
            min_height="2.6rem",
        ),
        rx.text(
            "Restore accepts MultiMind SQLite backups (.db/.sqlite/.sqlite3). "
            "Tap the area below, choose one backup, confirm its filename appears, then stage it.",
            size="2",
            overflow_wrap="anywhere",
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
                min_height="2.6rem",
            ),
            rx.button(
                "Restore safely",
                on_click=HostState.restore_database,
                variant="outline",
                min_height="2.6rem",
            ),
            wrap="wrap",
        ),
        rx.cond(
            HostState.restore_name != "",
            rx.text("Staged: ", HostState.restore_name, size="2", overflow_wrap="anywhere"),
        ),
        width="100%",
        spacing="2",
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
        overflow_x="hidden",
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
    )


def _workspace_utility_zone() -> rx.Component:
    return _workspace_zone_card(
        rx.vstack(
            _session_panel(),
            rx.separator(),
            _data_ops(),
            width="100%",
            spacing=rx.breakpoints(initial="3", md="4"),
        ),
        "utility",
    )


def _primary_run_button() -> rx.Component:
    # Keep exactly one Run control. Sticky positioning on phones removes the
    # long-scroll penalty without creating a second execution path.
    return rx.box(
        rx.button(
            rx.cond(HostState.busy, "Running…", "Run"),
            on_click=HostState.run_chat,
            disabled=HostState.busy,
            width="100%",
            size="3",
            min_height="3rem",
            background_color=HostState.active_primary,
            color=HostState.active_background,
            border_radius=HostState.active_radius_value,
        ),
        position=rx.breakpoints(initial="sticky", md="static"),
        bottom=rx.breakpoints(initial="0.5rem", md="auto"),
        z_index="10",
        width="100%",
        padding=rx.breakpoints(initial="0.35rem", md="0"),
        background_color=rx.breakpoints(initial=HostState.active_surface, md="transparent"),
        border_radius=HostState.active_radius_value,
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
                overflow_wrap="anywhere",
            ),
            _template_panel(),
            rx.text_area(
                placeholder="Prompt",
                value=HostState.prompt,
                on_change=HostState.set_prompt,
                min_height=rx.breakpoints(initial="8rem", md="10rem"),
                width="100%",
            ),
            _execution_controls(),
            _upload_panel(),
            _estimate_panel(),
            _primary_run_button(),
            rx.cond(
                HostState.status_message != "",
                rx.text(HostState.status_message, overflow_wrap="anywhere"),
            ),
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
            spacing=rx.breakpoints(initial="2", sm="3"),
        ),
        "composer",
    )


def _workspace_result_zone() -> rx.Component:
    return _workspace_zone_card(
        rx.vstack(
            rx.heading(
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
                size="4",
                color=HostState.active_primary,
            ),
            rx.cond(
                HostState.final_answer != "",
                rx.card(
                    rx.vstack(
                        rx.heading("Final answer", size="4"),
                        rx.text(
                            HostState.final_answer,
                            white_space="pre-wrap",
                            overflow_wrap="anywhere",
                            line_height="1.65",
                        ),
                        align="start",
                        width="100%",
                        spacing="2",
                    ),
                    width="100%",
                    min_width="0",
                ),
                rx.text("No result yet.", size="2"),
            ),
            _deliberation_panel(),
            width="100%",
            spacing=rx.breakpoints(initial="2", sm="3"),
        ),
        "result",
    )


def _workspace_history_zone() -> rx.Component:
    return _workspace_zone_card(_history_panel(), "history")


def _workspace_header() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.vstack(
                rx.heading("MultiMind", size="6", color=HostState.active_primary),
                rx.hstack(
                    rx.text("@", HostState.display_username, size="2"),
                    rx.badge(HostState.active_archetype, variant="soft"),
                    wrap="wrap",
                    spacing="2",
                ),
                rx.cond(
                    HostState.active_dna_mode == "canonical",
                    rx.text(
                        HostState.active_canonical_display_name,
                        " · ",
                        HostState.active_canonical_reference_id,
                        size="2",
                        overflow_wrap="anywhere",
                    ),
                    rx.text(
                        HostState.active_identity_display_name,
                        " + ",
                        HostState.active_web_display_name,
                        size="2",
                        overflow_wrap="anywhere",
                    ),
                ),
                align="start",
                spacing="1",
                min_width="0",
                flex="1",
            ),
            rx.hstack(
                rx.badge(rx.cond(HostState.busy, "BUSY", "READY")),
                rx.button(
                    "Theme Studio",
                    on_click=HostState.open_theme_studio,
                    variant="soft",
                    color=HostState.active_accent,
                    min_height="2.6rem",
                ),
                wrap="wrap",
                spacing="2",
            ),
            width="100%",
            align="center",
            justify="between",
            wrap="wrap",
            gap="0.75rem",
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
        padding=rx.breakpoints(initial="0.75rem", md="1rem"),
    )


def _workspace() -> rx.Component:
    # The four real semantic zones are instantiated exactly once. Archetype and
    # canonical DNA change only presentation composition; application/provider/
    # persistence truth remains behind the same event and application paths.
    return rx.container(
        rx.vstack(
            _workspace_header(),
            rx.grid(
                _workspace_utility_zone(),
                _workspace_composer_zone(),
                _workspace_result_zone(),
                _workspace_history_zone(),
                grid_template_columns=rx.breakpoints(
                    initial="minmax(0, 1fr)",
                    lg=rx.cond(
                        HostState.active_dna_mode == "canonical",
                        _canonical_workspace_desktop_columns(),
                        _workspace_desktop_columns(),
                    ),
                ),
                grid_template_areas=rx.breakpoints(
                    initial=rx.cond(
                        HostState.active_dna_mode == "canonical",
                        _canonical_workspace_mobile_areas(),
                        _workspace_mobile_areas(),
                    ),
                    lg=rx.cond(
                        HostState.active_dna_mode == "canonical",
                        _canonical_workspace_desktop_areas(),
                        _workspace_desktop_areas(),
                    ),
                ),
                gap=rx.cond(
                    HostState.active_dna_mode == "canonical",
                    HostState.active_canonical_gap,
                    "1rem",
                ),
                width="100%",
                align_items="start",
            ),
            width="100%",
            spacing=rx.breakpoints(initial="3", md="4"),
        ),
        max_width=rx.cond(
            HostState.active_archetype == "minimal_saas",
            "68rem",
            rx.cond(HostState.active_archetype == "terminal_hacker", "76rem", "88rem"),
        ),
        padding=rx.breakpoints(initial="0.5rem", sm="1rem", md="1.5rem"),
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
    )


def _authenticated_surface() -> rx.Component:
    return rx.cond(HostState.current_surface == "theme", _theme_studio(), _workspace())


def index() -> rx.Component:
    return rx.cond(HostState.logged_in, _authenticated_surface(), _login_panel())


app = rx.App()
app.add_page(index, title="MultiMind AI — Reflex Host")
