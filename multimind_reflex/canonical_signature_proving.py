"""Isolated visual-signature proving panels for canonical Design-DNA.

These panels may render draft private signature packs only for evidence collection.
They never change application truth, theme selection truth, visual-complete credit,
or production cutover state. Draft packs remain unavailable to normal presentation
resolution.
"""
from __future__ import annotations

import reflex as rx

from ui.canonical_signature_bridge import resolve_signature_for_proving


_BATCHES = (
    (
        "01",
        "material + typography · accepted baseline",
        (
            ("CA20", "Arts & Crafts"),
            ("CA21", "De Stijl"),
            ("CA22", "Cassandre"),
            ("CA24", "Art Deco"),
            ("CA27", "Streamline"),
            ("CA28", "Eames"),
        ),
    ),
    (
        "02",
        "generic material + typography · cultural-safe draft proving",
        (
            ("CA16", "Adire"),
            ("CA01", "Batik"),
            ("CA19", "Bògòlanfini"),
            ("CA14", "Ghadamès"),
            ("CA23", "Guimard"),
            ("CA29", "Guna Mola"),
        ),
    ),
)
_REFERENCES = tuple(item for _, _, batch in _BATCHES for item in batch)
_SURFACES = {reference_id: resolve_signature_for_proving(reference_id) for reference_id, _ in _REFERENCES}


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
                rx.text("Private signature unavailable; structural fallback retained.", size="2"),
                align="start",
                width="100%",
            ),
            width="100%",
            data_signature_reference=reference_id,
            data_signature_status="fallback",
        )

    t = surface.typography
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


def _batch_panel(batch_id: str, subtitle: str, batch: tuple[tuple[str, str], ...]) -> rx.Component:
    available = sum(_SURFACES.get(reference_id) is not None for reference_id, _ in batch)
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(f"Theme visual-signature proving · Batch {batch_id}", size="5"),
                    rx.text(subtitle, size="2"),
                    align="start",
                ),
                rx.spacer(),
                rx.badge(f"{available}/{len(batch)} PRIVATE SIGNATURES AVAILABLE", variant="soft"),
                width="100%",
                wrap="wrap",
            ),
            rx.callout(
                "This proving surface grants no visual-complete credit. Draft promotion still requires browser evidence and explicit private governance.",
                icon="shield_check",
                width="100%",
            ),
            rx.grid(
                *(_signature_card(reference_id, label) for reference_id, label in batch),
                columns=rx.breakpoints(initial="1", md="2"),
                spacing="3",
                width="100%",
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
        data_signature_batch=batch_id,
        data_signature_complete_credit="0",
    )


def canonical_signature_proving_panel() -> rx.Component:
    return rx.vstack(
        *(_batch_panel(batch_id, subtitle, batch) for batch_id, subtitle, batch in _BATCHES),
        width="100%",
        spacing="4",
    )


__all__ = ["canonical_signature_proving_panel"]
