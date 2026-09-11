"""Presentation-only mobile ergonomics layer for the Reflex host.

The production workspace, Theme Studio, application events, provider routing,
and persistence ownership remain in their accepted modules.  This entry module
only applies conservative global browser ergonomics before exposing the same
``rx.App`` instance to Reflex.
"""
from __future__ import annotations

from multimind_reflex.multimind_reflex import app


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

# ``app`` is the exact accepted application instance; only presentation style
# is extended.  No page, state, event, transport, or persistence owner is
# replaced here.
app.style.update(_MOBILE_POLISH)


__all__ = ["app"]
