"""Minimal RJ-2 Reflex production host surface."""

import reflex as rx

from multimind_reflex.state import HostState


UPLOAD_ID = "rj2_upload"


def _login_panel() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("MultiMind AI", size="7"),
                rx.text("Reflex production host — RJ-2 spine"),
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


def _session_panel() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Sessions", size="5"),
            rx.spacer(),
            rx.button("Logout", on_click=HostState.logout, variant="soft"),
            width="100%",
            align="center",
        ),
        rx.hstack(
            rx.input(
                placeholder="New session",
                value=HostState.new_session_name,
                on_change=HostState.set_new_session_name,
                width="100%",
            ),
            rx.button("Create", on_click=HostState.create_session),
            width="100%",
        ),
        rx.foreach(
            HostState.sessions,
            lambda session: rx.button(
                session["name"],
                on_click=HostState.select_session(session["id"]),
                width="100%",
                variant="soft",
            ),
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


def _workspace() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("MultiMind Reflex Host", size="7"),
                    rx.text("Logged in as ", HostState.display_username),
                    align="start",
                ),
                rx.spacer(),
                rx.badge(rx.cond(HostState.busy, "BUSY", "READY")),
                width="100%",
                align="center",
            ),
            rx.grid(
                rx.card(_session_panel()),
                rx.card(
                    rx.vstack(
                        rx.heading(
                            rx.cond(
                                HostState.current_session_name != "",
                                HostState.current_session_name,
                                "Select a session",
                            ),
                            size="5",
                        ),
                        rx.text_area(
                            placeholder="Prompt",
                            value=HostState.prompt,
                            on_change=HostState.set_prompt,
                            min_height="9rem",
                            width="100%",
                        ),
                        _upload_panel(),
                        rx.button(
                            rx.cond(HostState.busy, "Running…", "Run"),
                            on_click=HostState.run_chat,
                            disabled=HostState.busy,
                            width="100%",
                            size="3",
                        ),
                        rx.cond(
                            HostState.status_message != "",
                            rx.text(HostState.status_message),
                        ),
                        rx.cond(
                            HostState.error_message != "",
                            rx.callout(HostState.error_message, icon="triangle_alert"),
                        ),
                        rx.foreach(
                            HostState.warnings,
                            lambda warning: rx.callout(warning, icon="info"),
                        ),
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
                columns=rx.breakpoints(initial="1", md="3fr 7fr"),
                spacing="4",
                width="100%",
            ),
            width="100%",
            spacing="4",
        ),
        max_width="80rem",
        padding="1.5rem",
    )


def index() -> rx.Component:
    return rx.cond(HostState.logged_in, _workspace(), _login_panel())


app = rx.App()
app.add_page(index, title="MultiMind AI — Reflex Host")
