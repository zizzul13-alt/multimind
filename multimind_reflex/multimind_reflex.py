"""RJ-3 Reflex production presentation surface."""

import reflex as rx

from multimind_reflex.state import AGENT_OPTIONS, ARCHETYPES, SKILL_OPTIONS, TEMPLATE_OPTIONS, HostState


UPLOAD_ID = "rj3_upload"
RESTORE_ID = "rj3_restore"
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
                rx.button("Login", on_click=HostState.login, width="100%"),
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
            rx.hstack(
                rx.vstack(
                    rx.heading("Theme Studio", size="7"),
                    rx.text("Draft → preview → explicit Apply → workspace"),
                    align="start",
                ),
                rx.spacer(),
                rx.badge(HostState.theme_status),
                width="100%",
                align="center",
            ),
            rx.callout(
                rx.cond(
                    HostState.dna_runtime_available,
                    "Private Design-DNA is available server-side.",
                    "Private Design-DNA unavailable; safe neutral presentation remains operational.",
                ),
                icon="info",
                width="100%",
            ),
            rx.grid(
                rx.card(
                    rx.vstack(
                        rx.heading("Composition draft", size="5"),
                        rx.text("Archetype"),
                        rx.select(
                            ARCHETYPES,
                            value=HostState.draft_archetype,
                            on_change=HostState.set_draft_archetype,
                            width="100%",
                        ),
                        rx.text("Identity / Cultural DNA reference"),
                        rx.input(
                            placeholder="Optional private DNA reference",
                            value=HostState.draft_identity_dna,
                            on_change=HostState.set_draft_identity_dna,
                            width="100%",
                        ),
                        rx.text("Web / Information DNA reference"),
                        rx.input(
                            placeholder="Optional private DNA reference",
                            value=HostState.draft_web_dna,
                            on_change=HostState.set_draft_web_dna,
                            width="100%",
                        ),
                        rx.text("Density"),
                        rx.select(
                            ["compact", "comfortable", "spacious"],
                            value=HostState.draft_density,
                            on_change=HostState.set_draft_density,
                            width="100%",
                        ),
                        rx.text("Radius"),
                        rx.select(
                            ["none", "small", "medium", "large"],
                            value=HostState.draft_radius,
                            on_change=HostState.set_draft_radius,
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    )
                ),
                rx.card(
                    rx.vstack(
                        rx.heading("Live preview contract", size="5"),
                        rx.text("Archetype: ", HostState.draft_archetype),
                        rx.text("Identity: ", rx.cond(HostState.draft_identity_dna != "", HostState.draft_identity_dna, "neutral")),
                        rx.text("Web DNA: ", rx.cond(HostState.draft_web_dna != "", HostState.draft_web_dna, "neutral")),
                        rx.text("Density: ", HostState.draft_density),
                        rx.text("Radius: ", HostState.draft_radius),
                        rx.separator(),
                        rx.heading("MultiMind", size="6"),
                        rx.text("Application semantics stay unchanged while presentation composition changes."),
                        rx.button("Example action", variant="soft"),
                        spacing="3",
                        width="100%",
                    )
                ),
                columns=rx.breakpoints(initial="1", md="1fr 1fr"),
                spacing="4",
                width="100%",
            ),
            rx.hstack(
                rx.button("Apply Composition", on_click=HostState.apply_theme, size="3"),
                rx.button("Discard", on_click=HostState.discard_theme, variant="soft"),
                rx.button("Reset", on_click=HostState.reset_theme, variant="ghost"),
                rx.cond(
                    HostState.current_session_id != "",
                    rx.button("Back to workspace", on_click=HostState.return_to_workspace, variant="outline"),
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
        max_width="72rem",
        padding="1.5rem",
    )


def _session_panel() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Sessions", size="5"),
            rx.spacer(),
            rx.button("Logout", on_click=HostState.logout, variant="soft"),
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
        rx.button("Create session", on_click=HostState.create_session, width="100%"),
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
                rx.button("Use preview as editable prompt", on_click=HostState.use_template_preview, variant="soft"),
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
            ),
            rx.button(
                "Clear",
                on_click=[HostState.clear_uploads, rx.clear_selected_files(UPLOAD_ID)],
                variant="ghost",
            ),
        ),
        rx.cond(
            HostState.upload_names.length() > 0,
            rx.text("Staged: ", HostState.upload_names.to_string()),
        ),
        width="100%",
        spacing="2",
    )


def _estimate_panel() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Pre-send estimate", size="3"),
            rx.hstack(
                rx.text("Prompt: ", HostState.estimated_prompt_tokens, " tok"),
                rx.text("Files: ", HostState.estimated_file_tokens, " tok"),
                rx.text("Total: ", HostState.estimated_total_tokens, " tok"),
                rx.text("Cost: $", HostState.estimated_cost),
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


def _history_panel() -> rx.Component:
    return rx.vstack(
        rx.heading("Session history", size="4"),
        rx.foreach(
            HostState.history,
            lambda row: rx.card(
                rx.vstack(
                    rx.text(row["prompt"], weight="bold", white_space="pre-wrap"),
                    rx.text(row["final_answer"], white_space="pre-wrap"),
                    align="start",
                    width="100%",
                ),
                width="100%",
            ),
        ),
        width="100%",
        spacing="2",
    )


def _data_ops() -> rx.Component:
    return rx.vstack(
        rx.heading("Backup / Restore", size="4"),
        rx.button("Export SQLite backup", on_click=HostState.export_database, variant="soft"),
        rx.upload(
            rx.text("Select one SQLite backup"),
            id=RESTORE_ID,
            multiple=False,
            width="100%",
            border="1px dashed var(--gray-a8)",
            padding="0.75rem",
        ),
        rx.hstack(
            rx.button(
                "Stage restore",
                on_click=HostState.stage_restore(rx.upload_files(upload_id=RESTORE_ID)),
                variant="soft",
            ),
            rx.button("Restore safely", on_click=HostState.restore_database, variant="outline"),
        ),
        rx.cond(HostState.restore_name != "", rx.text("Staged: ", HostState.restore_name)),
        width="100%",
        spacing="2",
    )


def _workspace() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("MultiMind", size="7"),
                    rx.text("Logged in as ", HostState.display_username),
                    rx.text("Archetype: ", HostState.active_archetype, size="2"),
                    align="start",
                ),
                rx.spacer(),
                rx.badge(rx.cond(HostState.busy, "BUSY", "READY")),
                rx.button("Theme Studio", on_click=HostState.open_theme_studio, variant="soft"),
                width="100%",
                align="center",
                wrap="wrap",
            ),
            rx.grid(
                rx.card(
                    rx.vstack(
                        _session_panel(),
                        rx.separator(),
                        _data_ops(),
                        width="100%",
                        spacing="4",
                    )
                ),
                rx.vstack(
                    rx.card(
                        rx.vstack(
                            rx.heading(
                                rx.cond(
                                    HostState.current_session_name != "",
                                    HostState.current_session_name,
                                    "Select or create a session",
                                ),
                                size="5",
                            ),
                            _template_panel(),
                            rx.text_area(
                                placeholder="Prompt",
                                value=HostState.prompt,
                                on_change=HostState.set_prompt,
                                min_height="10rem",
                                width="100%",
                            ),
                            _execution_controls(),
                            _upload_panel(),
                            _estimate_panel(),
                            rx.button(
                                rx.cond(HostState.busy, "Running…", "Run"),
                                on_click=HostState.run_chat,
                                disabled=HostState.busy,
                                width="100%",
                                size="3",
                            ),
                            rx.cond(HostState.status_message != "", rx.text(HostState.status_message)),
                            rx.cond(
                                HostState.error_message != "",
                                rx.callout(HostState.error_message, icon="triangle_alert", width="100%"),
                            ),
                            rx.cond(
                                HostState.success_message != "",
                                rx.callout(HostState.success_message, icon="circle_check", width="100%"),
                            ),
                            rx.foreach(HostState.warnings, lambda warning: rx.callout(warning, icon="info", width="100%")),
                            rx.cond(
                                HostState.final_answer != "",
                                rx.card(
                                    rx.vstack(
                                        rx.heading("Final answer", size="4"),
                                        rx.text(HostState.final_answer, white_space="pre-wrap"),
                                        align="start",
                                    ),
                                    width="100%",
                                ),
                            ),
                            width="100%",
                            spacing="3",
                        )
                    ),
                    rx.card(_history_panel()),
                    width="100%",
                    spacing="4",
                ),
                columns=rx.breakpoints(initial="1", lg="3fr 7fr"),
                spacing="4",
                width="100%",
            ),
            width="100%",
            spacing="4",
        ),
        max_width="88rem",
        padding=rx.breakpoints(initial="0.75rem", sm="1rem", md="1.5rem"),
    )


def _authenticated_surface() -> rx.Component:
    return rx.cond(HostState.current_surface == "theme", _theme_studio(), _workspace())


def index() -> rx.Component:
    return rx.cond(HostState.logged_in, _authenticated_surface(), _login_panel())


app = rx.App()
app.add_page(index, title="MultiMind AI — Reflex Host")
