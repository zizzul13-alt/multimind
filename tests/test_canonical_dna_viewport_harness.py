import inspect

import multimind_reflex.canonical_theme_studio as studio


MOBILE_STRATEGIES = (
    "ordered_flow",
    "component_reflow",
    "serial_groups",
    "serial_clusters",
    "stack_pairs",
    "ordered_asymmetry",
    "reduced_continuity",
    "vertical_punctuation",
    "linear_trace",
)


def test_proving_renderer_uses_selected_viewport_not_browser_breakpoints():
    source = inspect.getsource(studio)
    assert "rx.breakpoints" not in source
    assert 'CanonicalDnaState.preview_viewport == "mobile"' in source
    assert "_mobile_structural_fixture()" in source
    assert "_desktop_structural_fixture()" in source
    assert "overflow_x=\"auto\"" in source


def test_mobile_renderer_consumes_all_canonical_mobile_strategies_structurally():
    source = inspect.getsource(studio)
    for strategy in MOBILE_STRATEGIES:
        assert f'CanonicalDnaState.mobile_strategy == "{strategy}"' in source or strategy == "linear_trace"
    # Final fallthrough is the ninth finite vocabulary member; no reference IDs
    # may select a mobile layout branch.
    assert "_mobile_linear_trace()" in source
    assert "selected_reference_id ==" not in source
    for forbidden in ("CW01", "CW02", "CW03", "CW04", "CW05", "CS07", "CS08", "CS10", "CS17"):
        assert forbidden not in source


def test_mobile_is_not_implemented_as_desktop_grid_collapse():
    source = inspect.getsource(studio)
    # Mobile must have its own semantic structures, not a 1fr override of the
    # desktop grid/template path.
    assert "_mobile_ordered_flow" in source
    assert "_mobile_component_reflow" in source
    assert "_mobile_serial_groups" in source
    assert "grid_template_columns=CanonicalDnaState.preview_primary_columns" not in source
    assert "grid_template_columns=CanonicalDnaState.preview_support_columns" not in source
