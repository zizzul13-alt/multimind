"""Regression locks for phone-first workspace / Theme Studio polish."""
from __future__ import annotations

import inspect
from pathlib import Path

import multimind_reflex.canonical_projection as projection
import multimind_reflex.workspace_dna_state as dna_state
from multimind_reflex.canonical_projection import project_reflex_tokens
from ui.canonical_dna_bridge import CanonicalHostRealizationPlan


ROOT = Path(__file__).resolve().parents[1]
DNA_STATE_SOURCE = (ROOT / "multimind_reflex" / "workspace_dna_state.py").read_text(encoding="utf-8")


def _plan(**overrides):
    values = dict(
        reference_id="opaque-reference",
        display_name="Opaque Reference",
        source_fingerprint="fingerprint",
        viewport="desktop",
        archetype_id="chat_first",
        layout_flow="grid",
        balance="ordered",
        density="comfortable",
        hierarchy="measured",
        continuity="none",
        motion="static",
        typography="measured",
        mobile_strategy="ordered_flow",
        active_axes=("INFORMATION",),
        active_zones=("U3_PRIMARY_WORK_SURFACE",),
        degraded_mechanism_count=0,
        accessibility_applied=False,
        reading_sanctuary_applied=False,
        reduced_motion_applied=False,
    )
    values.update(overrides)
    return CanonicalHostRealizationPlan(**values)


def test_canonical_picker_keeps_phone_result_window_bounded():
    assert dna_state._CANONICAL_RESULT_LIMIT == 12
    catalog = [
        {
            "id": f"R{index:03d}",
            "display_name": f"Reference {index}",
            "family": "family",
            "category": "category",
            "lineage": "lineage",
            "host_ready": "true",
        }
        for index in range(40)
    ]
    assert len(dna_state._filter_canonical_catalog(catalog, "")) == 12


def test_successful_reference_tap_collapses_picker_to_selected_identity():
    # Reflex wraps @rx.event methods as EventHandler objects at import time, so
    # lock the authored source contract rather than introspecting the wrapper.
    assert 'self.canonical_query = selected["id"]' in DNA_STATE_SOURCE
    assert "Canonical draft selected:" in DNA_STATE_SOURCE


def test_legacy_reset_and_logout_clear_canonical_search_context():
    assert DNA_STATE_SOURCE.count('self.canonical_query = ""') >= 4


def test_canonical_density_tokens_are_responsive_without_browser_truth_branching():
    for density in ("compact", "comfortable", "spacious"):
        tokens = project_reflex_tokens(_plan(density=density))
        for value in (tokens.gap, tokens.card_padding, tokens.group_gap, tokens.group_padding):
            assert value.startswith("clamp(")

    source = inspect.getsource(projection)
    assert "window.innerWidth" not in source
    assert "matchMedia" not in source
    assert "reference_id ==" not in source


def test_asymmetric_inset_remains_structural_but_phone_safe():
    asymmetric = project_reflex_tokens(_plan(balance="asymmetric"))
    organic = project_reflex_tokens(_plan(balance="organic"))
    assert asymmetric.secondary_inset.startswith("clamp(")
    assert organic.secondary_inset.startswith("clamp(")
    assert "clamp(" in asymmetric.secondary_width
    assert "clamp(" in organic.secondary_width
