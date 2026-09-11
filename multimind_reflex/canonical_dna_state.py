"""Reflex state for canonical Design-DNA catalog and EQ4 proving preview.

This state owns presentation-only search/preview/apply state. Canonical truth is
read exclusively through the optional public bridge; application/session/
provider/persistence state is never read or mutated here.

Host-realizable and browser-proving are deliberately separate states. A
reference may be renderable by the generic host machinery while still requiring
real-browser/operator evidence before any EQ4 credit is granted.
"""
from __future__ import annotations

import reflex as rx

from multimind_reflex.canonical_projection import project_reflex_tokens
from ui.canonical_dna_bridge import (
    list_browser_proving_reference_ids,
    list_canonical_reference_options,
    list_host_realizable_reference_ids,
    realize_canonical_reference,
)


_RESULT_LIMIT = 30


def _catalog_snapshots() -> list[dict[str, str]]:
    host_realizable = set(list_host_realizable_reference_ids())
    browser_proving = set(list_browser_proving_reference_ids())
    result = []
    for option in list_canonical_reference_options():
        if option.id in browser_proving:
            status = "EQ4 browser-proving slice"
            proving = "true"
        elif option.id in host_realizable:
            status = "Host-realizable · browser evidence pending"
            proving = "false"
        else:
            status = "Canonical · host realization pending"
            proving = "false"
        result.append(
            {
                "id": option.id,
                "display_name": option.display_name,
                "family": option.family,
                "category": option.category,
                "lineage": option.lineage,
                "status": status,
                "host_ready": "true" if option.id in host_realizable else "false",
                "proving": proving,
            }
        )
    return result


def _filter_catalog(options: list[dict[str, str]], query: str) -> list[dict[str, str]]:
    text = str(query or "").strip().casefold()
    if not text:
        return list(options[:_RESULT_LIMIT])
    terms = tuple(item for item in text.split() if item)
    result = []
    for option in options:
        haystack = " ".join(
            str(option.get(key, ""))
            for key in ("display_name", "id", "family", "category", "lineage")
        ).casefold()
        if all(term in haystack for term in terms):
            result.append(option)
        if len(result) >= _RESULT_LIMIT:
            break
    return result


class CanonicalDnaState(rx.State):
    """Per-client canonical DNA search and proving-preview state."""

    catalog: list[dict[str, str]] = _catalog_snapshots()
    query: str = ""
    selected_reference_id: str = ""
    selected_display_name: str = "No canonical reference selected"
    selected_category: str = ""
    selected_status: str = ""
    selected_is_browser_proving: bool = False
    preview_viewport: str = "desktop"
    reduced_motion: bool = False
    preview_message: str = "Choose a host-realizable canonical reference to render its asset-off host plan."
    plan_ready: bool = False

    fingerprint: str = ""
    layout_flow: str = ""
    balance: str = ""
    density: str = ""
    hierarchy: str = ""
    continuity: str = ""
    motion: str = ""
    typography: str = ""
    mobile_strategy: str = ""
    active_axes: list[str] = []
    active_zones: list[str] = []
    degraded_mechanism_count: int = 0
    accessibility_applied: bool = False
    reading_sanctuary_applied: bool = False
    reduced_motion_applied: bool = False

    fixture_template: str = "matrix"
    desktop_columns: str = "repeat(2, minmax(0, 1fr))"
    support_columns: str = "repeat(2, minmax(0, 1fr))"
    gap: str = "0.85rem"
    group_gap: str = "0.9rem"
    card_padding: str = "1rem"
    group_padding: str = "1.1rem"
    card_radius: str = "8px"
    group_radius: str = "10px"
    heading_size: str = "1.35rem"
    heading_weight: str = "650"
    heading_tracking: str = "0"
    secondary_offset: str = "none"
    secondary_inset: str = "0rem"
    secondary_width: str = "100%"
    continuity_border: str = "0px solid transparent"
    transition: str = "none"
    hover_transform: str = "none"
    font_family: str = "system-ui, -apple-system, sans-serif"
    line_height: str = "1.5"
    background: str = "#F8FAFC"
    surface: str = "#FFFFFF"
    surface_alt: str = "#F1F5F9"
    text_color: str = "#0F172A"
    text_muted: str = "#475569"
    accent: str = "#334155"
    border: str = "#94A3B8"

    active_reference_id: str = ""
    active_display_name: str = ""
    active_fingerprint: str = ""

    @rx.var
    def filtered_catalog(self) -> list[dict[str, str]]:
        return _filter_catalog(self.catalog, self.query)

    @rx.var
    def catalog_total(self) -> int:
        return len(self.catalog)

    @rx.var
    def host_realizable_total(self) -> int:
        return sum(item.get("host_ready") == "true" for item in self.catalog)

    @rx.var
    def browser_proving_total(self) -> int:
        return sum(item.get("proving") == "true" for item in self.catalog)

    @rx.var
    def preview_viewport_label(self) -> str:
        if self.preview_viewport == "desktop":
            return "Simulated desktop composition"
        return "Simulated mobile composition"

    @rx.event
    def refresh_catalog(self):
        self.catalog = _catalog_snapshots()
        if self.selected_reference_id and not any(
            item["id"] == self.selected_reference_id for item in self.catalog
        ):
            self._clear_plan("Selected reference is no longer present in the canonical catalog.")

    @rx.event
    def set_query(self, value: str):
        self.query = value

    def _clear_plan(self, message: str):
        self.plan_ready = False
        self.preview_message = message
        self.fingerprint = ""
        self.layout_flow = ""
        self.balance = ""
        self.density = ""
        self.hierarchy = ""
        self.continuity = ""
        self.motion = ""
        self.typography = ""
        self.mobile_strategy = ""
        self.active_axes = []
        self.active_zones = []
        self.degraded_mechanism_count = 0
        self.accessibility_applied = False
        self.reading_sanctuary_applied = False
        self.reduced_motion_applied = False

    def _refresh_plan(self):
        if not self.selected_reference_id:
            self._clear_plan("Choose a host-realizable canonical reference to render its asset-off host plan.")
            return
        selected = next(
            (item for item in self.catalog if item["id"] == self.selected_reference_id),
            None,
        )
        if selected is None:
            self._clear_plan("Selected reference is not present in the canonical catalog.")
            return
        if selected.get("host_ready") != "true":
            self._clear_plan(
                "Canonical contract is present, but this reference has not entered host realization yet."
            )
            return

        plan = realize_canonical_reference(
            self.selected_reference_id,
            viewport=self.preview_viewport,
            asset_state="off",
            archetype_id="chat_first",
            reduced_motion=self.reduced_motion,
            accessibility_required=True,
        )
        if plan is None:
            self._clear_plan("Canonical host realization failed safely; no presentation state was applied.")
            return
        try:
            tokens = project_reflex_tokens(plan)
        except (TypeError, ValueError):
            self._clear_plan("Canonical host vocabulary was unsupported; safe preview retained.")
            return

        self.plan_ready = True
        if self.selected_is_browser_proving:
            self.preview_message = "Canonical asset-off host plan resolved for the browser-proving slice. EQ4 evidence is still explicit."
        else:
            self.preview_message = "Canonical asset-off host plan resolved. Host-realizable only; browser evidence and EQ4 credit remain pending."
        self.fingerprint = plan.source_fingerprint
        self.layout_flow = plan.layout_flow
        self.balance = plan.balance
        self.density = plan.density
        self.hierarchy = plan.hierarchy
        self.continuity = plan.continuity
        self.motion = plan.motion
        self.typography = plan.typography
        self.mobile_strategy = plan.mobile_strategy
        self.active_axes = list(plan.active_axes)
        self.active_zones = list(plan.active_zones)
        self.degraded_mechanism_count = plan.degraded_mechanism_count
        self.accessibility_applied = plan.accessibility_applied
        self.reading_sanctuary_applied = plan.reading_sanctuary_applied
        self.reduced_motion_applied = plan.reduced_motion_applied

        self.fixture_template = tokens.fixture_template
        self.desktop_columns = tokens.desktop_columns
        self.support_columns = tokens.support_columns
        self.gap = tokens.gap
        self.group_gap = tokens.group_gap
        self.card_padding = tokens.card_padding
        self.group_padding = tokens.group_padding
        self.card_radius = tokens.card_radius
        self.group_radius = tokens.group_radius
        self.heading_size = tokens.heading_size
        self.heading_weight = tokens.heading_weight
        self.heading_tracking = tokens.heading_tracking
        self.secondary_offset = tokens.secondary_offset
        self.secondary_inset = tokens.secondary_inset
        self.secondary_width = tokens.secondary_width
        self.continuity_border = tokens.continuity_border
        self.transition = tokens.transition
        self.hover_transform = tokens.hover_transform
        self.font_family = tokens.font_family
        self.line_height = tokens.line_height
        self.background = tokens.background
        self.surface = tokens.surface
        self.surface_alt = tokens.surface_alt
        self.text_color = tokens.text
        self.text_muted = tokens.text_muted
        self.accent = tokens.accent
        self.border = tokens.border

    @rx.event
    def select_reference(self, reference_id: str):
        selected = next((item for item in self.catalog if item["id"] == reference_id), None)
        if selected is None:
            return
        self.selected_reference_id = selected["id"]
        self.selected_display_name = selected["display_name"]
        self.selected_category = selected["category"]
        self.selected_status = selected["status"]
        self.selected_is_browser_proving = selected.get("proving") == "true"
        self._refresh_plan()

    @rx.event
    def set_preview_viewport(self, value: str):
        if value not in {"desktop", "mobile"}:
            return
        self.preview_viewport = value
        self._refresh_plan()

    @rx.event
    def set_reduced_motion(self, value: bool):
        self.reduced_motion = bool(value)
        self._refresh_plan()

    @rx.event
    def apply_reference(self):
        if not self.plan_ready:
            self.preview_message = "Only a host-realizable canonical plan can be applied to proving presentation state."
            return
        self.active_reference_id = self.selected_reference_id
        self.active_display_name = self.selected_display_name
        self.active_fingerprint = self.fingerprint
        self.preview_message = "Canonical host presentation applied to isolated presentation state only; no EQ4 credit implied."

    @rx.event
    def clear_reference(self):
        self.selected_reference_id = ""
        self.selected_display_name = "No canonical reference selected"
        self.selected_category = ""
        self.selected_status = ""
        self.selected_is_browser_proving = False
        self.active_reference_id = ""
        self.active_display_name = ""
        self.active_fingerprint = ""
        self._clear_plan("Canonical selection cleared; safe presentation remains available.")


__all__ = ["CanonicalDnaState", "_catalog_snapshots", "_filter_catalog"]
