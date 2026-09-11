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


class WorkspaceDnaState(LegacyHostState):
    """Presentation-only canonical extension of the accepted Reflex host state."""

    canonical_catalog: list[dict[str, str]] = _canonical_catalog_snapshots()
    canonical_query: str = ""

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

    @rx.var
    def filtered_canonical_catalog(self) -> list[dict[str, str]]:
        return _filter_canonical_catalog(self.canonical_catalog, self.canonical_query)

    @rx.var
    def canonical_catalog_total(self) -> int:
        return len(self.canonical_catalog)

    @rx.var
    def canonical_host_ready_total(self) -> int:
        return sum(item.get("host_ready") == "true" for item in self.canonical_catalog)

    def _clear_canonical_draft(self) -> None:
        self.draft_canonical_reference_id = ""
        self.draft_canonical_display_name = ""
        self.draft_canonical_fingerprint = ""
        self.draft_canonical_layout_flow = ""
        self.draft_canonical_mobile_strategy = ""
        self.draft_canonical_balance = ""
        self.draft_canonical_density = ""
        self.draft_canonical_hierarchy = ""
        self.draft_canonical_continuity = ""
        self.draft_canonical_motion = ""
        self.draft_canonical_gap = "1rem"
        self.draft_canonical_card_padding = "1rem"
        self.draft_canonical_card_radius = "8px"
        self.draft_canonical_font_family = "system-ui, -apple-system, sans-serif"
        self.draft_canonical_line_height = "1.5"

    def _clear_canonical_active(self) -> None:
        self.active_canonical_reference_id = ""
        self.active_canonical_display_name = ""
        self.active_canonical_fingerprint = ""
        self.active_canonical_layout_flow = ""
        self.active_canonical_mobile_strategy = ""
        self.active_canonical_balance = ""
        self.active_canonical_density = ""
        self.active_canonical_hierarchy = ""
        self.active_canonical_continuity = ""
        self.active_canonical_motion = ""
        self.active_canonical_gap = "1rem"
        self.active_canonical_card_padding = "1rem"
        self.active_canonical_card_radius = "8px"
        self.active_canonical_font_family = "system-ui, -apple-system, sans-serif"
        self.active_canonical_line_height = "1.5"

    def _copy_canonical_draft_to_active(self) -> None:
        self.active_dna_mode = self.draft_dna_mode
        self.active_canonical_reference_id = self.draft_canonical_reference_id
        self.active_canonical_display_name = self.draft_canonical_display_name
        self.active_canonical_fingerprint = self.draft_canonical_fingerprint
        self.active_canonical_layout_flow = self.draft_canonical_layout_flow
        self.active_canonical_mobile_strategy = self.draft_canonical_mobile_strategy
        self.active_canonical_balance = self.draft_canonical_balance
        self.active_canonical_density = self.draft_canonical_density
        self.active_canonical_hierarchy = self.draft_canonical_hierarchy
        self.active_canonical_continuity = self.draft_canonical_continuity
        self.active_canonical_motion = self.draft_canonical_motion
        self.active_canonical_gap = self.draft_canonical_gap
        self.active_canonical_card_padding = self.draft_canonical_card_padding
        self.active_canonical_card_radius = self.draft_canonical_card_radius
        self.active_canonical_font_family = self.draft_canonical_font_family
        self.active_canonical_line_height = self.draft_canonical_line_height

    def _copy_canonical_active_to_draft(self) -> None:
        self.draft_dna_mode = self.active_dna_mode
        self.draft_canonical_reference_id = self.active_canonical_reference_id
        self.draft_canonical_display_name = self.active_canonical_display_name
        self.draft_canonical_fingerprint = self.active_canonical_fingerprint
        self.draft_canonical_layout_flow = self.active_canonical_layout_flow
        self.draft_canonical_mobile_strategy = self.active_canonical_mobile_strategy
        self.draft_canonical_balance = self.active_canonical_balance
        self.draft_canonical_density = self.active_canonical_density
        self.draft_canonical_hierarchy = self.active_canonical_hierarchy
        self.draft_canonical_continuity = self.active_canonical_continuity
        self.draft_canonical_motion = self.active_canonical_motion
        self.draft_canonical_gap = self.active_canonical_gap
        self.draft_canonical_card_padding = self.active_canonical_card_padding
        self.draft_canonical_card_radius = self.active_canonical_card_radius
        self.draft_canonical_font_family = self.active_canonical_font_family
        self.draft_canonical_line_height = self.active_canonical_line_height

    def _refresh_canonical_draft(self) -> bool:
        if not self.draft_canonical_reference_id:
            return False
        plan = realize_canonical_reference(
            self.draft_canonical_reference_id,
            viewport="desktop",
            asset_state="off",
            archetype_id=self.draft_archetype,
            accessibility_required=True,
        )
        if plan is None:
            self.theme_status = "Canonical realization failed safely; legacy presentation retained"
            return False
        try:
            tokens = project_reflex_tokens(plan)
        except (TypeError, ValueError):
            self.theme_status = "Canonical vocabulary unsupported; legacy presentation retained"
            return False

        self.draft_dna_mode = "canonical"
        self.draft_canonical_reference_id = plan.reference_id
        self.draft_canonical_display_name = plan.display_name
        self.draft_canonical_fingerprint = plan.source_fingerprint
        self.draft_canonical_layout_flow = plan.layout_flow
        self.draft_canonical_mobile_strategy = plan.mobile_strategy
        self.draft_canonical_balance = plan.balance
        self.draft_canonical_density = plan.density
        self.draft_canonical_hierarchy = plan.hierarchy
        self.draft_canonical_continuity = plan.continuity
        self.draft_canonical_motion = plan.motion
        self.draft_canonical_gap = tokens.gap
        self.draft_canonical_card_padding = tokens.card_padding
        self.draft_canonical_card_radius = tokens.card_radius
        self.draft_canonical_font_family = tokens.font_family
        self.draft_canonical_line_height = tokens.line_height

        # Reuse the accepted editable presentation-token seam. Canonical
        # structural identity remains tracked separately above; these neutral,
        # accessible tokens ensure Theme Studio and workspace immediately consume
        # the selected plan without introducing a second rendering engine.
        self.draft_background = tokens.background
        self.draft_surface = tokens.surface
        self.draft_text_color = tokens.text
        self.draft_primary = tokens.accent
        self.draft_accent = tokens.accent
        self.draft_border = tokens.border
        self.draft_font_family = tokens.font_family
        self.draft_radius_value = tokens.card_radius
        self.draft_spacing_value = tokens.card_padding
        self.draft_radius = _radius_preset(tokens.card_radius)
        self.draft_density = plan.density
        self.draft_metadata_prominence = "canonical"
        self.draft_status_richness = "canonical"
        self.draft_navigation_density = plan.mobile_strategy
        self.draft_secondary_compactness = plan.density == "compact"
        self.draft_information_discoverability = plan.hierarchy
        self.draft_utility_grouping = plan.layout_flow
        self.draft_hierarchy_contrast = plan.hierarchy
        self.draft_border_style = "solid"
        self.draft_energy_emphasis = plan.balance
        self.draft_surface_treatment = plan.layout_flow
        self.draft_transition_speed = plan.motion
        self.theme_status = f"Canonical Design-DNA · {plan.display_name}"
        return True

    def _restore_legacy_draft(self) -> None:
        self.draft_dna_mode = "legacy"
        self._clear_canonical_draft()
        if self.draft_identity_dna and self._refresh_theme_draft_from_composition():
            self.theme_status = "Legacy role-based Design-DNA"
            return
        self._set_neutral_theme_draft()
        self.draft_dna_mode = "legacy"
        self.theme_status = "Safe neutral presentation"

    @rx.event
    def refresh_canonical_catalog(self):
        self.canonical_catalog = _canonical_catalog_snapshots()
        if self.draft_canonical_reference_id and not any(
            item["id"] == self.draft_canonical_reference_id
            and item.get("host_ready") == "true"
            for item in self.canonical_catalog
        ):
            self._restore_legacy_draft()

    @rx.event
    def set_canonical_query(self, value: str):
        self.canonical_query = value

    @rx.event
    def select_canonical_reference(self, reference_id: str):
        selected = next(
            (
                item
                for item in self.canonical_catalog
                if item["id"] == reference_id and item.get("host_ready") == "true"
            ),
            None,
        )
        if selected is None:
            self.theme_status = "Canonical reference unavailable; legacy presentation retained"
            return
        previous_id = self.draft_canonical_reference_id
        self.draft_canonical_reference_id = selected["id"]
        self.draft_canonical_display_name = selected["display_name"]
        if not self._refresh_canonical_draft():
            self.draft_canonical_reference_id = previous_id
            if previous_id:
                self._refresh_canonical_draft()
            else:
                self._restore_legacy_draft()
            return

        # Collapse the long result list to the selected item after a successful
        # tap. The field remains editable, so finding the next DNA is one tap +
        # typing rather than another long mobile scroll.
        self.canonical_query = selected["id"]
        self.success_message = f"Canonical draft selected: {selected['display_name']}"

    @rx.event
    def use_legacy_dna(self):
        self._restore_legacy_draft()
        self.canonical_query = ""
        self.success_message = "Legacy role-based presentation selected as draft."

    @rx.event
    def set_composed_archetype(self, value: str):
        if value not in ARCHETYPES:
            return
        previous = self.draft_archetype
        self.draft_archetype = value
        if self.draft_dna_mode == "canonical" and self.draft_canonical_reference_id:
            if not self._refresh_canonical_draft():
                self.draft_archetype = previous
                self._refresh_canonical_draft()
            return
        if self.draft_identity_dna and not self._refresh_theme_draft_from_composition():
            self.draft_archetype = previous

    @rx.event
    def set_composed_identity_choice(self, value: str):
        unit_id = _choice_id(value)
        available = {_choice_id(choice) for choice in self.identity_dna_choices}
        if not unit_id or unit_id not in available:
            return
        self.draft_dna_mode = "legacy"
        self._clear_canonical_draft()
        self.canonical_query = ""
        self.draft_identity_choice = value
        self.draft_identity_dna = unit_id
        self._refresh_theme_draft_from_composition()

    @rx.event
    def set_composed_web_choice(self, value: str):
        unit_id = _choice_id(value)
        available = {_choice_id(choice) for choice in self.web_dna_choices}
        if unit_id and unit_id not in available:
            return
        self.draft_dna_mode = "legacy"
        self._clear_canonical_draft()
        self.canonical_query = ""
        self.draft_web_choice = value or _NONE_WEB_CHOICE
        self.draft_web_dna = unit_id
        self._refresh_theme_draft_from_composition()

    @rx.event
    def apply_composed_theme(self):
        self._copy_draft_to_active()
        self._copy_canonical_draft_to_active()
        self.theme_studio_open = False
        self.current_surface = "workspace"
        if self.active_dna_mode == "canonical":
            self.success_message = "Canonical Design-DNA presentation applied."
        else:
            self.success_message = "Legacy theme composition applied."

    @rx.event
    def discard_composed_theme(self):
        self._copy_active_to_draft()
        self._copy_canonical_active_to_draft()
        self.canonical_query = self.draft_canonical_reference_id if self.draft_dna_mode == "canonical" else ""
        self.success_message = "Presentation draft discarded."

    @rx.event
    def reset_composed_theme(self):
        self.draft_dna_mode = "legacy"
        self._clear_canonical_draft()
        self.canonical_query = ""
        identity_ids = {_choice_id(choice) for choice in self.identity_dna_choices}
        web_ids = {_choice_id(choice) for choice in self.web_dna_choices}
        if _DEFAULT_IDENTITY_DNA in identity_ids:
            self.draft_identity_dna = _DEFAULT_IDENTITY_DNA
        else:
            candidates = sorted(item for item in identity_ids if item)
            if not candidates:
                self._set_neutral_theme_draft()
                self.draft_dna_mode = "legacy"
                self.success_message = "Draft reset to safe defaults."
                return
            self.draft_identity_dna = candidates[0]
        self.draft_web_dna = _DEFAULT_WEB_DNA if _DEFAULT_WEB_DNA in web_ids else ""
        self.draft_archetype = "chat_first"
        self.draft_identity_choice = _choice_for_id(
            self.identity_dna_choices,
            self.draft_identity_dna,
            _NEUTRAL_IDENTITY_CHOICE,
        )
        self.draft_web_choice = _choice_for_id(
            self.web_dna_choices,
            self.draft_web_dna,
            _NONE_WEB_CHOICE,
        )
        self._refresh_theme_draft_from_composition()
        self.success_message = "Draft reset to resolved legacy defaults."

    @rx.event
    def logout_composed(self):
        """Mirror accepted logout semantics while clearing canonical presentation state."""
        if self.busy:
            self.error_message = "A run is still active."
            return
        self.username = ""
        self.display_username = ""
        self.user_id = ""
        self.logged_in = False
        self.current_surface = "theme"
        self.sessions = []
        self.current_session_id = ""
        self.current_session_name = ""
        self.current_session_mode = "coding"
        self.history = []
        self.prompt = ""
        self.status_message = ""
        self.error_message = ""
        self.success_message = ""
        self.final_answer = ""
        self._clear_deliberation_projection()
        self.warnings = []
        self.upload_names = []
        self._runtime_memories = {}
        self._pending_uploads = []
        self._pending_restore = b""
        self.identity_dna_choices = [_NEUTRAL_IDENTITY_CHOICE]
        self.web_dna_choices = [_NONE_WEB_CHOICE]
        self._set_neutral_theme_draft()
        self.draft_dna_mode = "legacy"
        self.active_dna_mode = "legacy"
        self.canonical_query = ""
        self._clear_canonical_draft()
        self._clear_canonical_active()
        self._copy_draft_to_active()


__all__ = [
    "WorkspaceDnaState",
    "_canonical_catalog_snapshots",
    "_filter_canonical_catalog",
]
