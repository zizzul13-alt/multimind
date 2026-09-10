"""Search-friendly Reflex picker for the optional Design-DNA catalog.

The catalog remains owned by the optional private Design-DNA bridge. This module
only keeps presentation search text/results and routes selected IDs back through
HostState validation. It intentionally does not invent DNA semantics or make
canonical non-renderable references selectable.
"""
from __future__ import annotations

import reflex as rx

from multimind_reflex.state import HostState
from ui.dna_bridge import list_theme_studio_dna_options


_RESULT_LIMIT = 24
_NONE_WEB_OPTION = {
    "id": "",
    "display_name": "None (Default information density)",
    "category": "default",
}


def _option_snapshot(option) -> dict[str, str]:
    return {
        "id": str(option.id),
        "display_name": str(option.display_name),
        "category": str(option.category or "uncategorized"),
    }


def _load_options(role: str) -> list[dict[str, str]]:
    return [_option_snapshot(option) for option in list_theme_studio_dna_options(role)]


def _filter_options(
    options: list[dict[str, str]],
    query: str,
    *,
    limit: int = _RESULT_LIMIT,
) -> list[dict[str, str]]:
    """Deterministic case-insensitive search across name, ID, and category."""
    normalized = str(query or "").strip().casefold()
    if not normalized:
        return list(options[:limit])
    terms = tuple(part for part in normalized.split() if part)
    matches = []
    for option in options:
        haystack = " ".join(
            (
                str(option.get("display_name", "")),
                str(option.get("id", "")),
                str(option.get("category", "")),
            )
        ).casefold()
        if all(term in haystack for term in terms):
            matches.append(option)
    return matches[:limit]


class DnaCatalogSearchState(rx.State):
    """Host-only search state; Design-DNA truth remains behind ui.dna_bridge."""

    identity_query: str = ""
    web_query: str = ""
    identity_options: list[dict[str, str]] = _load_options("identity")
    web_options: list[dict[str, str]] = [_NONE_WEB_OPTION] + _load_options("web_information")

    @rx.var
    def filtered_identity_options(self) -> list[dict[str, str]]:
        return _filter_options(self.identity_options, self.identity_query)

    @rx.var
    def filtered_web_options(self) -> list[dict[str, str]]:
        return _filter_options(self.web_options, self.web_query)

    @rx.var
    def identity_total(self) -> int:
        return len(self.identity_options)

    @rx.var
    def web_total(self) -> int:
        return max(0, len(self.web_options) - 1)

    @rx.event
    def set_identity_query(self, value: str):
        self.identity_query = value

    @rx.event
    def set_web_query(self, value: str):
        self.web_query = value


def _identity_option(option) -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.vstack(
                rx.text(option["display_name"], weight="bold", text_align="left"),
                rx.text(option["id"], size="1", text_align="left"),
                align="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.cond(
                option["id"] == HostState.draft_identity_dna,
                rx.badge("Selected"),
                rx.badge(option["category"], variant="soft"),
            ),
            width="100%",
            align="center",
        ),
        on_click=HostState.set_draft_identity_dna(option["id"]),
        variant="soft",
        width="100%",
        height="auto",
        padding="0.65rem",
    )


def _web_option(option) -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.vstack(
                rx.text(option["display_name"], weight="bold", text_align="left"),
                rx.cond(option["id"] != "", rx.text(option["id"], size="1", text_align="left")),
                align="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.cond(
                option["id"] == HostState.draft_web_dna,
                rx.badge("Selected"),
                rx.badge(option["category"], variant="soft"),
            ),
            width="100%",
            align="center",
        ),
        on_click=HostState.set_draft_web_dna(option["id"]),
        variant="soft",
        width="100%",
        height="auto",
        padding="0.65rem",
    )


def identity_dna_picker() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Selected: ",
            HostState.draft_identity_display_name,
            " · ",
            DnaCatalogSearchState.identity_total,
            " render-ready",
            size="2",
        ),
        rx.input(
            placeholder="Search Identity DNA by name, ID, or category…",
            value=DnaCatalogSearchState.identity_query,
            on_change=DnaCatalogSearchState.set_identity_query,
            width="100%",
        ),
        rx.box(
            rx.vstack(
                rx.foreach(DnaCatalogSearchState.filtered_identity_options, _identity_option),
                rx.cond(
                    DnaCatalogSearchState.filtered_identity_options.length() == 0,
                    rx.text("No matching render-ready Identity DNA.", size="2"),
                ),
                spacing="2",
                width="100%",
            ),
            max_height="18rem",
            overflow_y="auto",
            width="100%",
        ),
        width="100%",
        spacing="2",
    )


def web_dna_picker() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Selected: ",
            HostState.draft_web_display_name,
            " · ",
            DnaCatalogSearchState.web_total,
            " render-ready",
            size="2",
        ),
        rx.input(
            placeholder="Search Web / Information DNA by name, ID, or category…",
            value=DnaCatalogSearchState.web_query,
            on_change=DnaCatalogSearchState.set_web_query,
            width="100%",
        ),
        rx.box(
            rx.vstack(
                rx.foreach(DnaCatalogSearchState.filtered_web_options, _web_option),
                rx.cond(
                    DnaCatalogSearchState.filtered_web_options.length() == 0,
                    rx.text("No matching render-ready Web / Information DNA.", size="2"),
                ),
                spacing="2",
                width="100%",
            ),
            max_height="18rem",
            overflow_y="auto",
            width="100%",
        ),
        width="100%",
        spacing="2",
    )


__all__ = [
    "DnaCatalogSearchState",
    "_filter_options",
    "identity_dna_picker",
    "web_dna_picker",
]
