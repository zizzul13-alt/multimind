"""Presentation-only regression locks for the bounded mobile polish pass."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SURFACE = (ROOT / "multimind_reflex" / "multimind_reflex.py").read_text(encoding="utf-8")
STATE = (ROOT / "multimind_reflex" / "workspace_dna_state.py").read_text(encoding="utf-8")


def test_mobile_polish_keeps_one_execution_control_and_one_theme_apply_control():
    assert SURFACE.count("on_click=HostState.run_chat") == 1
    assert SURFACE.count("on_click=HostState.apply_composed_theme") == 1
    assert SURFACE.count('"Apply Composition"') == 1


def test_mobile_primary_actions_are_reachable_without_new_application_paths():
    assert "def _primary_run_button" in SURFACE
    assert "def _theme_studio_actions" in SURFACE
    assert 'position=rx.breakpoints(initial="sticky", md="static")' in SURFACE
    assert 'bottom=rx.breakpoints(initial="0.5rem", md="auto")' in SURFACE
    assert 'min_height="3rem"' in SURFACE
    assert 'min_height="2.75rem"' in SURFACE


def test_mobile_polish_handles_long_ai_and_metadata_text_without_horizontal_truth_loss():
    assert 'overflow_wrap="anywhere"' in SURFACE
    assert 'white_space="pre-wrap"' in SURFACE
    assert 'overflow_x="hidden"' in SURFACE
    assert 'line_height="1.65"' in SURFACE


def test_workspace_still_consumes_canonical_and_archetype_mobile_grammar():
    assert "_canonical_workspace_mobile_areas()" in SURFACE
    assert "_workspace_mobile_areas()" in SURFACE
    assert "HostState.active_canonical_mobile_strategy" in SURFACE
    assert "HostState.active_archetype" in SURFACE
    assert 'initial=rx.cond(' in SURFACE


def test_polish_does_not_duplicate_core_provider_or_persistence_truth():
    combined = SURFACE + STATE
    for forbidden in (
        "DebateOrchestrator",
        "sqlite3.connect(",
        "FastAPI",
        "requests.post(",
        "httpx.post(",
    ):
        assert forbidden not in combined


def test_theme_studio_catalog_is_mobile_bounded_not_removed():
    assert "HostState.filtered_canonical_catalog" in SURFACE
    assert 'max_height=rx.breakpoints(initial="14rem", md="20rem")' in SURFACE
    assert 'padding=rx.breakpoints(initial="0.5rem", sm="1rem", md="1.5rem")' in SURFACE
