"""Compatibility shim for the quarantined Theme Studio UI surface.

The implementation moved to ``dna_quarantine.theme_studio.surface`` during Q1.
Keep this import path stable until the public bridge is cut in Q3/Q4.
"""

from dna_quarantine.theme_studio.surface import (
    ensure_option_present,
    render_theme_studio_surface,
)

__all__ = ["ensure_option_present", "render_theme_studio_surface"]
