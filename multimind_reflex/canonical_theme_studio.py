"""Canonical Design-DNA EQ4 proving panel for the Reflex host.

One generic semantic fixture consumes typed host-realization scalars. The panel
shows all canonical references for discovery while clearly distinguishing the
bounded M2 proving slice from references whose host realization is still
pending. No reference ID/name branch exists in the renderer.
"""
from __future__ import annotations

import reflex as rx

from multimind_reflex.canonical_dna_state import CanonicalDnaState


def _catalog_row(option) -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.vstack(
                rx.text(option["display_name"], weight="bold", text_align="left"),
                rx.text(option["id"], size="1", text_align="left"),
                rx.text(option["category"], size="1", text_align="left"),
                align="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.badge(option["status"], variant="soft"),
            width="100%",
            align="center",
        ),
        on_click=CanonicalDnaState.select_reference(option["id"]),
        variant="soft",
        width="100%",
        height="auto",
        padding="0.7rem",
    )


def _semantic_card(title: str, body: str, *, alternate: bool = False, offset: bool = False) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(
                title,
                font_size=CanonicalDnaState.heading_size,
                font_weight=CanonicalDnaState.heading_weight,
                letter_spacing=CanonicalDnaState.heading_tracking,
            ),
            rx.text(body, color=CanonicalDnaState.text_muted, line_height=CanonicalDnaState.line_height),
            rx.badge("semantic content unchanged", variant="soft"),
            align="start",
            spacing="2",
            width="100%",
        ),
        width="100%",
        background_color=CanonicalDnaState.surface_alt if alternate else CanonicalDnaState.surface,
        color=CanonicalDnaState.text_color,
        border=f"1px solid {CanonicalDnaState.border}",
        border_left=CanonicalDnaState.continuity_border,
        border_radius=CanonicalDnaState.card_radius,
        padding=CanonicalDnaState.card_padding,
        transform=CanonicalDnaState.secondary_offset if offset else "none",
        transition=CanonicalDnaState.transition,
        _hover={"transform": CanonicalDnaState.hover_transform},
    )


def _canonical_fixture() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Primary context",
                        font_size=CanonicalDnaState.heading_size,
                        font_weight=CanonicalDnaState.heading_weight,
                        letter_spacing=CanonicalDnaState.heading_tracking,
                    ),
                    rx.text(
                        "One fixed semantic fixture is projected through every proving reference.",
                        color=CanonicalDnaState.text_muted,
                    ),
                    align="start",
                ),
                rx.spacer(),
                rx.badge(CanonicalDnaState.layout_flow),
                rx.badge(CanonicalDnaState.balance, variant="soft"),
                wrap="wrap",
                width="100%",
            ),
            rx.grid(
                _semantic_card(
                    "Work surface",
                    "Stable prompt, history, and result meaning. DNA may change hierarchy and grouping, never the application truth.",
                ),
                _semantic_card(
                    "Primary action",
                    "The same action remains discoverable and semantically primary across every reference.",
                    alternate=True,
                    offset=True,
                ),
                _semantic_card(
                    "System state",
                    "Loading, success, warning, and failure meaning remain explicit while presentation structure changes.",
                    alternate=True,
                ),
                _semantic_card(
                    "Auxiliary context",
                    "Metadata remains available without replacing the primary work surface or reading sanctuary.",
                    offset=True,
                ),
                grid_template_columns=rx.breakpoints(
                    initial="1fr",
                    md=CanonicalDnaState.desktop_columns,
                ),
                gap=CanonicalDnaState.gap,
                width="100%",
            ),
            rx.hstack(
                rx.badge("density: ", CanonicalDnaState.density, variant="soft"),
                rx.badge("hierarchy: ", CanonicalDnaState.hierarchy, variant="soft"),
                rx.badge("continuity: ", CanonicalDnaState.continuity, variant="soft"),
                rx.badge("motion: ", CanonicalDnaState.motion, variant="soft"),
                rx.badge("type: ", CanonicalDnaState.typography, variant="soft"),
                wrap="wrap",
            ),
            rx.text(
                "Mobile strategy: ",
                CanonicalDnaState.mobile_strategy,
                " · canonical viewport: ",
                CanonicalDnaState.preview_viewport,
                size="2",
                color=CanonicalDnaState.text_muted,
            ),
            width="100%",
            spacing="4",
        ),
        width="100%",
        background_color=CanonicalDnaState.background,
        color=CanonicalDnaState.text_color,
        font_family=CanonicalDnaState.font_family,
        border=f"1px solid {CanonicalDnaState.border}",
        border_radius=CanonicalDnaState.card_radius,
        padding=CanonicalDnaState.card_padding,
    )


def canonical_theme_studio_panel() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Canonical Design-DNA · EQ4 proving", size="5"),
                    rx.text(
                        "Canonical catalog is complete; host realization is deliberately graduated by evidence.",
                        size="2",
                    ),
                    align="start",
                ),
                rx.spacer(),
                rx.badge("Asset-off first", variant="soft"),
                wrap="wrap",
                width="100%",
            ),
            rx.hstack(
                rx.text("References: ", CanonicalDnaState.catalog_total, size="2"),
                rx.text("Host proving-ready: ", CanonicalDnaState.proving_ready_total, size="2"),
                wrap="wrap",
            ),
            rx.input(
                placeholder="Search 160 canonical references by title, ID, family, or category…",
                value=CanonicalDnaState.query,
                on_change=CanonicalDnaState.set_query,
                width="100%",
            ),
            rx.box(
                rx.vstack(
                    rx.foreach(CanonicalDnaState.filtered_catalog, _catalog_row),
                    rx.cond(
                        CanonicalDnaState.filtered_catalog.length() == 0,
                        rx.text("No canonical reference matches this search.", size="2"),
                    ),
                    spacing="2",
                    width="100%",
                ),
                max_height="20rem",
                overflow_y="auto",
                width="100%",
            ),
            rx.separator(),
            rx.hstack(
                rx.vstack(
                    rx.text("Selected canonical reference", size="2", weight="bold"),
                    rx.text(CanonicalDnaState.selected_display_name),
                    rx.text(CanonicalDnaState.selected_reference_id, size="1"),
                    align="start",
                ),
                rx.spacer(),
                rx.badge(CanonicalDnaState.selected_status, variant="soft"),
                wrap="wrap",
                width="100%",
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("Canonical projection viewport", size="2"),
                    rx.select(
                        ["desktop", "mobile"],
                        value=CanonicalDnaState.preview_viewport,
                        on_change=CanonicalDnaState.set_preview_viewport,
                    ),
                    align="start",
                ),
                rx.checkbox(
                    "Reduced motion",
                    checked=CanonicalDnaState.reduced_motion,
                    on_change=CanonicalDnaState.set_reduced_motion,
                ),
                wrap="wrap",
                width="100%",
                align="end",
            ),
            rx.callout(CanonicalDnaState.preview_message, icon="info", width="100%"),
            rx.cond(
                CanonicalDnaState.plan_ready,
                rx.vstack(
                    _canonical_fixture(),
                    rx.hstack(
                        rx.text(
                            "Fingerprint: ",
                            CanonicalDnaState.fingerprint,
                            size="1",
                            color=CanonicalDnaState.text_muted,
                        ),
                        rx.text(
                            "Degraded mechanisms: ",
                            CanonicalDnaState.degraded_mechanism_count,
                            size="1",
                            color=CanonicalDnaState.text_muted,
                        ),
                        wrap="wrap",
                    ),
                    rx.hstack(
                        rx.badge(
                            rx.cond(CanonicalDnaState.accessibility_applied, "Accessibility veto applied", "Accessibility safe"),
                            variant="soft",
                        ),
                        rx.badge(
                            rx.cond(CanonicalDnaState.reading_sanctuary_applied, "Reading Sanctuary applied", "Reading-safe"),
                            variant="soft",
                        ),
                        rx.badge(
                            rx.cond(CanonicalDnaState.reduced_motion_applied, "Reduced motion applied", "Motion policy normal"),
                            variant="soft",
                        ),
                        wrap="wrap",
                    ),
                    rx.button(
                        "Apply canonical proving presentation",
                        on_click=CanonicalDnaState.apply_reference,
                        variant="solid",
                    ),
                    width="100%",
                    spacing="3",
                ),
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
    )


__all__ = ["canonical_theme_studio_panel"]
