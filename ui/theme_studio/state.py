"""Compatibility shim for the quarantined Theme Studio state implementation.

The implementation moved to ``dna_quarantine.theme_studio.state`` during Q1.
Keep this module import-compatible until the public bridge is cut in Q3/Q4.
"""

from dna_quarantine.theme_studio.state import (
    SESSION_DRAFT_KEY,
    ThemeStudioDraft,
    apply_draft_to_active_theme,
    get_or_create_draft,
    init_draft_from_base,
    init_draft_from_composition,
    reset_draft_to_base,
)

__all__ = [
    "SESSION_DRAFT_KEY",
    "ThemeStudioDraft",
    "apply_draft_to_active_theme",
    "get_or_create_draft",
    "init_draft_from_base",
    "init_draft_from_composition",
    "reset_draft_to_base",
]
