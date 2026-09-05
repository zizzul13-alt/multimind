from itertools import combinations
import inspect

import pytest

import design_dna.catalog as catalog_module
import design_dna.cultural as cultural_module
from design_dna import (
    AssetState,
    Axis,
    CompositionRequest,
    CULTURAL_TIER_S_ASSET_ON_APPLICABLE,
    CULTURAL_TIER_S_BY_ID,
    CULTURAL_TIER_S_HISTORICAL_NON_ADDITIVE,
    CULTURAL_TIER_S_IDS,
    CULTURAL_TIER_S_M2_REUSED_IDS,
    CULTURAL_TIER_S_REFERENCES,
    DNARegistry,
    DegradationState,
    M1_ENGINE_IDS,
    M2_REFERENCE_BY_ID,
    SemanticContext,
    SemanticZone,
    UnitKind,
    Viewport,
    cultural_tier_s_asset_on_applicable,
    register_cultural_tier_s,
    register_m1_engines,
    resolve,
)

EXPECTED_NAMES = {
    "CS01": "Javanese Axial",
    "CS02": "Balinese Subak",
    "CS03": "Japan Print / Ink",
    "CS04": "Rinpa",
    "CS05": "Suzhou Garden",
    "CS06": "Hangeul Structural",
    "CS07": "Swiss International Typographic",
    "CS08": "Horta Continuous Organic",
    "CS09": "Czech Cubist Space",
    "CS10": "Futurist Typography",
    "CS11": "Mexico '68",
    "CS12": "Neo-Concrete",
    "CS13": "MASP",
    "CS14": "Quipu",
    "CS16": "Marshallese Navigation",
    "CS17": "Continuous Knowledge Traversal",
}
VIEWPORTS = (Viewport.DESKTOP, Viewport.TABLET, Viewport.MOBILE)
ASSET_STATES = (AssetState.AVAILABLE, AssetState.LOADING, AssetState.PARTIAL, AssetState.OFF)
REFERENCE_PAIRS = tuple(combinations(CULTURAL_TIER_S_IDS, 2))
COLLISION_CLUSTER = ("CS14", "CS16", "CS17")


def _registry():
    registry = DNARegistry()
    register_m1_engines(registry)
    register_cultural_tier_s(registry)
    return registry


def _project(reference_id, *, viewport=Viewport.DESKTOP, asset_state=AssetState.OFF, engine_ids=(), context=None):
    context = context or SemanticContext(viewport=viewport)
    return resolve(
        _registry(),
        CompositionRequest(reference_id, engine_ids=tuple(engine_ids), asset_state=asset_state),
        context,
    )


def _signature(projection):
    return tuple(
        (item.axis, item.zone, item.directive, item.degradation)
        for item in projection.mechanisms
        if item.source_unit_id == projection.composition_id.split("|", 1)[0]
    )


def test_m3_membership_is_exact_additive_tier_s_16():
    assert CULTURAL_TIER_S_IDS == (
        "CS01", "CS02", "CS03", "CS04", "CS05", "CS06", "CS07", "CS08",
        "CS09", "CS10", "CS11", "CS12", "CS13", "CS14", "CS16", "CS17",
    )
    assert len(CULTURAL_TIER_S_REFERENCES) == 16
    assert tuple(item.id for item in CULTURAL_TIER_S_REFERENCES) == CULTURAL_TIER_S_IDS
    assert set(CULTURAL_TIER_S_BY_ID) == set(CULTURAL_TIER_S_IDS)
    assert CULTURAL_TIER_S_HISTORICAL_NON_ADDITIVE == ("CS15",)
    assert "CS15" not in CULTURAL_TIER_S_BY_ID


def test_m3_names_match_locked_migration_membership():
    assert {item_id: CULTURAL_TIER_S_BY_ID[item_id].family for item_id in CULTURAL_TIER_S_IDS} == EXPECTED_NAMES


def test_m2_proving_units_are_reused_verbatim_not_reauthored():
    assert CULTURAL_TIER_S_M2_REUSED_IDS == ("CS07", "CS08", "CS10", "CS17")
    for item_id in CULTURAL_TIER_S_M2_REUSED_IDS:
        assert CULTURAL_TIER_S_BY_ID[item_id] is M2_REFERENCE_BY_ID[item_id]


def test_all_16_are_reference_units_with_total_15_axis_accounting():
    for item in CULTURAL_TIER_S_REFERENCES:
        assert item.kind is UnitKind.REFERENCE
        mechanism_axes = {m.axis for m in item.mechanisms}
        absence_axes = {a.axis for a in item.axis_absences}
        assert mechanism_axes.isdisjoint(absence_axes)
        assert mechanism_axes | absence_axes == set(Axis)


def test_all_tier_s_are_asset_on_applicable_but_assets_are_not_required_or_added():
    assert CULTURAL_TIER_S_ASSET_ON_APPLICABLE == set(CULTURAL_TIER_S_IDS)
    for item in CULTURAL_TIER_S_REFERENCES:
        assert cultural_tier_s_asset_on_applicable(item.id)
        assert item.assets == ()
        assert all(m.requires_asset_slot is None for m in item.mechanisms)
        assert "structural" in item.identity_survival


def test_asset_applicability_rejects_unknown_reference():
    with pytest.raises(KeyError):
        cultural_tier_s_asset_on_applicable("CS99")


def test_tier_s_owns_no_provenance_disclosure_zone():
    for item in CULTURAL_TIER_S_REFERENCES:
        assert all(SemanticZone.U9 not in mechanism.zones for mechanism in item.mechanisms)


def test_catalog_and_tier_s_modules_remain_host_and_core_neutral():
    source = (inspect.getsource(catalog_module) + inspect.getsource(cultural_module)).lower()
    for forbidden in ("import reflex", "import streamlit", "from core", "from database", "requests.", "httpx"):
        assert forbidden not in source


def test_no_per_reference_runtime_branching_is_introduced():
    source = inspect.getsource(cultural_module).lower()
    assert "if reference_id ==" not in source
    assert "if ref_id ==" not in source


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_S_IDS)
def test_provenance_is_repo_bounded_and_explicit(reference_id):
    pointer = CULTURAL_TIER_S_BY_ID[reference_id].provenance_pointer
    assert pointer.startswith("docs/design-dna/")
    assert "http://" not in pointer and "https://" not in pointer


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_S_IDS)
def test_every_reference_has_distinct_mobile_and_wide_adaptation(reference_id):
    adaptations = [m for m in CULTURAL_TIER_S_BY_ID[reference_id].mechanisms if m.axis is Axis.ADAPTATION]
    assert len(adaptations) == 2
    assert {m.viewports for m in adaptations} == {("desktop", "tablet"), ("mobile",)}
    mobile = next(m for m in adaptations if m.viewports == ("mobile",))
    wide = next(m for m in adaptations if m.viewports == ("desktop", "tablet"))
    assert "mobile" in mobile.directive
    assert mobile.directive != wide.directive


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_S_IDS)
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_all_16_resolve_asset_off_on_all_viewports(reference_id, viewport):
    projection = _project(reference_id, viewport=viewport)
    assert projection.is_valid
    assert projection.viewport is viewport
    assert projection.asset_decisions == ()
    assert any(item.source_unit_id == reference_id for item in projection.mechanisms)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_S_IDS)
@pytest.mark.parametrize("asset_state", ASSET_STATES)
def test_all_asset_states_survive_without_m12(reference_id, asset_state):
    projection = _project(reference_id, asset_state=asset_state)
    assert projection.is_valid
    assert projection.asset_decisions == ()
    assert any(item.source_unit_id == reference_id for item in projection.mechanisms)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_S_IDS)
def test_partial_and_off_are_structurally_equivalent_before_m12(reference_id):
    partial = _project(reference_id, asset_state=AssetState.PARTIAL)
    off = _project(reference_id, asset_state=AssetState.OFF)
    assert partial.is_valid and off.is_valid
    assert partial.mechanisms == off.mechanisms
    assert partial.asset_decisions == off.asset_decisions == ()


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_S_IDS)
def test_tier_s_projection_is_deterministic(reference_id):
    first = _project(reference_id)
    second = _project(reference_id)
    assert first.is_valid and second.is_valid
    assert first.fingerprint == second.fingerprint
    assert first.mechanisms == second.mechanisms
    assert first.provenance == second.provenance


@pytest.mark.parametrize("left_id,right_id", REFERENCE_PAIRS)
def test_all_120_tier_s_pairs_are_structurally_differentiated(left_id, right_id):
    left = _project(left_id)
    right = _project(right_id)
    assert left.is_valid and right.is_valid
    assert _signature(left) != _signature(right)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_S_IDS)
@pytest.mark.parametrize("engine_id", M1_ENGINE_IDS)
def test_every_tier_s_reference_composes_with_every_m1_engine(reference_id, engine_id):
    projection = _project(reference_id, engine_ids=(engine_id,))
    assert projection.is_valid
    owners = {item.source_unit_id for item in projection.mechanisms}
    assert reference_id in owners
    assert engine_id in owners


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_S_IDS)
def test_mobile_is_recomposition_not_desktop_shrink(reference_id):
    desktop = _project(reference_id, viewport=Viewport.DESKTOP)
    mobile = _project(reference_id, viewport=Viewport.MOBILE)
    desktop_directives = {m.directive for m in desktop.mechanisms if m.axis is Axis.ADAPTATION and m.source_unit_id == reference_id}
    mobile_directives = {m.directive for m in mobile.mechanisms if m.axis is Axis.ADAPTATION and m.source_unit_id == reference_id}
    assert desktop_directives and mobile_directives
    assert desktop_directives.isdisjoint(mobile_directives)


def test_quipu_marshallese_ckt_collision_cluster_is_distinct():
    projections = {item_id: _project(item_id) for item_id in COLLISION_CLUSTER}
    signatures = {item_id: _signature(projection) for item_id, projection in projections.items()}
    assert len(set(signatures.values())) == 3
    assert "strand-and-node-topology" in " ".join(m.directive for m in projections["CS14"].mechanisms)
    assert "relational-orientation-field" in " ".join(m.directive for m in projections["CS16"].mechanisms)
    assert "knowledge" in " ".join(m.directive for m in projections["CS17"].mechanisms).lower()


def test_knowledge_navigation_cluster_never_invents_truth():
    quipu = " ".join(m.directive for m in CULTURAL_TIER_S_BY_ID["CS14"].mechanisms).lower()
    marshallese = " ".join(m.directive for m in CULTURAL_TIER_S_BY_ID["CS16"].mechanisms).lower()
    ckt = " ".join(m.directive for m in CULTURAL_TIER_S_BY_ID["CS17"].mechanisms).lower()
    assert "never-encodes-invented-cultural-meaning-data-or-hierarchy" in quipu
    assert "without-inventing-route-authority-geography-or-cultural-meaning" in marshallese
    assert "without-inventing" in ckt


def test_script_and_language_truth_is_preserved():
    hangeul = " ".join(m.directive for m in CULTURAL_TIER_S_BY_ID["CS06"].mechanisms).lower()
    assert "without-substituting-or-altering-user-text" in hangeul
    assert "never-fabricates-hangeul-or-transliteration" in hangeul
    assert "reading-order" in hangeul


def test_axial_and_subak_do_not_invent_authority_or_social_hierarchy():
    axial = " ".join(m.directive for m in CULTURAL_TIER_S_BY_ID["CS01"].mechanisms).lower()
    subak = " ".join(m.directive for m in CULTURAL_TIER_S_BY_ID["CS02"].mechanisms).lower()
    assert "without-inventing-authority" in axial
    assert "without-inventing-chronology-ritual-or-semantic-rank" in axial
    assert "without-inventing-social-hierarchy-resource-rights-or-authority" in subak


def test_japan_print_rinpa_suzhou_are_structural_not_motif_or_scenery_skins():
    texts = {item_id: " ".join(m.directive for m in CULTURAL_TIER_S_BY_ID[item_id].mechanisms).lower() for item_id in ("CS03", "CS04", "CS05")}
    assert "without-literal-print-motif-or-illustration-copying" in texts["CS03"]
    assert "without-motif-pack-substitution" in texts["CS04"]
    assert "without-scenery-wallpaper" in texts["CS05"]


def test_czech_cubist_and_masp_are_construction_logic_not_texture_or_prop():
    cubist = " ".join(m.directive for m in CULTURAL_TIER_S_BY_ID["CS09"].mechanisms).lower()
    masp = " ".join(m.directive for m in CULTURAL_TIER_S_BY_ID["CS13"].mechanisms).lower()
    assert "not-applied-cubist-texture" in cubist
    assert "not-museum-prop-or-texture" in masp


def test_mexico68_and_neoconcrete_have_accessible_static_fallbacks_without_added_wait():
    context = SemanticContext(reduced_motion=True, accessibility_required=True)
    mexico = _project("CS11", context=context)
    neo = _project("CS12", context=context)
    assert mexico.is_valid and neo.is_valid
    mexico_unsafe = [m for m in mexico.mechanisms if m.source_unit_id == "CS11" and m.mechanism_id in {"cs11-optical-type", "cs11-pulse"}]
    neo_unsafe = [m for m in neo.mechanisms if m.source_unit_id == "CS12" and m.mechanism_id in {"cs12-bounded-motion"}]
    assert mexico_unsafe and neo_unsafe
    assert all(m.degradation is DegradationState.ACCESSIBILITY_DEMOTED for m in mexico_unsafe + neo_unsafe)
    text = " ".join(m.directive for m in CULTURAL_TIER_S_BY_ID["CS12"].mechanisms).lower()
    assert "not-added-wait-time" in text
    assert "never-add-actions-change-permissions-or-mutate-domain-state" in text


def test_reading_sanctuary_behavior_from_m2_proving_refs_is_preserved_in_m3():
    for reference_id in ("CS08", "CS10", "CS17"):
        projection = _project(reference_id)
        demoted = [
            m for m in projection.mechanisms
            if m.source_unit_id == reference_id
            and m.zone is SemanticZone.U7
            and m.degradation is DegradationState.READING_SANCTUARY_DEMOTED
        ]
        assert demoted


def test_a_b_a_switching_returns_identical_projection_without_state_coupling():
    first_a = _project("CS14")
    _ = _project("CS16")
    second_a = _project("CS14")
    assert first_a.fingerprint == second_a.fingerprint
    assert first_a.mechanisms == second_a.mechanisms
