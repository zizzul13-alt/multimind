"""Seven-archetype context proving panel for canonical Design-DNA.

Archetype chooses the semantic scaffold. Canonical DNA host vocabulary chooses
visual hierarchy/material-free presentation inside that scaffold. Neither path
owns application/session/provider/persistence truth and neither branches on a
Design-DNA reference ID.
"""
from __future__ import annotations

import reflex as rx

from multimind_reflex.canonical_dna_state import CanonicalDnaState


def _context_card(title, body, *, emphasis: str = "normal") -> rx.Component:
    border_width = rx.cond(emphasis == "primary", "3px", "1px")
    return rx.box(
        rx.vstack(
            rx.text(
                title,
                font_size=rx.cond(emphasis == "primary", "1.45rem", CanonicalDnaState.heading_size),
                font_weight=rx.cond(emphasis == "primary", "800", CanonicalDnaState.heading_weight),
                letter_spacing=CanonicalDnaState.heading_tracking,
            ),
            rx.text(body, color=CanonicalDnaState.text_muted, line_height=CanonicalDnaState.line_height),
            align="start",
            spacing="2",
            width="100%",
        ),
        width="100%",
        background_color=rx.cond(emphasis == "secondary", CanonicalDnaState.surface_alt, CanonicalDnaState.surface),
        border=f"{border_width} solid {CanonicalDnaState.border}",
        border_left=rx.cond(
            CanonicalDnaState.continuity_border != "0px solid transparent",
            CanonicalDnaState.continuity_border,
            f"{border_width} solid {CanonicalDnaState.border}",
        ),
        border_radius=CanonicalDnaState.card_radius,
        padding=CanonicalDnaState.card_padding,
        transition=CanonicalDnaState.transition,
        _hover={"transform": CanonicalDnaState.hover_transform},
    )


def _work() -> rx.Component:
    return _context_card(CanonicalDnaState.work_title, CanonicalDnaState.work_body, emphasis="primary")


def _action() -> rx.Component:
    return _context_card(CanonicalDnaState.action_title, CanonicalDnaState.action_body, emphasis="primary")


def _state() -> rx.Component:
    return _context_card(CanonicalDnaState.state_title, CanonicalDnaState.state_body, emphasis="secondary")


def _aux() -> rx.Component:
    return _context_card(CanonicalDnaState.auxiliary_title, CanonicalDnaState.auxiliary_body, emphasis="secondary")


def _chat_first() -> rx.Component:
    return rx.vstack(
        _work(),
        rx.hstack(_state(), _aux(), width="100%", align="stretch", spacing="2"),
        _action(),
        width="100%",
        spacing="3",
    )


def _command_center() -> rx.Component:
    return rx.vstack(
        rx.grid(_state(), _aux(), grid_template_columns="repeat(2, minmax(0, 1fr))", gap=CanonicalDnaState.gap, width="100%"),
        _work(),
        _action(),
        width="100%",
        spacing="3",
    )


def _ai_workspace() -> rx.Component:
    return rx.grid(
        _work(),
        rx.vstack(_aux(), _state(), _action(), width="100%", spacing="2"),
        grid_template_columns=rx.cond(CanonicalDnaState.preview_viewport == "desktop", "minmax(0, 1.45fr) minmax(0, 0.8fr)", "1fr"),
        gap=CanonicalDnaState.group_gap,
        width="100%",
        align_items="start",
    )


def _research_lab() -> rx.Component:
    return rx.vstack(
        _work(),
        rx.box(
            rx.vstack(_aux(), _state(), width="100%", spacing="2"),
            width="94%",
            margin_left="6%",
            border_left=f"4px solid {CanonicalDnaState.accent}",
            padding_left="0.75rem",
        ),
        _action(),
        width="100%",
        spacing="3",
    )


def _agent_canvas() -> rx.Component:
    def node(label: str, child: rx.Component) -> rx.Component:
        return rx.hstack(
            rx.badge(label, variant="solid"),
            rx.box(child, width="calc(100% - 3rem)"),
            width="100%",
            align="start",
            spacing="2",
        )

    return rx.vstack(
        node("01", _work()),
        node("02", _aux()),
        node("03", _state()),
        node("04", _action()),
        width="100%",
        spacing="2",
        border_left=f"3px dashed {CanonicalDnaState.accent}",
        padding_left="0.5rem",
    )


def _terminal_hacker() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(rx.text("$", weight="bold"), rx.text(CanonicalDnaState.action_title, weight="bold"), width="100%"),
            _action(),
            rx.hstack(rx.text("→", weight="bold"), rx.text("execution", weight="bold"), width="100%"),
            _state(),
            rx.hstack(rx.text("▣", weight="bold"), rx.text("output", weight="bold"), width="100%"),
            _work(),
            _aux(),
            width="100%",
            spacing="2",
        ),
        width="100%",
        background_color=CanonicalDnaState.surface,
        border=f"2px solid {CanonicalDnaState.accent}",
        border_radius=CanonicalDnaState.group_radius,
        padding=CanonicalDnaState.group_padding,
    )


def _minimal_saas() -> rx.Component:
    return rx.vstack(
        rx.box(_work(), max_width="46rem", width="100%", margin="0 auto"),
        rx.box(_action(), max_width="34rem", width="100%", margin="0 auto"),
        rx.box(_state(), max_width="40rem", width="100%", margin="0 auto"),
        rx.box(_aux(), max_width="40rem", width="100%", margin="0 auto", opacity="0.82"),
        width="100%",
        spacing="3",
    )


def _archetype_fixture() -> rx.Component:
    return rx.cond(
        CanonicalDnaState.preview_archetype == "chat_first",
        _chat_first(),
        rx.cond(
            CanonicalDnaState.preview_archetype == "command_center",
            _command_center(),
            rx.cond(
                CanonicalDnaState.preview_archetype == "ai_workspace",
                _ai_workspace(),
                rx.cond(
                    CanonicalDnaState.preview_archetype == "ai_research_lab",
                    _research_lab(),
                    rx.cond(
                        CanonicalDnaState.preview_archetype == "agent_canvas",
                        _agent_canvas(),
                        rx.cond(
                            CanonicalDnaState.preview_archetype == "terminal_hacker",
                            _terminal_hacker(),
                            _minimal_saas(),
                        ),
                    ),
                ),
            ),
        ),
    )


def canonical_archetype_context_panel() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Archetype context proving", size="5"),
                    rx.text(
                        "Same canonical DNA, seven accepted MultiMind presentation contexts. Archetype changes meaning hierarchy; DNA changes presentation character.",
                        size="2",
                    ),
                    align="start",
                ),
                rx.spacer(),
                rx.badge("ISOLATED · NO APP TRUTH", variant="soft"),
                width="100%",
                wrap="wrap",
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("Presentation archetype", size="2", weight="bold"),
                    rx.select(
                        CanonicalDnaState.archetype_choices,
                        value=CanonicalDnaState.preview_archetype,
                        on_change=CanonicalDnaState.set_preview_archetype,
                        width="100%",
                    ),
                    align="start",
                    min_width="15rem",
                ),
                rx.vstack(
                    rx.text("Primary object", size="2", weight="bold"),
                    rx.badge(CanonicalDnaState.context_primary_object, variant="outline"),
                    align="start",
                ),
                wrap="wrap",
                width="100%",
                align="end",
            ),
            rx.cond(
                CanonicalDnaState.plan_ready,
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.vstack(
                                rx.heading(CanonicalDnaState.context_title, size="5"),
                                rx.text(CanonicalDnaState.context_body, color=CanonicalDnaState.text_muted),
                                align="start",
                            ),
                            rx.spacer(),
                            rx.badge(CanonicalDnaState.context_display_name),
                            rx.badge(CanonicalDnaState.layout_flow, variant="soft"),
                            rx.badge(CanonicalDnaState.mobile_strategy, variant="soft"),
                            wrap="wrap",
                            width="100%",
                        ),
                        _archetype_fixture(),
                        rx.text(
                            "Archetype: ", CanonicalDnaState.preview_archetype,
                            " · DNA: ", CanonicalDnaState.selected_display_name,
                            " · viewport: ", CanonicalDnaState.preview_viewport,
                            size="1", color=CanonicalDnaState.text_muted,
                        ),
                        width="100%",
                        spacing="4",
                    ),
                    width="100%",
                    background_color=CanonicalDnaState.background,
                    color=CanonicalDnaState.text_color,
                    font_family=CanonicalDnaState.font_family,
                    border=f"1px solid {CanonicalDnaState.border}",
                    border_radius=CanonicalDnaState.group_radius,
                    padding=CanonicalDnaState.group_padding,
                    overflow_x="auto",
                ),
                rx.callout("Select a host-realization-ready DNA above first.", icon="info", width="100%"),
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
    )


__all__ = ["canonical_archetype_context_panel"]
