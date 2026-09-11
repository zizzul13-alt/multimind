import inspect

import pytest

import multimind_reflex.canonical_projection as projection
import multimind_reflex.canonical_theme_studio as studio
from multimind_reflex.canonical_projection import project_reflex_tokens
from ui.canonical_dna_bridge import CanonicalHostRealizationPlan


def plan(**overrides):
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


def test_mapper_depends_on_vocabulary_not_reference_identity():
    first = project_reflex_tokens(plan(reference_id="one", display_name="One"))
    second = project_reflex_tokens(plan(reference_id="two", display_name="Two"))
    assert first == second
    source = inspect.getsource(projection)
    for forbidden in ("CW01", "CW02", "CW03", "CW04", "CW05", "CS07", "CS08", "CS10", "CS17"):
        assert forbidden not in source
    assert "reference_id ==" not in source


def test_layout_flow_projects_macro_distinct_host_templates():
    layouts = ("grid", "components", "grouped", "paired", "continuous", "directional", "trace")
    profiles = [project_reflex_tokens(plan(layout_flow=layout)) for layout in layouts]
    assert len({profile.fixture_template for profile in profiles}) == len(layouts)
    assert {profile.fixture_template for profile in profiles} == {
        "matrix",
        "component_hierarchy",
        "group_bands",
        "paired_blocks",
        "continuous_surface",
        "directional_path",
        "trace_timeline",
    }


def test_structural_vocab_changes_visible_scalar_projection():
    ordered = project_reflex_tokens(plan())
    dense = project_reflex_tokens(plan(layout_flow="grouped", density="compact", hierarchy="strong"))
    organic = project_reflex_tokens(plan(layout_flow="continuous", balance="organic", density="spacious", hierarchy="soft"))
    directional = project_reflex_tokens(plan(layout_flow="directional", balance="asymmetric", hierarchy="dramatic", motion="directional", typography="directional"))
    assert len({ordered, dense, organic, directional}) == 4
    assert dense.card_padding != organic.card_padding
    assert organic.card_radius != directional.card_radius
    assert directional.heading_weight != ordered.heading_weight
    assert directional.hover_transform != ordered.hover_transform
    assert ordered.fixture_template != dense.fixture_template != organic.fixture_template != directional.fixture_template


def test_balance_projects_mobile_safe_macro_inset_not_micro_transform_only():
    ordered = project_reflex_tokens(plan(balance="ordered"))
    asymmetric = project_reflex_tokens(plan(balance="asymmetric"))
    organic = project_reflex_tokens(plan(balance="organic"))
    assert ordered.secondary_inset == "0rem"
    assert ordered.secondary_width == "100%"
    assert asymmetric.secondary_inset != ordered.secondary_inset
    assert asymmetric.secondary_width != ordered.secondary_width
    assert organic.secondary_inset != ordered.secondary_inset
    assert organic.secondary_width != ordered.secondary_width


def test_renderer_branches_only_on_host_vocabulary_not_reference_identity():
    source = inspect.getsource(studio)
    for forbidden in ("CW01", "CW02", "CW03", "CW04", "CW05", "CS07", "CS08", "CS10", "CS17"):
        assert forbidden not in source
    assert "selected_reference_id ==" not in source
    assert "fixture_template ==" in source
    assert "mobile_strategy ==" in source
    for template in (
        "matrix",
        "component_hierarchy",
        "group_bands",
        "paired_blocks",
        "continuous_surface",
        "directional_path",
        "trace_timeline",
    ):
        assert template in source
    for strategy in (
        "ordered_flow",
        "component_reflow",
        "serial_groups",
        "serial_clusters",
        "stack_pairs",
        "ordered_asymmetry",
        "reduced_continuity",
        "vertical_punctuation",
        "linear_trace",
    ):
        assert strategy in source


def test_mobile_renderer_is_not_desktop_one_column_fallback():
    source = inspect.getsource(studio)
    assert "preview_viewport == \"mobile\"" in source
    assert "_mobile_structural_fixture" in source
    assert "_desktop_structural_fixture" in source
    assert "rx.breakpoints" not in source
    assert 'grid_template_columns="1fr"' not in source


def test_continuity_is_visibly_projected_without_changing_semantic_content():
    none = project_reflex_tokens(plan(continuity="none"))
    state = project_reflex_tokens(plan(continuity="state"))
    service = project_reflex_tokens(plan(continuity="service"))
    language = project_reflex_tokens(plan(continuity="language"))
    knowledge = project_reflex_tokens(plan(continuity="knowledge"))
    assert len({item.continuity_border for item in (none, state, service, language, knowledge)}) == 5


def test_proving_mapper_keeps_one_accessible_neutral_palette_until_asset_color_eq4_is_authorized():
    profiles = [
        project_reflex_tokens(plan(layout_flow=layout))
        for layout in ("grid", "components", "grouped", "paired", "continuous", "directional", "trace")
    ]
    palettes = {(p.background, p.surface, p.text, p.accent, p.border) for p in profiles}
    assert len(palettes) == 1
    assert next(iter(palettes)) == ("#F8FAFC", "#FFFFFF", "#0F172A", "#334155", "#94A3B8")


def test_unknown_vocabulary_fails_closed_instead_of_genericizing_silently():
    with pytest.raises(ValueError, match="unsupported canonical host vocabulary"):
        project_reflex_tokens(plan(layout_flow="made-up-layout"))
