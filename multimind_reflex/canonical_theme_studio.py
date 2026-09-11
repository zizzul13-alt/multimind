"""Canonical Design-DNA EQ4 proving panel for the Reflex host.

The renderer consumes finite host-realization vocabulary only. Reference IDs,
titles, families, and private directive prose never choose layout branches.
Desktop composition follows ``layout_flow``; mobile composition follows the
canonical ``mobile_strategy`` instead of merely collapsing desktop columns.
"""
from __future__ import annotations

import reflex as rx

from multimind_reflex.canonical_dna_state import CanonicalDnaState


def _catalog_row(option) -> rx.Component:
    return rx.button(
        rx.flex(
            rx.vstack(
                rx.text(
                    option["display_name"],
                    weight="bold",
                    text_align="left",
                    overflow_wrap="normal",
                ),
                rx.text(option["id"], size="1", text_align="left"),
                rx.text(option["category"], size="1", text_align="left"),
                align="start",
                spacing="1",
                min_width="12rem",
                flex="1 1 12rem",
            ),
            rx.badge(option["status"], variant="soft", flex_shrink="0"),
            width="100%",
            align="center",
            justify="between",
            gap="0.5rem",
            wrap="wrap",
        ),
        on_click=CanonicalDnaState.select_reference(option["id"]),
        variant="soft",
        width="100%",
        height="auto",
        padding="0.7rem",
    )


def _semantic_card(title: str, body: str, *, alternate: bool = False, secondary: bool = False) -> rx.Component:
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
        width=CanonicalDnaState.secondary_width if secondary else "100%",
        margin_left=CanonicalDnaState.secondary_inset if secondary else "0rem",
        background_color=CanonicalDnaState.surface_alt if alternate else CanonicalDnaState.surface,
        color=CanonicalDnaState.text_color,
        border=f"1px solid {CanonicalDnaState.border}",
        border_left=CanonicalDnaState.continuity_border,
        border_radius=CanonicalDnaState.card_radius,
        padding=CanonicalDnaState.card_padding,
        transform=CanonicalDnaState.secondary_offset if secondary else "none",
        transition=CanonicalDnaState.transition,
        _hover={"transform": CanonicalDnaState.hover_transform},
    )


def _semantic_section(title: str, body: str, *, alternate: bool = False) -> rx.Component:
    """Semantic content without card chrome for continuous mobile grammars."""
    return rx.vstack(
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
        padding=CanonicalDnaState.card_padding,
        background_color=CanonicalDnaState.surface_alt if alternate else "transparent",
    )


def _work_surface() -> rx.Component:
    return _semantic_card(
        "Work surface",
        "Stable prompt, history, and result meaning. DNA may change hierarchy and grouping, never the application truth.",
    )


def _primary_action(*, secondary: bool = False) -> rx.Component:
    return _semantic_card(
        "Primary action",
        "The same action remains discoverable and semantically primary across every reference.",
        alternate=True,
        secondary=secondary,
    )


def _system_state(*, secondary: bool = False) -> rx.Component:
    return _semantic_card(
        "System state",
        "Loading, success, warning, and failure meaning remain explicit while presentation structure changes.",
        alternate=True,
        secondary=secondary,
    )


def _auxiliary_context(*, secondary: bool = False) -> rx.Component:
    return _semantic_card(
        "Auxiliary context",
        "Metadata remains available without replacing the primary work surface or reading sanctuary.",
        secondary=secondary,
    )


def _group(label: str, *children: rx.Component) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(label, size="1", weight="bold", text_transform="uppercase", letter_spacing="0.08em"),
            *children,
            width="100%",
            spacing="2",
        ),
        width="100%",
        border=f"1px solid {CanonicalDnaState.border}",
        border_radius=CanonicalDnaState.group_radius,
        padding=CanonicalDnaState.group_padding,
        background_color=CanonicalDnaState.surface,
    )


# ---------------------------------------------------------------------------
# Desktop host templates: controlled only by finite layout_flow vocabulary.
# ---------------------------------------------------------------------------


def _matrix_fixture() -> rx.Component:
    return rx.grid(
        _work_surface(),
        _primary_action(),
        _system_state(),
        _auxiliary_context(),
        grid_template_columns=CanonicalDnaState.desktop_columns,
        gap=CanonicalDnaState.gap,
        width="100%",
    )


def _component_hierarchy_fixture() -> rx.Component:
    return rx.vstack(
        _work_surface(),
        rx.grid(
            _primary_action(secondary=True),
            _system_state(secondary=True),
            _auxiliary_context(secondary=True),
            grid_template_columns=CanonicalDnaState.support_columns,
            gap=CanonicalDnaState.group_gap,
            width="100%",
        ),
        width="100%",
        spacing="4",
    )


def _group_bands_fixture() -> rx.Component:
    return rx.vstack(
        _group("Work context", _work_surface(), _auxiliary_context(secondary=True)),
        _group("Action and state", _primary_action(), _system_state(secondary=True)),
        width="100%",
        spacing="4",
    )


def _paired_blocks_fixture() -> rx.Component:
    return rx.grid(
        _group("Work pair", _work_surface(), _auxiliary_context()),
        _group("Action pair", _primary_action(), _system_state()),
        grid_template_columns=CanonicalDnaState.desktop_columns,
        gap=CanonicalDnaState.group_gap,
        width="100%",
    )


def _continuous_surface_fixture() -> rx.Component:
    return rx.box(
        rx.vstack(
            _semantic_section(
                "Work surface",
                "Stable prompt, history, and result meaning. DNA may change hierarchy and grouping, never the application truth.",
            ),
            rx.separator(),
            _semantic_section(
                "Primary action",
                "The same action remains discoverable and semantically primary across every reference.",
                alternate=True,
            ),
            rx.separator(),
            _semantic_section(
                "System state",
                "Loading, success, warning, and failure meaning remain explicit while presentation structure changes.",
                alternate=True,
            ),
            rx.separator(),
            _semantic_section(
                "Auxiliary context",
                "Metadata remains available without replacing the primary work surface or reading sanctuary.",
            ),
            width="100%",
            spacing="0",
        ),
        width="100%",
        padding=CanonicalDnaState.group_padding,
        border=f"1px solid {CanonicalDnaState.border}",
        border_radius=CanonicalDnaState.group_radius,
        background_color=CanonicalDnaState.surface,
    )


def _directional_path_fixture() -> rx.Component:
    return rx.vstack(
        _work_surface(),
        rx.box(_primary_action(), width="88%", margin_left="12%"),
        rx.box(_system_state(), width="88%"),
        rx.box(_auxiliary_context(), width="82%", margin_left="18%"),
        width="100%",
        spacing="3",
    )


def _trace_timeline_fixture() -> rx.Component:
    return rx.box(
        rx.vstack(
            _work_surface(),
            _primary_action(),
            _system_state(),
            _auxiliary_context(),
            width="100%",
            spacing="3",
        ),
        width="100%",
        border_left=f"5px solid {CanonicalDnaState.accent}",
        padding_left="1rem",
    )


def _desktop_structural_fixture() -> rx.Component:
    return rx.cond(
        CanonicalDnaState.fixture_template == "matrix",
        _matrix_fixture(),
        rx.cond(
            CanonicalDnaState.fixture_template == "component_hierarchy",
            _component_hierarchy_fixture(),
            rx.cond(
                CanonicalDnaState.fixture_template == "group_bands",
                _group_bands_fixture(),
                rx.cond(
                    CanonicalDnaState.fixture_template == "paired_blocks",
                    _paired_blocks_fixture(),
                    rx.cond(
                        CanonicalDnaState.fixture_template == "continuous_surface",
                        _continuous_surface_fixture(),
                        rx.cond(
                            CanonicalDnaState.fixture_template == "directional_path",
                            _directional_path_fixture(),
                            _trace_timeline_fixture(),
                        ),
                    ),
                ),
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Mobile host templates: controlled only by canonical mobile_strategy.
# These are not desktop templates with columns collapsed to 1fr.
# ---------------------------------------------------------------------------


def _mobile_marker(label: str) -> rx.Component:
    return rx.box(
        rx.text(label, size="1", weight="bold"),
        min_width="2rem",
        height="2rem",
        display="flex",
        align_items="center",
        justify_content="center",
        border=f"2px solid {CanonicalDnaState.accent}",
        border_radius="999px",
        background_color=CanonicalDnaState.surface,
    )


def _mobile_step(label: str, child: rx.Component) -> rx.Component:
    return rx.hstack(
        _mobile_marker(label),
        rx.box(child, width="calc(100% - 2.75rem)"),
        width="100%",
        align="start",
        spacing="2",
    )


def _mobile_ordered_flow() -> rx.Component:
    return rx.vstack(
        _mobile_step("1", _work_surface()),
        _mobile_step("2", _primary_action()),
        _mobile_step("3", _system_state()),
        _mobile_step("4", _auxiliary_context()),
        width="100%",
        spacing="3",
    )


def _mobile_component_reflow() -> rx.Component:
    return rx.vstack(
        _work_surface(),
        rx.box(
            rx.vstack(
                rx.text("Supporting components", size="1", weight="bold", text_transform="uppercase"),
                _primary_action(),
                _system_state(),
                _auxiliary_context(),
                width="100%",
                spacing="2",
            ),
            width="94%",
            margin_left="6%",
            border_left=f"5px solid {CanonicalDnaState.accent}",
            padding_left="0.75rem",
        ),
        width="100%",
        spacing="4",
    )


def _mobile_serial_groups() -> rx.Component:
    return rx.vstack(
        _group("01 · Work group", _work_surface(), _auxiliary_context()),
        _group("02 · Action group", _primary_action(), _system_state()),
        width="100%",
        spacing="3",
    )


def _mobile_serial_clusters() -> rx.Component:
    return rx.vstack(
        _group("Context cluster", _work_surface()),
        rx.box(_primary_action(), width="92%", margin_left="8%"),
        _group("Service state cluster", _system_state(), _auxiliary_context()),
        width="100%",
        spacing="3",
    )


def _mobile_stack_pairs() -> rx.Component:
    return rx.vstack(
        _group("Pair A", _work_surface(), _auxiliary_context()),
        rx.center(rx.text("↕", size="5", weight="bold"), width="100%"),
        _group("Pair B", _primary_action(), _system_state()),
        width="100%",
        spacing="2",
    )


def _mobile_ordered_asymmetry() -> rx.Component:
    return rx.vstack(
        rx.box(_work_surface(), width="94%"),
        rx.box(_primary_action(), width="88%", margin_left="12%"),
        rx.box(_system_state(), width="90%"),
        rx.box(_auxiliary_context(), width="84%", margin_left="16%"),
        width="100%",
        spacing="3",
    )


def _mobile_reduced_continuity() -> rx.Component:
    return rx.box(
        rx.vstack(
            _semantic_section(
                "Work surface",
                "Stable prompt, history, and result meaning. DNA may change hierarchy and grouping, never the application truth.",
            ),
            rx.separator(),
            _semantic_section(
                "Primary action",
                "The same action remains discoverable and semantically primary across every reference.",
                alternate=True,
            ),
            rx.separator(),
            _semantic_section(
                "System state",
                "Loading, success, warning, and failure meaning remain explicit while presentation structure changes.",
            ),
            rx.separator(),
            _semantic_section(
                "Auxiliary context",
                "Metadata remains available without replacing the primary work surface or reading sanctuary.",
            ),
            width="100%",
            spacing="0",
        ),
        width="100%",
        border=f"1px solid {CanonicalDnaState.border}",
        border_radius=CanonicalDnaState.group_radius,
        overflow="hidden",
        background_color=CanonicalDnaState.surface,
    )


def _mobile_vertical_punctuation() -> rx.Component:
    return rx.box(
        rx.vstack(
            _mobile_step("•", _work_surface()),
            _mobile_step("!", _primary_action()),
            _mobile_step("•", _system_state()),
            _mobile_step("→", _auxiliary_context()),
            width="100%",
            spacing="3",
        ),
        width="100%",
        border_left=f"3px dashed {CanonicalDnaState.accent}",
        padding_left="0.5rem",
    )


def _mobile_linear_trace() -> rx.Component:
    return rx.vstack(
        rx.hstack(rx.badge("01", variant="solid"), rx.text("WORK TRACE", size="1", weight="bold"), width="100%"),
        rx.box(_work_surface(), width="96%", margin_left="4%", border_left=f"4px solid {CanonicalDnaState.accent}", padding_left="0.5rem"),
        rx.hstack(rx.badge("02", variant="solid"), rx.text("ACTION TRACE", size="1", weight="bold"), width="100%"),
        rx.box(_primary_action(), width="96%", margin_left="4%", border_left=f"4px solid {CanonicalDnaState.accent}", padding_left="0.5rem"),
        rx.hstack(rx.badge("03", variant="solid"), rx.text("STATE TRACE", size="1", weight="bold"), width="100%"),
        rx.box(_system_state(), width="96%", margin_left="4%", border_left=f"4px solid {CanonicalDnaState.accent}", padding_left="0.5rem"),
        rx.hstack(rx.badge("04", variant="solid"), rx.text("AUX TRACE", size="1", weight="bold"), width="100%"),
        rx.box(_auxiliary_context(), width="96%", margin_left="4%", border_left=f"4px solid {CanonicalDnaState.accent}", padding_left="0.5rem"),
        width="100%",
        spacing="2",
    )


def _mobile_structural_fixture() -> rx.Component:
    return rx.cond(
        CanonicalDnaState.mobile_strategy == "ordered_flow",
        _mobile_ordered_flow(),
        rx.cond(
            CanonicalDnaState.mobile_strategy == "component_reflow",
            _mobile_component_reflow(),
            rx.cond(
                CanonicalDnaState.mobile_strategy == "serial_groups",
                _mobile_serial_groups(),
                rx.cond(
                    CanonicalDnaState.mobile_strategy == "serial_clusters",
                    _mobile_serial_clusters(),
                    rx.cond(
                        CanonicalDnaState.mobile_strategy == "stack_pairs",
                        _mobile_stack_pairs(),
                        rx.cond(
                            CanonicalDnaState.mobile_strategy == "ordered_asymmetry",
                            _mobile_ordered_asymmetry(),
                            rx.cond(
                                CanonicalDnaState.mobile_strategy == "reduced_continuity",
                                _mobile_reduced_continuity(),
                                rx.cond(
                                    CanonicalDnaState.mobile_strategy == "vertical_punctuation",
                                    _mobile_vertical_punctuation(),
                                    _mobile_linear_trace(),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


def _structural_fixture() -> rx.Component:
    return rx.cond(
        CanonicalDnaState.preview_viewport == "mobile",
        _mobile_structural_fixture(),
        _desktop_structural_fixture(),
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
            rx.badge(CanonicalDnaState.preview_viewport_label, variant="outline"),
            _structural_fixture(),
            rx.hstack(
                rx.badge("density: ", CanonicalDnaState.density, variant="soft"),
                rx.badge("hierarchy: ", CanonicalDnaState.hierarchy, variant="soft"),
                rx.badge("continuity: ", CanonicalDnaState.continuity, variant="soft"),
                rx.badge("motion: ", CanonicalDnaState.motion, variant="soft"),
                rx.badge("type: ", CanonicalDnaState.typography, variant="soft"),
                wrap="wrap",
            ),
            rx.text(
                "Host template: ", CanonicalDnaState.fixture_template,
                " · mobile strategy: ", CanonicalDnaState.mobile_strategy,
                " · canonical viewport: ", CanonicalDnaState.preview_viewport,
                size="2", color=CanonicalDnaState.text_muted,
            ),
            width="100%",
            spacing="4",
        ),
        width="100%",
        min_width=rx.cond(CanonicalDnaState.preview_viewport == "desktop", "44rem", "0"),
        background_color=CanonicalDnaState.background,
        color=CanonicalDnaState.text_color,
        font_family=CanonicalDnaState.font_family,
        border=f"1px solid {CanonicalDnaState.border}",
        border_radius=CanonicalDnaState.group_radius,
        padding=CanonicalDnaState.group_padding,
    )


def canonical_theme_studio_panel() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Canonical Design-DNA · EQ4 proving", size="5"),
                    rx.text("Canonical catalog is complete; host realization is deliberately graduated by evidence.", size="2"),
                    align="start",
                ),
                rx.spacer(),
                rx.badge("Asset-off first", variant="soft"),
                wrap="wrap", width="100%",
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
                    rx.cond(CanonicalDnaState.filtered_catalog.length() == 0, rx.text("No canonical reference matches this search.", size="2")),
                    spacing="2", width="100%",
                ),
                max_height="20rem", overflow_y="auto", width="100%",
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
                wrap="wrap", width="100%",
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("Canonical projection viewport", size="2"),
                    rx.select(["desktop", "mobile"], value=CanonicalDnaState.preview_viewport, on_change=CanonicalDnaState.set_preview_viewport),
                    align="start",
                ),
                rx.checkbox("Reduced motion", checked=CanonicalDnaState.reduced_motion, on_change=CanonicalDnaState.set_reduced_motion),
                wrap="wrap", width="100%", align="end",
            ),
            rx.callout(CanonicalDnaState.preview_message, icon="info", width="100%"),
            rx.cond(
                CanonicalDnaState.plan_ready,
                rx.vstack(
                    rx.box(_canonical_fixture(), width="100%", overflow_x="auto"),
                    rx.hstack(
                        rx.text("Fingerprint: ", CanonicalDnaState.fingerprint, size="1", color=CanonicalDnaState.text_muted),
                        rx.text("Degraded mechanisms: ", CanonicalDnaState.degraded_mechanism_count, size="1", color=CanonicalDnaState.text_muted),
                        wrap="wrap",
                    ),
                    rx.hstack(
                        rx.badge(rx.cond(CanonicalDnaState.accessibility_applied, "Accessibility veto applied", "Accessibility safe"), variant="soft"),
                        rx.badge(rx.cond(CanonicalDnaState.reading_sanctuary_applied, "Reading Sanctuary applied", "Reading-safe"), variant="soft"),
                        rx.badge(rx.cond(CanonicalDnaState.reduced_motion_applied, "Reduced motion applied", "Motion policy normal"), variant="soft"),
                        wrap="wrap",
                    ),
                    rx.button("Apply canonical proving presentation", on_click=CanonicalDnaState.apply_reference, variant="solid"),
                    width="100%", spacing="3",
                ),
            ),
            width="100%", spacing="3",
        ),
        width="100%",
    )


__all__ = ["canonical_theme_studio_panel"]
