"""Canonical Design-DNA extension for the real Reflex workspace.

This module extends the already-accepted RJ3 host state only with presentation
state. Application/session/provider/persistence truth stays in the base
``HostState`` and ``MultiMindApplication`` boundary.

Two presentation modes deliberately coexist during migration:

* ``canonical`` — one of the 160 canonical reference records is realized through
  the private bridge and projected through the finite host vocabulary.
* ``legacy`` — the existing role-based Identity/Web composition remains a safe
  rollback/compatibility path until an explicit later cutover decision.

Canonical absence/failure always falls back to the legacy/neutral presentation;
it never blocks MultiMind operation.
"""
from __future__ import annotations

import reflex as rx

from multimind_reflex.canonical_projection import project_reflex_tokens
from multimind_reflex.state import (
    ARCHETYPES,
    HostState as LegacyHostState,
    _DEFAULT_IDENTITY_DNA,
    _DEFAULT_WEB_DNA,
    _NEUTRAL_IDENTITY_CHOICE,
    _NONE_WEB_CHOICE,
    _choice_for_id,
    _choice_id,
    _radius_preset,
)
from ui.music_dna_bridge import list_music_theme_options, realize_music_theme
from ui.canonical_dna_bridge import (
    list_canonical_reference_options,
    list_host_realizable_reference_ids,
    realize_canonical_reference,
)


# Theme Studio is phone-first in practice. A small result window avoids forcing
# users through a 30-item scroll wall while preserving the full 160-reference
# catalog behind search.
_CANONICAL_RESULT_LIMIT = 12


def _canonical_catalog_snapshots() -> list[dict[str, str]]:
    ready = set(list_host_realizable_reference_ids())
    return [
        {
            "id": option.id,
            "display_name": option.display_name,
            "family": option.family,
            "category": option.category,
            "lineage": option.lineage,
            "host_ready": "true" if option.id in ready else "false",
        }
        for option in list_canonical_reference_options()
    ]


def _filter_canonical_catalog(
    catalog: list[dict[str, str]], query: str
) -> list[dict[str, str]]:
    text = str(query or "").strip().casefold()
    terms = tuple(item for item in text.split() if item)
    result: list[dict[str, str]] = []
    for item in catalog:
        if item.get("host_ready") != "true":
            continue
        haystack = " ".join(
            str(item.get(key, ""))
            for key in ("id", "display_name", "family", "category", "lineage")
        ).casefold()
        if not terms or all(term in haystack for term in terms):
            result.append(item)
        if len(result) >= _CANONICAL_RESULT_LIMIT:
            break
    return result


def _music_choice_label(option) -> str:
    """Stable MusicDNA select label owned by the host presentation layer."""
    return f"{option.display_name} · music:{option.id}"


def _initial_music_dna_choices() -> list[str]:
    """Host-owned catalog snapshot from private MusicDNA when available.

    Mirrors ``_canonical_catalog_snapshots``: the selector catalog is not
    discovered solely by the login event. Session state still owns the user's
    selection; this only seeds the immutable option list for Theme Studio.
    """
    try:
        options = list_music_theme_options(include_all=True)
    except Exception:
        return []
    return [_music_choice_label(option) for option in options]


class WorkspaceDnaState(LegacyHostState):
    """Presentation-only canonical extension of the accepted Reflex host state."""

    canonical_catalog: list[dict[str, str]] = _canonical_catalog_snapshots()
    canonical_query: str = ""
    music_dna_choices: list[str] = _initial_music_dna_choices()

    draft_dna_mode: str = "legacy"
    active_dna_mode: str = "legacy"

    draft_canonical_reference_id: str = ""
    draft_canonical_display_name: str = ""
    draft_canonical_fingerprint: str = ""
    draft_canonical_layout_flow: str = ""
    draft_canonical_mobile_strategy: str = ""
    draft_canonical_balance: str = ""
    draft_canonical_density: str = ""
    draft_canonical_hierarchy: str = ""
    draft_canonical_continuity: str = ""
    draft_canonical_motion: str = ""
    draft_canonical_gap: str = "1rem"
    draft_canonical_card_padding: str = "1rem"
    draft_canonical_card_radius: str = "8px"
    draft_canonical_font_family: str = "system-ui, -apple-system, sans-serif"
    draft_canonical_line_height: str = "1.5"

    active_canonical_reference_id: str = ""
    active_canonical_display_name: str = ""
    active_canonical_fingerprint: str = ""
    active_canonical_layout_flow: str = ""
    active_canonical_mobile_strategy: str = ""
    active_canonical_balance: str = ""
    active_canonical_density: str = ""
    active_canonical_hierarchy: str = ""
    active_canonical_continuity: str = ""
    active_canonical_motion: str = ""
    active_canonical_gap: str = "1rem"
    active_canonical_card_padding: str = "1rem"
    active_canonical_card_radius: str = "8px"
    active_canonical_font_family: str = "system-ui, -apple-system, sans-serif"
    active_canonical_line_height: str = "1.5"

    draft_music_topology: str = ""
    draft_music_world: str = ""
    draft_music_signature: str = ""
    draft_music_combination_id: str = ""
    draft_music_layout_flow: str = ""
    draft_music_mobile_strategy: str = ""
    draft_music_primary_object: str = ""
    draft_music_primary_action: str = ""
    draft_music_composer_label: str = ""
    draft_music_asset_url: str = ""
    draft_music_asset_credit: str = ""
    active_music_topology: str = ""
    active_music_world: str = ""
    active_music_signature: str = ""
    active_music_combination_id: str = ""
    active_music_layout_flow: str = ""
    active_music_mobile_strategy: str = ""
    active_music_primary_object: str = ""
    active_music_primary_action: str = ""
    active_music_composer_label: str = ""
    active_music_asset_url: str = ""
    active_music_asset_credit: str = ""

    @rx.var
    def music_selector_status(self) -> str:
        if not self.draft_identity_dna.startswith("music:"):
            return "No MusicDNA track selected"
        return f"{self.draft_identity_display_name} × {self.draft_archetype}"

    @rx.var
    def filtered_canonical_catalog(self) -> list[dict[str, str]]:
        return _filter_canonical_catalog(self.canonical_catalog, self.canonical_query)

    @rx.var
    def canonical_catalog_total(self) -> int:
        return len(self.canonical_catalog)

    @rx.var
    def canonical_host_ready_total(self) -> int:
        return sum(item.get("host_ready") == "true" for item in self.canonical_catalog)

    def _load_theme_studio_catalog(self):
        """Reconcile legacy + MusicDNA catalogs after login.

        MusicDNA choices are also seeded at state definition via
        ``_initial_music_dna_choices`` so Theme Studio is not empty when the
        private package is already importable. This method remains the
        refresh path after authentication.
        """
        super()._load_theme_studio_catalog()
        choices = _initial_music_dna_choices()
        self.music_dna_choices = choices
        if not choices:
            return
        first = choices[0]
        self.draft_identity_choice = first
        self.draft_identity_dna = _choice_id(first)
        self._clear_canonical_draft()
        self._refresh_music_draft()
        self._copy_draft_to_active()
