"""Isolated real-browser proving route for canonical Design-DNA.

This route is intentionally presentation-only. It collects Reflex host evidence
without mutating application, session, provider, persistence, or cutover truth.
"""
from __future__ import annotations

import reflex as rx

from multimind_reflex.canonical_archetype_proving import canonical_archetype_context_panel
from multimind_reflex.canonical_dna_state import CanonicalDnaState
from multimind_reflex.canonical_material_proving import canonical_material_proving_panel
from multimind_reflex.canonical_signature_proving import canonical_signature_proving_panel
from multimind_reflex.canonical_theme_studio import canonical_theme_studio_panel


@rx.page(route="/canonical-dna", title="MultiMind · Canonical Design-DNA Proving")
def canonical_dna_proving_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Canonical Design-DNA", size="7"),
                    rx.text("Isolated Reflex proving surface · application truth untouched"),
                    align="start",
                ),
                rx.spacer(),
                rx.badge("PROVING · NOT CUTOVER", variant="soft"),
                width="100%",
                align="center",
                wrap="wrap",
            ),
            rx.callout(
                "This page validates canonical catalog, deterministic asset-off projection, responsive host realization, seven-archetype context survival, accessibility demotion, A→B→A presentation behavior, approved material payload rendering, and isolated draft visual-signature candidates. It does not authorize production cutover.",
                icon="shield_check",
                width="100%",
            ),
            canonical_theme_studio_panel(),
            canonical_archetype_context_panel(),
            canonical_material_proving_panel(),
            canonical_signature_proving_panel(),
            rx.hstack(
                rx.button("Refresh canonical catalog", on_click=CanonicalDnaState.refresh_catalog, variant="soft"),
                rx.button("Clear proving selection", on_click=CanonicalDnaState.clear_reference, variant="ghost"),
                wrap="wrap",
            ),
            width="100%",
            spacing="4",
        ),
        max_width="80rem",
        padding=rx.breakpoints(initial="0.75rem", sm="1rem", md="1.5rem"),
    )


__all__ = ["canonical_dna_proving_page"]
