"""Regression locks for canonical 160 → Theme Studio → real workspace seam."""
from __future__ import annotations

import inspect

import multimind_reflex.multimind_reflex as surface
import multimind_reflex.workspace_dna_state as dna_state


STATE = inspect.getsource(dna_state)
SURFACE = inspect.getsource(surface)
WORKSPACE = inspect.getsource(surface._workspace)


def test_canonical_catalog_is_consumed_through_optional_public_bridge():
    assert "list_canonical_reference_options" in STATE
    assert "list_host_realizable_reference_ids" in STATE
    assert "realize_canonical_reference" in STATE
    assert "project_reflex_tokens" in STATE
    assert "design_dna" not in STATE


def test_theme_studio_exposes_searchable_canonical_catalog_and_explicit_legacy_fallback():
    for token in (
        'rx.heading("Canonical Reference DNA"',
        'rx.badge("Canonical 160"',
        "HostState.canonical_query",
        "HostState.filtered_canonical_catalog",
        "HostState.select_canonical_reference",
        '"Use legacy role-based composition"',
        "HostState.use_legacy_dna",
    ):
        assert token in SURFACE


def test_canonical_apply_is_explicit_and_draft_isolated():
    assert "draft_dna_mode" in STATE
    assert "active_dna_mode" in STATE
    assert "def apply_composed_theme" in STATE
    assert "self._copy_draft_to_active()" in STATE
    assert "self._copy_canonical_draft_to_active()" in STATE
    assert 'self.current_surface = "workspace"' in STATE
    assert "HostState.apply_composed_theme" in SURFACE
    assert "Draft only — active workspace unchanged" in SURFACE


def test_canonical_workspace_uses_finite_structural_vocabulary_not_reference_ids():
    for token in (
        "_canonical_workspace_desktop_columns",
        "_canonical_workspace_desktop_areas",
        "_canonical_workspace_mobile_areas",
        "HostState.active_canonical_layout_flow",
        "HostState.active_canonical_mobile_strategy",
        '"grid"',
        '"components"',
        '"grouped"',
        '"paired"',
        '"continuous"',
        '"directional"',
        '"ordered_flow"',
        '"component_reflow"',
        '"serial_groups"',
        '"serial_clusters"',
        '"stack_pairs"',
        '"ordered_asymmetry"',
        '"reduced_continuity"',
        '"vertical_punctuation"',
    ):
        assert token in SURFACE

    for forbidden in (
        "CW01",
        "CW02",
        "CW03",
        "CW04",
        "CW05",
        "CS07",
        "CS08",
        "CS10",
        "CS17",
        "IZA07",
        "MR-023",
    ):
        assert forbidden not in SURFACE
        assert forbidden not in STATE


def test_workspace_still_instantiates_one_set_of_application_facing_zones():
    for call in (
        "_workspace_utility_zone()",
        "_workspace_composer_zone()",
        "_workspace_result_zone()",
        "_workspace_history_zone()",
    ):
        assert WORKSPACE.count(call) == 1

    # Canonical DNA changes composition only. The single upload, restore and Run
    # event paths remain unchanged rather than being copied per reference.
    assert SURFACE.count("id=UPLOAD_ID,") == 1
    assert SURFACE.count("id=RESTORE_ID,") == 1
    assert SURFACE.count("on_click=HostState.run_chat") == 1


def test_canonical_seam_does_not_claim_application_or_persistence_ownership():
    # Mentioning the stable application boundary in documentation is allowed;
    # importing/constructing application, orchestration, persistence or network
    # owners from this presentation-only extension is not.
    for forbidden in (
        "from core.application import MultiMindApplication",
        "MultiMindApplication(",
        "from core.orchestrator import DebateOrchestrator",
        "DebateOrchestrator(",
        "Config.get_db_path",
        "database.manager",
        "sqlite3.connect(",
        "requests.post(",
        "httpx.post(",
        "FastAPI",
    ):
        assert forbidden not in STATE


def test_canonical_failure_retains_legacy_or_neutral_path():
    assert "Canonical realization failed safely; legacy presentation retained" in STATE
    assert "Canonical vocabulary unsupported; legacy presentation retained" in STATE
    assert "def _restore_legacy_draft" in STATE
    assert "self._set_neutral_theme_draft()" in STATE


def test_canonical_token_projection_reaches_real_workspace_surface():
    for token in (
        "HostState.active_canonical_card_radius",
        "HostState.active_canonical_card_padding",
        "HostState.active_canonical_gap",
        "HostState.active_canonical_font_family",
        "HostState.active_canonical_line_height",
    ):
        assert token in SURFACE
