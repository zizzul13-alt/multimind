import inspect

import multimind_reflex.canonical_theme_studio as studio
from multimind_reflex.canonical_dna_state import CanonicalDnaState


def test_proving_renderer_uses_selected_viewport_not_browser_breakpoints():
    source = inspect.getsource(studio)
    assert "rx.breakpoints" not in source
    assert "CanonicalDnaState.preview_primary_columns" in source
    assert "CanonicalDnaState.preview_support_columns" in source
    assert "overflow_x=\"auto\"" in source


def test_viewport_computed_vars_have_explicit_desktop_and_mobile_paths():
    primary = inspect.getsource(CanonicalDnaState.preview_primary_columns.fget)
    support = inspect.getsource(CanonicalDnaState.preview_support_columns.fget)
    for source in (primary, support):
        assert 'preview_viewport == "desktop"' in source
        assert 'return "1fr"' in source
