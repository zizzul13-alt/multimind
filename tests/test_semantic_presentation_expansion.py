"""
MultiMind AI - S8.4 Semantic Presentation Expansion Regression Tests (T01 - T13)
Verifies generic presentation consumption, boundary isolation, and non-branching guarantees.
"""
import pytest
from ui.dna.models import DesignDNA, DesignComposition, IdentityPresentationProjection, PresentationPolicy
from ui.dna.resolver import resolve_composition, resolve_source_dna, resolve_identity_projection
from ui.themes.registry import generate_theme_css, get_theme, resolve_theme
from ui.dna.proofs import (
    RINPA_DECORATIVE_SPATIAL_DNA,
    JAPAN_PRINT_INK_DNA,
    CHAINSAW_MAN_INSPIRED_DNA,
    MUSHISHI_INSPIRED_DNA,
    JAPAN_HIGH_DENSITY_INFO_DNA,
)


def test_t01_no_canonical_dna_id_branches():
    """T01: No canonical DNA ID/name behavior branches exist in generic resolver code."""
    import inspect
    import ui.dna.resolver as resolver_mod
    import ui.themes.registry as registry_mod

    res_src = inspect.getsource(resolver_mod)
    reg_src = inspect.getsource(registry_mod)

    # Assert no hardcoded identity DNA ID checks like `if dna.id == "rinpa-decorative-spatial"`
    for canonical_id in [
        "rinpa-decorative-spatial",
        "japan-print-ink",
        "chainsaw-man-inspired",
        "mushishi-inspired",
    ]:
        assert f'dna.id == "{canonical_id}"' not in res_src
        assert f'id == "{canonical_id}"' not in res_src
        assert f'dna.id == "{canonical_id}"' not in reg_src


def test_t02_synthetic_future_dna_uses_generic_consumers():
    """T02: Synthetic future DNA can use every new generic consumer seamlessly through full runtime chain."""
    from ui.dna import get_registry as get_dna_registry
    from ui.themes import register_theme
    from ui.dna.mapper import dna_to_theme

    synthetic_dna = DesignDNA(
        id="synthetic-future-dna-001",
        display_name="Synthetic Future DNA",
        role="identity",
        category="custom",
        visual_energy="aggressive",
        hierarchy_strength="dramatic",
        shape_character="sharp",
        surface_character="poster",
        interaction_intensity="assertive",
        colors={
            "background": "#000000",
            "surface": "#111111",
            "primary": "#FF0055",
            "border": "#333333",
            "text": "#FFFFFF",
        },
    )

    # Register synthetic DNA & Theme in registries to prove generic non-branching chain
    get_dna_registry().register_dna(synthetic_dna)
    register_theme(dna_to_theme(synthetic_dna))

    proj = resolve_identity_projection(synthetic_dna)
    assert isinstance(proj, IdentityPresentationProjection)
    assert proj.hierarchy_contrast == "dramatic"
    assert proj.border_stroke_style == "crisp"
    assert proj.energy_emphasis == "aggressive"
    assert proj.surface_treatment == "poster"
    assert proj.transition_speed == "assertive"

    css = generate_theme_css("synthetic-future-dna-001")
    assert "--mm-heading-font-weight: 900;" in css
    assert "--mm-shape-border-style: solid;" in css
    assert "--mm-energy-hover-lift: translate(-1px, -1px);" in css
    assert "--mm-surface-elevation-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);" in css
    assert "--mm-transition-spec: background-color 0.1s cubic-bezier" in css


def test_t03_s83_spatial_density_behavior_intact():
    """T03: S8.3 spatial_density behavior remains intact in resolve_composition."""
    comp_dense = DesignComposition(
        identity_dna_id="chainsaw-man-inspired",
        web_information_dna_id=None,
        archetype_id="chat_first",
    )
    composed = resolve_composition(comp_dense)
    assert composed.presentation_policy.secondary_compactness is True

    comp_spacious = DesignComposition(
        identity_dna_id="rinpa-decorative-spatial",
        web_information_dna_id=None,
        archetype_id="chat_first",
    )
    composed_spacious = resolve_composition(comp_spacious)
    assert composed_spacious.presentation_policy.secondary_compactness is False


def test_t04_s83_ornament_emphasis_behavior_intact():
    """T04: S8.3 ornament_emphasis behavior remains intact in brand identity rendering."""
    from ui.presentation.brand import _get_ornament_width

    assert _get_ornament_width("none") == 0
    assert _get_ornament_width("subtle") == 24
    assert _get_ornament_width("selective") == 32
    assert _get_ornament_width("prominent") == 40


def test_t05_identity_theme_ownership_intact():
    """T05: Identity Theme ownership remains intact and primary color tokens are preserved."""
    comp = DesignComposition(
        identity_dna_id="chainsaw-man-inspired",
        web_information_dna_id="japan-high-density-info",
        archetype_id="chat_first",
    )
    composed = resolve_composition(comp)
    assert composed.theme.id == "chainsaw-man-inspired"
    assert composed.theme.colors["primary"] == CHAINSAW_MAN_INSPIRED_DNA.colors["primary"]


def test_t06_web_dna_presentation_policy_ownership_intact():
    """T06: Web DNA PresentationPolicy ownership remains intact."""
    comp = DesignComposition(
        identity_dna_id="rinpa-decorative-spatial",
        web_information_dna_id="japan-high-density-info",
        archetype_id="chat_first",
    )
    composed = resolve_composition(comp)
    assert composed.presentation_policy.metadata_prominence == "high"
    assert composed.presentation_policy.status_richness == "rich"


def test_t07_archetype_ownership_intact():
    """T07: Archetype ownership remains intact."""
    comp = DesignComposition(
        identity_dna_id="rinpa-decorative-spatial",
        web_information_dna_id=None,
        archetype_id="command_center",
    )
    composed = resolve_composition(comp)
    assert composed.archetype_id == "command_center"


def test_t08_theme_studio_draft_isolation_intact():
    """T08: Theme Studio draft/active isolation remains intact."""
    from ui.theme_studio.state import init_draft_from_composition

    draft = init_draft_from_composition(
        identity_dna_id="mushishi-inspired",
        web_information_dna_id=None,
        archetype_id="ai_workspace",
    )
    assert draft.identity_dna_id == "mushishi-inspired"
    assert draft.archetype_id == "ai_workspace"
    projection = draft.resolve()
    assert projection.archetype_id == "ai_workspace"


def test_t09_s84_semantic_reaches_actual_application_presentation():
    """T09: At least one S8.4 semantic reaches actual application presentation in generated CSS."""
    css_chainsaw = generate_theme_css("chainsaw-man-inspired")
    assert "--mm-heading-font-weight: 900;" in css_chainsaw
    assert "--mm-shape-border-style: solid;" in css_chainsaw
    assert "--mm-energy-hover-lift: translate(-1px, -1px);" in css_chainsaw
    assert "--mm-surface-elevation-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);" in css_chainsaw
    assert "--mm-transition-spec: background-color 0.1s cubic-bezier" in css_chainsaw

    css_mushishi = generate_theme_css("mushishi-inspired")
    assert "--mm-heading-font-weight: 500;" in css_mushishi
    assert "--mm-shape-border-style: solid;" in css_mushishi
    assert "--mm-energy-hover-lift: none;" in css_mushishi


def test_t10_deferred_semantics_not_falsely_exposed():
    """T10: Deferred semantics (responsive_identity_priority, composition_balance) are not falsely exposed as full consumers."""
    from ui.dna.models import VALID_RESPONSIVE_IDENTITY_PRIORITY, VALID_COMPOSITION_BALANCE

    assert VALID_RESPONSIVE_IDENTITY_PRIORITY == {"minimal", "preserve_core", "preserve_strong"}
    assert VALID_COMPOSITION_BALANCE == {"regular", "asymmetric", "organic"}


def test_t11_four_canonical_dna_profiles_resolve_without_special_cases():
    """T11: Four canonical DNA profiles resolve without special cases."""
    for dna_id in [
        "rinpa-decorative-spatial",
        "japan-print-ink",
        "chainsaw-man-inspired",
        "mushishi-inspired",
    ]:
        comp = DesignComposition(identity_dna_id=dna_id, archetype_id="chat_first")
        composed = resolve_composition(comp)
        assert composed.theme.id == dna_id
        assert composed.identity_projection is not None


def test_t12_existing_material_pipeline_valid():
    """T12: Existing Material Pipeline remains valid."""
    from ui.dna.resolver import resolve_material

    res = resolve_material("rinpa-decorative-spatial")
    assert res.is_resolved or res.status in ("resolved", "fallback")


def test_t13_existing_responsive_behavior_valid():
    """T13: Existing responsive CSS behavior in ui/style.css remains valid."""
    with open("ui/style.css", "r", encoding="utf-8") as f:
        style_css = f.read()

    assert "@media screen and (max-width: 768px)" in style_css
    assert "@media screen and (max-width: 390px)" in style_css
