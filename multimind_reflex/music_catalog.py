"""Host-owned MusicDNA catalog snapshot for Theme Studio.

Private Design-DNA remains the source of truth. This module only projects
display labels for the Reflex selector so options are available at state
definition time (same pattern as canonical_catalog snapshots).
"""
from __future__ import annotations

from ui.music_dna_bridge import list_music_theme_options


def music_choice_label(option) -> str:
    """Stable MusicDNA select label owned by the host presentation layer."""
    return f"{option.display_name} · music:{option.id}"


def initial_music_dna_choices() -> list[str]:
    """Seed MusicDNA selector options when private DNA is importable.

    Returns an empty list when the optional private package is absent or fails;
    Theme Studio stays fail-closed and operational.
    """
    try:
        options = list_music_theme_options(include_all=True)
    except Exception:
        return []
    return [music_choice_label(option) for option in options]


__all__ = [
    "initial_music_dna_choices",
    "music_choice_label",
]
