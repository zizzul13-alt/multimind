"""Presentation-only mobile ergonomics and visual-signature layer.

The production workspace, Theme Studio, application events, provider routing,
and persistence ownership remain in their accepted modules. This entry module
only adds conservative browser ergonomics plus an optional approved-signature
frame around the same real workspace component tree.
"""
from __future__ import annotations

import reflex as rx

from multimind_reflex import multimind_reflex as _surface
from multimind_reflex import verdict_entry as _verdict_entry  # noqa: F401
from multimind_reflex.workspace_signature_state import WorkspaceSignatureState


# The accepted page functions resolve their presentation globals when Reflex
# compiles/renders them. Swap only the presentation-state class; all inherited
# application/session/provider/persistence event paths remain unchanged.
_surface.HostState = WorkspaceSignatureState
_original_workspace = _surface._workspace


def _signature_workspace() -> rx.Component:
    """Wrap the one real workspace tree with a bounded material/typography field."""
    state = WorkspaceSignatureState
    return rx.box(
        rx.box(
            _original_workspace(),
            position="relative",
            z_index="1",
            width="100%",
        ),
        width="100%",
        min_height="100vh",
        position="relative",
        isolation="isolate",
        overflow="hidden",
        background_color=state.active_background,
        data_signature_active=rx.cond(state.active_signature_available, "true", "false"),
        data_signature_reference=state.active_canonical_reference_id,
        data_signature_placement=state.active_signature_material_placement_mode,
        class_name="mm-signature-workspace-frame",
        style={
            "&::before": {
                "content": '""',
                "position": "absolute",
                "inset": "0",
                "pointer_events": "none",
                "z_index": "0",
                "background_image": rx.cond(
                    state.active_signature_available,
                    f"url({state.active_signature_material_data_uri})",
                    "none",
                ),
                "background_size": state.active_signature_material_tile_size,
                "background_repeat": "repeat",
                "opacity": state.active_signature_material_opacity,
            },
            "& .mm-workspace": {
                "background_color": rx.cond(
                    state.active_signature_available,
                    "transparent !important",
                    state.active_background,
                ),
                "font_family": state.active_signature_font_family,
            },
            "& .mm-workspace h1, & .mm-workspace h2, & .mm-workspace h3, & .mm-workspace h4, & .mm-workspace h5, & .mm-workspace h6": {
                "font_family": state.active_signature_font_family,
                "font_weight": state.active_signature_heading_font_weight_css,
                "letter_spacing": state.active_signature_heading_letter_spacing,
                "text_transform": state.active_signature_heading_text_transform,
            },
            "& .mm-workspace p, & .mm-workspace button, & .mm-workspace input, & .mm-workspace textarea, & .mm-workspace select": {
                "letter_spacing": state.active_signature_body_letter_spacing,
            },
        },
    )


# Replace only the presentation wrapper used by the already-registered page.
# The original workspace function is called exactly once by this wrapper.
_surface._workspace = _signature_workspace
app = _surface.app


_MOBILE_POLISH = {
    "*": {
        "box_sizing": "border-box",
    },
    "html": {
        "text_size_adjust": "100%",
    },
    "body": {
        "margin": "0",
        "min_width": "0",
        "overflow_x": "hidden",
    },
    "button": {
        "min_height": "2.75rem",
        "max_width": "100%",
        "touch_action": "manipulation",
    },
    "input": {
        "min_height": "2.75rem",
        "max_width": "100%",
        "font_size": "1rem",
    },
    "textarea": {
        "max_width": "100%",
        "font_size": "1rem",
        "line_height": "1.5",
        "resize": "vertical",
    },
    "select": {
        "min_height": "2.75rem",
        "max_width": "100%",
        "font_size": "1rem",
    },
    "p": {
        "overflow_wrap": "anywhere",
    },
    "pre": {
        "max_width": "100%",
        "overflow_x": "auto",
        "white_space": "pre-wrap",
        "overflow_wrap": "anywhere",
    },
    "code": {
        "overflow_wrap": "anywhere",
    },
    "@media (max-width: 48em)": {
        "body": {
            "line_height": "1.55",
        },
        "button": {
            "min_height": "2.875rem",
        },
        "input, textarea, select": {
            "font_size": "1rem",
        },
    },
}

# Keep the same accepted App instance. The stylesheet is static presentation
# only and deliberately targets existing semantic grid-area output instead of
# introducing a second workspace/component tree.
if "/mobile-workspace-polish.css" not in app.stylesheets:
    app.stylesheets.append("/mobile-workspace-polish.css")
app.style.update(_MOBILE_POLISH)


__all__ = ["app"]
