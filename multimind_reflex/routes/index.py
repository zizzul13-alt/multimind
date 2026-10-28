"""Route entry for the MultiMind Reflex host landing page.

Reflex 0.8 SPA mode uses file-based routing; this module exposes the
same ``index`` component that was previously registered via
``app.add_page`` so the React Router v8 SPA has a route to render.
"""
from __future__ import annotations

from multimind_reflex.multimind_reflex import index, app  # noqa: F401

__all__ = ["index", "app"]
