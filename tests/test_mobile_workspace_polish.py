from pathlib import Path

import rxconfig
from multimind_reflex import mobile_entry
from multimind_reflex import multimind_reflex as surface


ROOT = Path(__file__).resolve().parents[1]
ENTRY = (ROOT / "multimind_reflex" / "mobile_entry.py").read_text(encoding="utf-8")
SURFACE = (ROOT / "multimind_reflex" / "multimind_reflex.py").read_text(encoding="utf-8")
CSS = (ROOT / "assets" / "mobile-workspace-polish.css").read_text(encoding="utf-8")


def test_reflex_uses_mobile_polish_entry_without_replacing_app_instance():
    assert rxconfig.config.app_module_import == "multimind_reflex.mobile_entry"
    assert mobile_entry.app is surface.app
    assert "/mobile-workspace-polish.css" in mobile_entry.app.stylesheets


def test_mobile_polish_keeps_touch_targets_and_text_inputs_phone_safe():
    style = mobile_entry.app.style
    assert style["button"]["min_height"] == "2.75rem"
    assert style["input"]["font_size"] == "1rem"
    assert style["textarea"]["font_size"] == "1rem"
    assert style["select"]["font_size"] == "1rem"
    assert style["body"]["overflow_x"] == "hidden"
    assert style["p"]["overflow_wrap"] == "anywhere"
    assert "@media (max-width: 48em)" in style


def test_stylesheet_targets_real_semantic_zones_instead_of_dead_classes_or_dna_ids():
    for area in ("utility", "composer", "result", "history"):
        assert f"grid-area: {area}" in CSS

    # The accepted surface remains the only place that instantiates the zones.
    for token in (
        '_workspace_utility_zone()',
        '_workspace_composer_zone()',
        '_workspace_result_zone()',
        '_workspace_history_zone()',
    ):
        assert token in SURFACE

    for forbidden in ("CW01", "CW02", "CW03", "CS10", "CS17", "IZA07", "MR-"):
        assert forbidden not in CSS
        assert forbidden not in ENTRY


def test_mobile_polish_is_presentation_only():
    combined = ENTRY + CSS
    for forbidden in (
        "MultiMindApplication",
        "DebateOrchestrator",
        "sqlite3.connect(",
        "build_host_application",
        "execute_chat",
        "restore_database",
        "requests.post(",
        "httpx.post(",
        "FastAPI",
    ):
        assert forbidden not in combined


def test_phone_readability_reachable_actions_and_reduced_motion_are_explicit():
    assert "@media (max-width: 767px)" in CSS
    assert "min-height: 2.875rem" in CSS
    assert "min-height: 8.5rem" in CSS
    assert "overflow-wrap: anywhere" in CSS
    assert ".mm-theme-actions" in CSS
    assert "position: sticky" in CSS
    assert ".mm-run-button" in CSS
    assert ".mm-result-card" in CSS
    assert ".mm-participant-card" in CSS
    assert ".mm-history-card" in CSS
    assert "@media (prefers-reduced-motion: reduce)" in CSS


def test_deliberation_polish_improves_scanability_without_hiding_evidence():
    for token in (
        ".mm-readable",
        "max-width: 78ch",
        ".mm-result-card",
        ".mm-participant-card",
        ".mm-critique-card",
        ".mm-history-card",
        "border-inline-start",
        "scroll-margin-block",
    ):
        assert token in CSS

    # Presentation may group and visually separate evidence, but it must not
    # hide, truncate, reorder, or replace participant/judge/history truth.
    lowered = CSS.casefold()
    for forbidden in (
        "display: none",
        "visibility: hidden",
        "text-overflow: ellipsis",
        "line-clamp",
        "order:",
    ):
        assert forbidden not in lowered


def test_existing_workspace_and_theme_studio_remain_owners():
    assert "from multimind_reflex.multimind_reflex import app" in ENTRY
    assert "def _workspace()" in SURFACE
    assert "def _theme_studio()" in SURFACE
    assert "WorkspaceDnaState as HostState" in SURFACE