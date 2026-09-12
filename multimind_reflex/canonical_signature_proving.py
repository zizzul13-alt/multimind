"""Isolated visual-signature proving panel for canonical Design-DNA.

This panel may render draft private signature packs only for evidence collection.
It never changes application truth, theme selection truth, or production cutover
state. Draft packs remain unavailable to normal presentation resolution.
"""
from __future__ import annotations

import reflex as rx

from ui.canonical_signature_bridge import resolve_signature_for_proving


_BATCH = (
    ("CA20", "Arts & Crafts"),
    ("CA21", "De Stijl"),
    ("CA22", "Cassandre"),
    ("CA24", "Art Deco"),
    ("CA27", "Streamline"),
    ("CA28", "Eames"),
)
_SURFACES = {reference_id: resolve_signature_for_proving(reference_id) for reference_id, _ in _BATCH}


def _signature_card(reference_id: str, label: str) -> rx.Component:
    surface = _SURFACES.get(reference_id)
    if surface is None:
        return rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading(label, size="4"),
                    rx.spacer(),
                    rx.badge(f"{reference_id} · NEUTRAL FALLBACK", variant="soft"),
                    width="100%",
                    wrap="wrap",
                ),
                rx.text("Private draft signature unavailable; structural fallback retained.", size="2"),
                align="start",
                width="100%",
            ),
            width="100%",
            data_signature_reference=reference_id,
            data_signature_status="fallback",
        )

    t = surface.typography
    # Material is intentionally placed in a frame/gutter field around the opaque
    # semantic content surface. It is never a blanket texture under text.
    return rx.box(
        rx.box(
            position="absolute",
            inset="0",
            background_image=f"url('{surface.data_uri}')",
            background_repeat="repeat",
            background_size=surface.tile_size,
            opacity=str(surface.surface_opacity),
            pointer_events="none",
            border_radius="inherit",
            data_signature_material=surface.material_unit_id,
            data_signature_candidate=surface.material_candidate_id,
            data_signature_sha256=surface.payload_sha256,
            data_signature_opacity=str(surface.surface_opacity),
            data_signature_placement=surface.placement_mode,
        ),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.heading(
                        label,
                        size="5",
                        font_family=t.font_family,
                        font_weight=str(t.font_weight),
                        letter_spacing=t.heading_letter_spacing,
                        text_transform=t.heading_text_transform,
                    ),
                    rx.spacer(),
                    rx.badge(
                        f"{reference_id} · {'FINAL' if surface.final_approved else 'DRAFT PROVING'}",
                        variant="soft",
                    ),
                    width="100%",
                    align="center",
                    wrap="wrap",
                ),
                rx.text(
                    "Work surface",
                    font_family=t.font_family,
                    letter_spacing=t.body_letter_spacing,
                    line_height=str(t.line_height),
                    weight="medium",
                ),
                rx.text(
                    "Primary action · System state · Auxiliary context",
                    font_family=t.font_family,
                    letter_spacing=t.body_letter_spacing,
                    line_height=str(t.line_height),
                    size="2",
                ),
                rx.hstack(
                    rx.badge(surface.material_variant, variant="outline"),
                    rx.badge(t.pack_id, variant="outline"),
                    wrap="wrap",
                ),
                align="start",
                width="100%",
                spacing="2",
            ),
            position="relative",
            z_index="1",
            margin="10px",
            padding="1rem",
            background_color="var(--color-panel-solid)",
            border="1px solid var(--gray-a6)",
            border_radius="10px",
            data_signature_typography=t.pack_id,
        ),
        position="relative",
        isolation="isolate",
        overflow="hidden",
        width="100%",
        border_radius="14px",
        data_signature_reference=reference_id,
        data_signature_status="candidate",
    )


def canonical_signature_proving_panel() -> rx.Component:
    available = sum(surface is not None for surface in _SURFACES.values())
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Theme visual-signature proving", size="5"),
                    rx.text(
                        "Batch 01 · material + typography · isolated evidence only",
                        size="2",
                    ),
                    align="start",
                ),
                rx.spacer(),
                rx.badge(f"{available}/6 PRIVATE DRAFTS AVAILABLE", variant="soft"),
                width="100%",
                wrap="wrap",
            ),
            rx.callout(
                "A theme does not receive visual-complete credit here. Final approval requires browser evidence and explicit private-governance promotion.",
                icon="shield_check",
                width="100%",
            ),
            rx.grid(
                *(_signature_card(reference_id, label) for reference_id, label in _BATCH),
                columns=rx.breakpoints(initial="1", md="2"),
                spacing="3",
                width="100%",
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
        data_signature_batch="01",
        data_signature_complete_credit="0",
    )


__all__ = ["canonical_signature_proving_panel"]
