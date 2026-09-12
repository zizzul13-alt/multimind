"""Approved visual-signature presentation wiring for the accepted Reflex host.

The accepted workspace and Theme Studio remain their existing implementations.
This module only wraps the authenticated presentation once with an optional
material/typography/mark environment derived from the already-active canonical
reference. Application/provider/persistence ownership is untouched.
"""
from __future__ import annotations

import reflex as rx

import multimind_reflex.multimind_reflex as workspace
from multimind_reflex.identity_state import IdentityVerdictHostState


HostState = IdentityVerdictHostState
_original_authenticated_surface = workspace._authenticated_surface


def _signature_authenticated_surface() -> rx.Component:
    return rx.box(
        rx.box(
            position="absolute",
            inset="0",
            background_image=rx.cond(
                HostState.active_signature_available,
                f"url('{HostState.active_signature_material_data_uri}')",
                "none",
            ),
            background_repeat="repeat",
            background_size=HostState.active_signature_material_tile_size,
            opacity=HostState.active_signature_material_opacity,
            pointer_events="none",
            z_index="0",
            data_signature_material_layer="true",
        ),
        rx.box(
            position="absolute",
            top="0.75rem",
            right="0.75rem",
            width=HostState.active_signature_mark_width,
            height=HostState.active_signature_mark_height,
            border_width=HostState.active_signature_mark_stroke_width,
            border_style="solid",
            border_color=HostState.active_accent,
            border_radius=HostState.active_signature_mark_radius,
            transform=HostState.active_signature_mark_transform,
            opacity=HostState.active_signature_mark_opacity,
            display=rx.cond(HostState.active_signature_mark_available, "block", "none"),
            pointer_events="none",
            z_index="2",
            data_signature_mark_layer="true",
            data_signature_mark_pack=HostState.active_signature_mark_pack_id,
            data_signature_mark_shape=HostState.active_signature_mark_shape,
            aria_hidden="true",
        ),
        rx.box(
            _original_authenticated_surface(),
            position="relative",
            z_index="1",
            width="100%",
        ),
        position="relative",
        isolation="isolate",
        overflow="hidden",
        width="100%",
        min_height="100vh",
        background_color=HostState.active_background,
        font_family=HostState.active_signature_font_family,
        data_signature_active=rx.cond(HostState.active_signature_available, "true", "false"),
        data_signature_reference=HostState.active_canonical_reference_id,
        data_signature_placement=HostState.active_signature_material_placement_mode,
        class_name="mm-signature-authenticated-frame",
        style={
            "& .mm-workspace": {
                "background_color": rx.cond(
                    HostState.active_signature_available,
                    "transparent !important",
                    HostState.active_background,
                ),
                "font_family": HostState.active_signature_font_family,
            },
            "& .mm-workspace h1, & .mm-workspace h2, & .mm-workspace h3, & .mm-workspace h4, & .mm-workspace h5, & .mm-workspace h6": {
                "font_family": HostState.active_signature_font_family,
                "font_weight": HostState.active_signature_heading_font_weight_css,
                "letter_spacing": HostState.active_signature_heading_letter_spacing,
                "text_transform": HostState.active_signature_heading_text_transform,
            },
            "& .mm-workspace p, & .mm-workspace button, & .mm-workspace input, & .mm-workspace textarea, & .mm-workspace select": {
                "letter_spacing": HostState.active_signature_body_letter_spacing,
            },
        },
    )


workspace._authenticated_surface = _signature_authenticated_surface
app = workspace.app


__all__ = ["app"]
