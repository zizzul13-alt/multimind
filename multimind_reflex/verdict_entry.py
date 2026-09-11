"""Persistent user-verdict presentation wiring for the accepted Reflex app.

This module patches presentation globals on the existing workspace module. It
never creates a second ``rx.App`` and never owns application/persistence truth.
The production ``mobile_entry`` remains the accepted host entry and imports this
module only to install the bounded verdict-aware presentation extension.
"""
from __future__ import annotations

import reflex as rx

import multimind_reflex.multimind_reflex as workspace
from multimind_reflex.verdict_state import VerdictHostState


# Existing workspace functions resolve these module globals when Reflex renders
# the registered page. Bind them to the verdict-aware state without cloning the
# workspace or moving business logic into presentation.
workspace.HostState = VerdictHostState


def _participant_card(participant) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(participant["participant_id"], weight="bold"),
                rx.badge(participant["status"]),
                rx.cond(
                    VerdictHostState.current_user_verdict == participant["participant_id"],
                    rx.badge("MY WINNER", variant="solid"),
                ),
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
            rx.cond(
                participant["status"] == "success",
                rx.cond(
                    VerdictHostState.current_user_verdict == participant["participant_id"],
                    rx.button(
                        "Clear my winner",
                        on_click=VerdictHostState.clear_current_user_verdict,
                        variant="outline",
                        size="2",
                        class_name="mm-touch-target",
                    ),
                    rx.button(
                        "My winner",
                        on_click=VerdictHostState.set_current_user_verdict(participant["participant_id"]),
                        variant="soft",
                        size="2",
                        class_name="mm-touch-target",
                    ),
                ),
            ),
            align="start",
            width="100%",
        ),
        width="100%",
        class_name="mm-participant-card",
    )


def _history_panel() -> rx.Component:
    return rx.vstack(
        rx.heading("Session history", size="4"),
        rx.foreach(
            VerdictHostState.history,
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
                    rx.cond(
                        row["user_verdict"] != "",
                        rx.text("Your winner: ", row["user_verdict"], size="2", weight="bold"),
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


workspace._participant_card = _participant_card
workspace._history_panel = _history_panel
app = workspace.app

__all__ = ["app"]
