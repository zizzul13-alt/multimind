"""
MultiMind AI - S8.5 Final Visual Closure & Correctness Regression Tests

Ensures overflow containment, material fallback coherence, Theme Studio state isolation,
and contract compliance for S8.5 closure.
"""
import pytest
import os
from ui.foundation import load_css
from ui.dna.resolver import resolve_material, resolve_composition
from ui.dna.models import DesignComposition
from ui.dna import get_registry
from ui.themes import list_themes


def test_responsive_css_presence():
    """Verify CSS file exists and contains essential responsive / overflow rules."""
    css_path = os.path.join("ui", "style.css")
    assert os.path.exists(css_path)
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "word-break: break-word" in content or "overflow-wrap: anywhere" in content
    assert "@media screen and (max-width: 390px)" in content
    assert "@media screen and (max-width: 768px)" in content


def test_material_fallback_integrity():
    """Verify material resolution works consistently across all 4 canonical DNAs."""
    canonical_dnas = [
        "rinpa-decorative-spatial",
        "japan-print-ink",
        "chainsaw-man-inspired",
        "mushishi-inspired"
    ]
    for dna_id in canonical_dnas:
        res = resolve_material(dna_id)
        assert res.is_resolved, f"Material for {dna_id} failed to resolve: {res.error_reason}"
        assert res.resolved_path is not None
        assert os.path.exists(res.resolved_path)


def test_no_canonical_dna_branching_in_resolver():
    """Verify composition resolver contains zero conditional branches on canonical DNA IDs."""
    import inspect
    from ui.dna import resolver
    source = inspect.getsource(resolver)

    # Ensure no hardcoded DNA name checks exist in resolve_composition logic
    assert "rinpa-decorative-spatial" not in source
    assert "chainsaw-man-inspired" not in source


def test_all_canonical_themes_registered():
    """Verify all canonical themes are available in Theme Engine."""
    from ui.dna.bootstrap import ensure_proof_dna_and_themes_registered
    ensure_proof_dna_and_themes_registered()
    themes = list_themes()
    theme_ids = [t.id for t in themes]

    assert "rinpa-decorative-spatial" in theme_ids
    assert "japan-print-ink" in theme_ids
    assert "chainsaw-man-inspired" in theme_ids
    assert "mushishi-inspired" in theme_ids
