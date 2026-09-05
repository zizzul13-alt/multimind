from itertools import combinations
import inspect

import pytest

import design_dna.references as m2_module
from design_dna import (
    AssetState,
    Axis,
    COUNTRY_WEB_ASSET_ON_APPLICABLE,
    COUNTRY_WEB_ASSET_ON_NOT_APPLICABLE,
    COUNTRY_WEB_REFERENCE_IDS,
    CompositionRequest,
    DNARegistry,
    DegradationState,
    FailureCode,
    M2_ASSET_ON_APPLICABLE,
    M2_ASSET_ON_NOT_APPLICABLE,
    M2_CULTURAL_ASSET_ON_APPLICABLE,
    M2_CULTURAL_REFERENCE_IDS,
    M2_PROVING_REFERENCE_IDS,
    M2_PROVING_REFERENCES,
    M2_REFERENCE_BY_ID,
    M2_REQUIRED_PRIMITIVE_IDS,
    RuntimeConstraints,
    SemanticContext,
    SemanticZone,
    UnitKind,
    Viewport,
    m2_reference_asset_on_applicable,
    register_m1_engines,
    register_m2_proving_references,
    resolve,
)


VIEWPORTS = (Viewport.DESKTOP, Viewport.TABLET, Viewport.MOBILE)
ASSET_STATES = (AssetState.AVAILABLE, AssetState.LOADING, AssetState.PARTIAL, AssetState.OFF)
REFERENCE_PAIRS = tuple(combinations(M2_PROVING_REFERENCE_IDS, 2))
TENSION_CASES = (
    ("CW03", "M3", Axis.SPACE),
    ("CS07", "M12", Axis.SPACE),
    ("CS08", "M7", Axis.FORM),
    ("CS10", "M12", Axis.SPACE),
    ("CS17", "M12", Axis.SPACE),
)


def _registry():
    registry = DNARegistry()
    register_m1_engines(registry)
    register_m2_proving_references(registry)
    return registry


def _project(
    reference_id,
    *,
    viewport=Viewport.DESKTOP,
    asset_state=AssetState.OFF,
    engine_ids=(),
    context=None,
    constraints=None,
):
    context = context or SemanticContext(viewport=viewport)
    return resolve(
        _registry(),
        CompositionRequest(
            reference_id,
            engine_ids=tuple(engine_ids),
            primitive_ids=M2_REQUIRED_PRIMITIVE_IDS,
            asset_state=asset_state,
        ),
        context,
        constraints,
    )


def _structural_signature(projection):
    return tuple(
        (item.axis, item.zone, item.viewport, item.directive, item.degradation)
        for item in projection.mechanisms
    )


def test_m2_membership_is_exact_five_country_web_plus_four_tier_s():
    assert COUNTRY_WEB_REFERENCE_IDS == ("CW01", "CW02", "CW03", "CW04", "CW05")
    assert M2_CULTURAL_REFERENCE_IDS == ("CS07", "CS08", "CS10", "CS17")
    assert M2_PROVING_REFERENCE_IDS == COUNTRY_WEB_REFERENCE_IDS + M2_CULTURAL_REFERENCE_IDS
    assert len(M2_PROVING_REFERENCES) == 9
    assert tuple(unit.id for unit in M2_PROVING_REFERENCES) == M2_PROVING_REFERENCE_IDS
    assert set(M2_REFERENCE_BY_ID) == set(M2_PROVING_REFERENCE_IDS)


def test_m2_does_not_fabricate_primitive_dependencies():
    assert M2_REQUIRED_PRIMITIVE_IDS == ()


def test_all_m2_units_are_references_and_cover_all_15_axes_explicitly():
    for unit in M2_PROVING_REFERENCES:
        assert unit.kind is UnitKind.REFERENCE
        mechanism_axes = {m.axis for m in unit.mechanisms}
        absence_axes = {a.axis for a in unit.axis_absences}
        assert mechanism_axes.isdisjoint(absence_axes)
        assert mechanism_axes | absence_axes == set(Axis)


def test_country_web_family_names_match_locked_scopes():
    expected = {
        "CW01": "Switzerland — Swiss institutional/product typographic-system lineage",
        "CW02": "USA — U.S. product-web/SaaS design-system lineage",
        "CW03": "Japan — Japanese commerce/public-service high-information lineage",
        "CW04": "China — Chinese service-platform ecosystem convergence lineage",
        "CW05": "Aotearoa New Zealand — public-cultural bilingual/bicultural integration lineage",
    }
    assert {unit_id: M2_REFERENCE_BY_ID[unit_id].family for unit_id in COUNTRY_WEB_REFERENCE_IDS} == expected


def test_cultural_subset_names_match_locked_tier_s_membership():
    expected = {
        "CS07": "Swiss International Typographic",
        "CS08": "Horta Continuous Organic",
        "CS10": "Futurist Typography",
        "CS17": "Continuous Knowledge Traversal",
    }
    assert {unit_id: M2_REFERENCE_BY_ID[unit_id].family for unit_id in M2_CULTURAL_REFERENCE_IDS} == expected


def test_country_web_asset_applicability_matches_batch7_lock():
    assert COUNTRY_WEB_ASSET_ON_APPLICABLE == {"CW01", "CW03", "CW04", "CW05"}
    assert COUNTRY_WEB_ASSET_ON_NOT_APPLICABLE == {"CW02"}
    assert M2_CULTURAL_ASSET_ON_APPLICABLE == set(M2_CULTURAL_REFERENCE_IDS)
    assert M2_ASSET_ON_NOT_APPLICABLE == {"CW02"}
    assert M2_ASSET_ON_APPLICABLE == set(M2_PROVING_REFERENCE_IDS) - {"CW02"}


@pytest.mark.parametrize("reference_id", M2_PROVING_REFERENCE_IDS)
def test_asset_applicability_helper_is_total_over_proving_slice(reference_id):
    assert m2_reference_asset_on_applicable(reference_id) is (reference_id != "CW02")


def test_asset_applicability_helper_rejects_unknown_reference():
    with pytest.raises(KeyError):
        m2_reference_asset_on_applicable("CW99")


def test_m2_has_no_asset_files_or_required_asset_slots_before_m12():
    for unit in M2_PROVING_REFERENCES:
        assert unit.assets == ()
        assert unit.identity_survival == "structural-reference-without-assets"
        assert all(m.requires_asset_slot is None for m in unit.mechanisms)


def test_country_web_and_cultural_namespaces_do_not_collapse():
    assert M2_REFERENCE_BY_ID["CW01"].lineage == "country-web-scoped-digital-lineage"
    assert M2_REFERENCE_BY_ID["CS07"].lineage == "cultural-tier-s-swiss-international-typographic"
    assert M2_REFERENCE_BY_ID["CW01"].family != M2_REFERENCE_BY_ID["CS07"].family
    assert M2_REFERENCE_BY_ID["CW01"].provenance_pointer != M2_REFERENCE_BY_ID["CS07"].provenance_pointer


def test_ckt_preserves_project_abstraction_and_recovered_lineage_typing():
    ckt = M2_REFERENCE_BY_ID["CS17"]
    assert ckt.lineage == "project-abstraction-with-recovered-vanuatu-sand-drawing-lineage"
    assert "WAVE_H" in ckt.provenance_pointer


def test_no_m2_reference_owns_provenance_disclosure_zone():
    for unit in M2_PROVING_REFERENCES:
        assert all(SemanticZone.U9 not in mechanism.zones for mechanism in unit.mechanisms)


def test_no_host_framework_or_application_import_in_m2_reference_catalog():
    source = inspect.getsource(m2_module).lower()
    assert "import reflex" not in source
    assert "import streamlit" not in source
    assert "from core" not in source
    assert "from database" not in source
    assert "provider" not in source


def test_no_reference_specific_host_branching_pattern_in_catalog():
    source = inspect.getsource(m2_module).lower()
    assert "if reference ==" not in source
    assert "if reference_id ==" not in source


@pytest.mark.parametrize("reference_id", M2_PROVING_REFERENCE_IDS)
def test_provenance_pointer_is_locked_repo_document_not_external_runtime_fetch(reference_id):
    pointer = M2_REFERENCE_BY_ID[reference_id].provenance_pointer
    assert pointer.startswith("docs/design-dna/")
    assert "http://" not in pointer
    assert "https://" not in pointer


@pytest.mark.parametrize("reference_id", M2_PROVING_REFERENCE_IDS)
def test_every_reference_has_explicit_mobile_and_wide_adaptation(reference_id):
    unit = M2_REFERENCE_BY_ID[reference_id]
    adaptations = [m for m in unit.mechanisms if m.axis is Axis.ADAPTATION]
    assert len(adaptations) == 2
    assert {m.viewports for m in adaptations} == {("desktop", "tablet"), ("mobile",)}
    mobile = next(m for m in adaptations if m.viewports == ("mobile",))
    wide = next(m for m in adaptations if m.viewports == ("desktop", "tablet"))
    assert "mobile" in mobile.directive
    assert mobile.directive != wide.directive


@pytest.mark.parametrize("reference_id", M2_PROVING_REFERENCE_IDS)
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_every_reference_resolves_asset_off_on_every_viewport(reference_id, viewport):
    projection = _project(reference_id, viewport=viewport)
    assert projection.is_valid
    assert any(item.source_unit_id == reference_id for item in projection.mechanisms)
    assert projection.viewport is viewport
    assert projection.asset_decisions == ()


@pytest.mark.parametrize("reference_id", M2_PROVING_REFERENCE_IDS)
@pytest.mark.parametrize("asset_state", ASSET_STATES)
def test_every_asset_state_preserves_structural_identity_without_m12_assets(reference_id, asset_state):
    projection = _project(reference_id, asset_state=asset_state)
    assert projection.is_valid
    assert projection.mechanisms
    assert projection.asset_decisions == ()
    assert any(item.source_unit_id == reference_id for item in projection.mechanisms)


@pytest.mark.parametrize("reference_id", M2_PROVING_REFERENCE_IDS)
def test_partial_asset_failure_is_structurally_equivalent_to_asset_off(reference_id):
    off = _project(reference_id, asset_state=AssetState.OFF)
    partial = _project(reference_id, asset_state=AssetState.PARTIAL)
    assert off.is_valid and partial.is_valid
    assert _structural_signature(off) == _structural_signature(partial)
    assert off.asset_decisions == partial.asset_decisions == ()


@pytest.mark.parametrize("reference_id", M2_PROVING_REFERENCE_IDS)
def test_reference_projection_is_deterministic(reference_id):
    first = _project(reference_id)
    second = _project(reference_id)
    assert first.is_valid and second.is_valid
    assert first.fingerprint == second.fingerprint
    assert first.mechanisms == second.mechanisms
    assert first.provenance == second.provenance


@pytest.mark.parametrize("left_id,right_id", REFERENCE_PAIRS)
def test_every_pair_is_structurally_differentiated_asset_off(left_id, right_id):
    left = _project(left_id)
    right = _project(right_id)
    assert left.is_valid and right.is_valid
    left_signature = tuple((m.axis, m.zone, m.directive, m.degradation) for m in left.mechanisms)
    right_signature = tuple((m.axis, m.zone, m.directive, m.degradation) for m in right.mechanisms)
    assert left_signature != right_signature


@pytest.mark.parametrize("reference_id", M2_PROVING_REFERENCE_IDS)
def test_mobile_is_recomposition_not_desktop_shrink(reference_id):
    desktop = _project(reference_id, viewport=Viewport.DESKTOP)
    mobile = _project(reference_id, viewport=Viewport.MOBILE)
    assert desktop.is_valid and mobile.is_valid
    desktop_adaptation = {m.directive for m in desktop.mechanisms if m.axis is Axis.ADAPTATION}
    mobile_adaptation = {m.directive for m in mobile.mechanisms if m.axis is Axis.ADAPTATION}
    assert desktop_adaptation
    assert mobile_adaptation
    assert desktop_adaptation.isdisjoint(mobile_adaptation)
    assert any("mobile" in directive for directive in mobile_adaptation)


@pytest.mark.parametrize("reference_id", M2_PROVING_REFERENCE_IDS)
def test_reading_sanctuary_never_rejects_proving_reference(reference_id):
    projection = _project(reference_id, context=SemanticContext())
    assert projection.is_valid
    assert not any(issue.code is FailureCode.FALLBACK_IDENTITY_COLLAPSE for issue in projection.rejections)


def test_reading_sanctuary_demotes_horta_futurist_and_ckt_intensity():
    for reference_id in ("CS08", "CS10", "CS17"):
        projection = _project(reference_id)
        demoted = [
            m for m in projection.mechanisms
            if m.source_unit_id == reference_id
            and m.zone is SemanticZone.U7
            and m.degradation is DegradationState.READING_SANCTUARY_DEMOTED
        ]
        assert demoted


def test_futurist_accessibility_and_reduced_motion_have_static_fallbacks():
    projection = _project(
        "CS10",
        context=SemanticContext(reduced_motion=True, accessibility_required=True),
    )
    assert projection.is_valid
    kinetic = next(m for m in projection.mechanisms if m.mechanism_id == "cs10-kinetic-cue")
    assert kinetic.degradation is DegradationState.ACCESSIBILITY_DEMOTED
    assert kinetic.directive == "static-directional-force-cue"
    directional = next(m for m in projection.mechanisms if m.mechanism_id == "cs10-directional-form")
    assert directional.degradation is DegradationState.ACCESSIBILITY_DEMOTED


def test_japan_is_controlled_density_not_shrink_everything():
    unit = M2_REFERENCE_BY_ID["CW03"]
    text = " ".join(m.directive for m in unit.mechanisms).lower()
    assert "high-simultaneous-information" in text
    assert "explicit-local-grouping" in text
    assert "not-desktop-shrink" in text
    assert "never-shrinking-everything" in text
    assert "small-font-or-clutter-substitution" in text


def test_china_is_bounded_ecosystem_not_undifferentiated_launcher():
    unit = M2_REFERENCE_BY_ID["CW04"]
    text = " ".join(m.directive for m in unit.mechanisms).lower()
    assert "bounded-multi-service" in text
    assert "service-context-continuity" in text
    assert "never-giant-undifferentiated-launcher" in text
    assert "without-inventing-services-or-permissions" in text


def test_aotearoa_language_integration_does_not_invent_translation():
    unit = M2_REFERENCE_BY_ID["CW05"]
    text = " ".join(m.directive for m in unit.mechanisms).lower()
    assert "bilingual-semantic-pairing" in text
    assert "never-inventing-translation" in text
    assert "correct-language-metadata" in text
    assert "no-fabricated-equivalence" in text
    assert "language-state-continuity" in text


def test_usa_product_system_does_not_invent_workflow_steps():
    unit = M2_REFERENCE_BY_ID["CW02"]
    text = " ".join(m.directive for m in unit.mechanisms).lower()
    assert "task-first-component-hierarchy" in text
    assert "action-state-grammar" in text
    assert "without-inventing-workflow-steps" in text


def test_swiss_country_web_and_cultural_swiss_have_distinct_atomic_mechanisms():
    cw = _project("CW01")
    cultural = _project("CS07")
    assert cw.is_valid and cultural.is_valid
    cw_text = " ".join(m.directive for m in cw.mechanisms)
    cs_text = " ".join(m.directive for m in cultural.mechanisms)
    assert "cross-view-alignment-consistency" in cw_text
    assert "bounded-asymmetric-tension" in cs_text
    assert "not-country-web-system-identity" in cs_text
    assert cw_text != cs_text


def test_horta_is_structural_continuity_not_texture_or_floral_wallpaper():
    unit = M2_REFERENCE_BY_ID["CS08"]
    text = " ".join(m.directive for m in unit.mechanisms).lower()
    assert "structural-contour" in text
    assert "structural-continuity" in text
    assert "not-texture-pack" in text
    assert "without-applied-floral-wallpaper" in text


def test_futurist_typography_preserves_text_meaning_and_application_state():
    unit = M2_REFERENCE_BY_ID["CS10"]
    text = " ".join(m.directive for m in unit.mechanisms).lower()
    assert "without-changing-text-meaning" in text
    assert "never-mutating-application-state-or-semantic-order" in text


def test_ckt_preserves_existing_knowledge_truth():
    unit = M2_REFERENCE_BY_ID["CS17"]
    text = " ".join(m.directive for m in unit.mechanisms).lower()
    assert "without-inventing-order-relationships-or-meaning" in text
    assert "without-fabricated-hierarchy" in text
    assert "without-changing-semantic-relations" in text


@pytest.mark.parametrize("reference_id,engine_id,axis", TENSION_CASES)
def test_reference_engine_ownership_tension_is_deterministic(reference_id, engine_id, axis):
    constraints = RuntimeConstraints(dominance_cap=1, contradiction_budget=10)
    first = _project(reference_id, engine_ids=(engine_id,), constraints=constraints)
    second = _project(reference_id, engine_ids=(engine_id,), constraints=constraints)
    assert first.is_valid and second.is_valid
    assert first.fingerprint == second.fingerprint
    winners = [m for m in first.mechanisms if m.axis is axis]
    assert any(m.source_unit_id == reference_id for m in winners)
    assert any(
        issue.code is FailureCode.OWNERSHIP_COLLISION and issue.axis is axis
        for issue in first.warnings
    )


def test_engine_tension_does_not_erase_uncontested_engine_axes():
    projection = _project(
        "CS10",
        engine_ids=("M12",),
        constraints=RuntimeConstraints(dominance_cap=1, contradiction_budget=10),
    )
    assert projection.is_valid
    assert any(m.source_unit_id == "CS10" for m in projection.mechanisms)
    assert any(m.source_unit_id == "M12" and m.axis is Axis.MATERIAL_CONSTRUCTION for m in projection.mechanisms)


def test_mobile_country_web_fingerprints_remain_pairwise_distinct():
    projections = {
        reference_id: _project(reference_id, viewport=Viewport.MOBILE)
        for reference_id in COUNTRY_WEB_REFERENCE_IDS
    }
    assert all(projection.is_valid for projection in projections.values())
    assert len({projection.fingerprint for projection in projections.values()}) == len(COUNTRY_WEB_REFERENCE_IDS)


def test_a_b_a_theme_switch_restores_same_projection_without_hidden_randomness():
    a1 = _project("CW03", viewport=Viewport.MOBILE)
    b = _project("CS10", viewport=Viewport.MOBILE)
    a2 = _project("CW03", viewport=Viewport.MOBILE)
    assert a1.is_valid and b.is_valid and a2.is_valid
    assert a1.fingerprint == a2.fingerprint
    assert a1.mechanisms == a2.mechanisms
    assert a1.fingerprint != b.fingerprint


def test_registry_registration_helper_is_exact_and_deterministic():
    registry = DNARegistry()
    register_m2_proving_references(registry)
    assert tuple(unit.id for unit in registry.list_units(UnitKind.REFERENCE)) == tuple(sorted(M2_PROVING_REFERENCE_IDS))
