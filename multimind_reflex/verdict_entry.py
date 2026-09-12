"""Persistent user-verdict + AI-identity presentation wiring for Reflex.

The accepted workspace remains the single rendering implementation. This module
binds it to identity-aware state and keeps provider/model route detail secondary.
Application/persistence truth remains behind MultiMindApplication.
"""
from __future__ import annotations

import reflex as rx

import multimind_reflex.multimind_reflex as workspace
from core.ai_identity import AI_IDENTITY_LABELS, AI_IDENTITY_OPTIONS
from multimind_reflex.identity_state import IdentityVerdictHostState


HostState = IdentityVerdictHostState
workspace.HostState = HostState
workspace.AGENT_OPTIONS = list(AI_IDENTITY_OPTIONS)


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
        rx.text("AI participants", size="2", weight="bold"),
        rx.hstack(
            *[
                rx.checkbox(
                    AI_IDENTITY_LABELS[identity_id],
                    checked=HostState.active_agents.contains(identity_id),
                    on_change=lambda enabled, identity_id=identity_id: HostState.set_agent_enabled(identity_id, enabled),
                )
                for identity_id in AI_IDENTITY_OPTIONS
            ],
            wrap="wrap",
            width="100%",
        ),
        rx.text(
            "Infrastructure routes are resolved automatically. Route/model details remain visible in result provenance.",
            size="1",
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
                    workspace.SKILL_OPTIONS,
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


def _participant_card(participant) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(
                    rx.cond(
                        participant["effective_identity_label"] != "",
                        participant["effective_identity_label"],
                        rx.cond(
                            participant["requested_identity_label"] != "",
                            participant["requested_identity_label"],
                            participant["participant_id"],
                        ),
                    ),
                    weight="bold",
                ),
                rx.badge(participant["status"]),
                rx.cond(
                    HostState.current_user_verdict == participant["participant_id"],
                    rx.badge("MY WINNER", variant="solid"),
                ),
                wrap="wrap",
            ),
            rx.cond(
                participant["requested_identity_label"] != "",
                rx.text("Requested AI: ", participant["requested_identity_label"], size="2"),
            ),
            rx.cond(
                participant["effective_identity_label"] != "",
                rx.text("Effective AI: ", participant["effective_identity_label"], size="2", weight="bold"),
            ),
            rx.cond(
                participant["identity_route_fallback"],
                rx.callout("Same-AI route fallback was used.", icon="info", width="100%"),
            ),
            rx.cond(
                participant["model"] != "",
                rx.text("Model: ", participant["model"], size="2"),
            ),
            rx.cond(
                participant["route_provider"] != "",
                rx.text("Route: ", participant["route_provider"], size="2"),
            ),
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
                    HostState.current_user_verdict == participant["participant_id"],
                    rx.button(
                        "Clear my winner",
                        on_click=HostState.clear_current_user_verdict,
                        variant="outline",
                        size="2",
                        class_name="mm-touch-target",
                    ),
                    rx.button(
                        "My winner",
                        on_click=HostState.set_current_user_verdict(participant["participant_id"]),
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
            HostState.history,
            lambda row: rx.card(
                rx.vstack(
                    rx.text(row["prompt"], weight="bold", white_space="pre-wrap", class_name="mm-readable"),
                    rx.text(row["final_answer"], white_space="pre-wrap", class_name="mm-readable"),
                    rx.cond(
                        row["participant_summary"] != "",
                        rx.text("AI participants: ", row["participant_summary"], size="2"),
                    ),
                    rx.cond(
                        row["judge_provider"] != "",
                        rx.text("Judge route: ", row["judge_provider"], size="2"),
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


workspace._execution_controls = _execution_controls
workspace._participant_card = _participant_card
workspace._history_panel = _history_panel
app = workspace.app

__all__ = ["app"]
