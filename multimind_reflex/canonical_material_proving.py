"""Isolated approved-material proving panel for the canonical Reflex route.

This panel is evidence infrastructure only. It does not bind M7 globally to any
reference/theme. A future composition may consume M7 only when its canonical
material semantics explicitly request Textile / Woven.
"""
from __future__ import annotations

import reflex as rx

from ui.canonical_asset_bridge import resolve_approved_asset_surface


_M7_SURFACE = resolve_approved_asset_surface("M7")


def canonical_material_proving_panel() -> rx.Component:
    if _M7_SURFACE is None:
        return rx.card(
            rx.vstack(
                rx.heading("Approved material proving", size="5"),
                rx.callout(
                    "Approved private material payload unavailable; neutral structural fallback retained.",
                    icon="shield_check",
                    width="100%",
                ),
                align="start",
                width="100%",
            ),
            width="100%",
        )

    surface = _M7_SURFACE
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Approved material proving", size="5"),
                    rx.text(
                        "M7 · Textile / Woven · isolated asset-on evidence; no reference/theme binding implied.",
                        size="2",
                    ),
                    align="start",
                ),
                rx.spacer(),
                rx.badge("M7 APPROVED PAYLOAD · ACTIVE", variant="soft"),
                width="100%",
                wrap="wrap",
            ),
            rx.box(
                rx.box(
                    position="absolute",
                    inset="0",
                    background_image=f"url('{surface.data_uri}')",
                    background_repeat="repeat",
                    background_size=surface.tile_size,
                    opacity=str(surface.surface_opacity),
                    pointer_events="none",
                    border_radius="inherit",
                    data_asset_unit=surface.unit_id,
                    data_asset_candidate=surface.candidate_id,
                    data_asset_sha256=surface.payload_sha256,
                    data_asset_opacity=str(surface.surface_opacity),
                ),
                rx.vstack(
                    rx.text("Approved asset payload is behind this semantic fixture.", weight="bold"),
                    rx.text(
                        "Structural identity remains primary; the visual layer is optional enrichment and may be vetoed.",
                        size="2",
                    ),
                    rx.hstack(
                        rx.badge("Textile / Woven", variant="outline"),
                        rx.badge("CC0 self-hosted", variant="outline"),
                        rx.badge("opacity 0.01", variant="outline"),
                        wrap="wrap",
                    ),
                    align="start",
                    position="relative",
                    z_index="1",
                    width="100%",
                ),
                position="relative",
                isolation="isolate",
                overflow="hidden",
                width="100%",
                padding="1rem",
                border="1px solid var(--gray-a6)",
                border_radius="10px",
                background_color="var(--color-panel-solid)",
                data_material_proof="m7-approved",
            ),
            rx.text(
                "This proves package→public bridge→Reflex rendering only. Production cutover remains unauthorized.",
                size="1",
                color="var(--gray-a11)",
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
    )


__all__ = ["canonical_material_proving_panel"]
