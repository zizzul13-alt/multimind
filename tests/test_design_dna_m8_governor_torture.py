from itertools import combinations

import pytest

from design_dna import (
    AssetState,
    CompositionRequest,
    COUNTRY_WEB_REFERENCE_IDS,
    CULTURAL_TIER_S_IDS,
    DNARegistry,
    IZZUL_REFERENCE_IDS,
    M1_ENGINE_IDS,
    M4_PRIMITIVE_IDS,
    MIKO_REFERENCE_IDS,
    RuntimeConstraints,
    SemanticContext,
    TRACK_T_I_REFERENCE_IDS,
    UnitKind,
    Viewport,
    register_country_web_references,
    register_cultural_tier_s,
    register_m1_engines,
    register_m4_primitives,
    register_m5_izzul_references,
    register_m6_miko_references,
    register_m7_track_t_i_references,
    resolve,
)
from design_dna.cultural_tier_a import (
    CULTURAL_TIER_A_EVIDENCE_MODE_BY_ID,
    CULTURAL_TIER_A_HISTORICAL_NON_ADDITIVE,
    CULTURAL_TIER_A_IDS,
    register_cultural_tier_a,
)

PAIRS = tuple(combinations(CULTURAL_TIER_A_IDS, 2))
PRIOR_REFERENCE_IDS = (
    *COUNTRY_WEB_REFERENCE_IDS,
    *CULTURAL_TIER_S_IDS,
    *IZZUL_REFERENCE_IDS,
    *MIKO_REFERENCE_IDS,
    *TRACK_T_I_REFERENCE_IDS,
)
CROSS_REFERENCE = tuple(
    (tier_a_id, prior_id)
    for tier_a_id in CULTURAL_TIER_A_IDS
    for prior_id in PRIOR_REFERENCE_IDS
)
ASSET_STATES = (AssetState.AVAILABLE, AssetState.LOADING, AssetState.PARTIAL, AssetState.OFF)
VIEWPORTS = (Viewport.DESKTOP, Viewport.TABLET, Viewport.MOBILE)


def _registry():
    registry = DNARegistry()
    register_m1_engines(registry)
    register_country_web_references(registry)
    register_cultural_tier_s(registry)
    register_m4_primitives(registry)
    register_m5_izzul_references(registry)
    register_m6_miko_references(registry)
    register_m7_track_t_i_references(registry)
    register_cultural_tier_a(registry)
    return registry


def _project(reference_id, *, engine_ids=(), primitive_ids=(), asset_state=AssetState.OFF, context=None, constraints=None):
    context = context or SemanticContext(viewport=Viewport.DESKTOP)
    return resolve(
        _registry(),
        CompositionRequest(
            selected_reference_id=reference_id,
            engine_ids=tuple(engine_ids),
            primitive_ids=tuple(primitive_ids),
            asset_state=asset_state,
        ),
        context,
        constraints,
    )


def _sources(projection):
    return (
        {item.source_unit_id for item in projection.mechanisms}
        | {item.source_unit_id for item in projection.provenance if item.source_unit_id}
    )


def _identity(projection, reference_id):
    return tuple(
        item.directive
        for item in projection.mechanisms
        if item.source_unit_id == reference_id and item.mechanism_id.endswith("-identity")
    )


def test_combined_m0_to_m8_registry_exact_counts_and_collision_free():
    registry = _registry()
    assert len(PRIOR_REFERENCE_IDS) == 96
    assert len(registry.list_units(UnitKind.REFERENCE)) == 125
    assert len(registry.list_units(UnitKind.ENGINE)) == 29
    assert len(registry.list_units(UnitKind.PRIMITIVE)) == 68
    all_ids = [item.id for item in registry.list_units()]
    assert len(all_ids) == len(set(all_ids)) == 222
    assert set(CULTURAL_TIER_A_IDS).isdisjoint(PRIOR_REFERENCE_IDS)
    assert set(CULTURAL_TIER_A_IDS).isdisjoint(CULTURAL_TIER_A_HISTORICAL_NON_ADDITIVE)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_A_IDS)
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_all_29_project_on_every_viewport(reference_id, viewport):
    projection = _project(reference_id, context=SemanticContext(viewport=viewport))
    assert projection.is_valid and not projection.rejections
    assert reference_id in _sources(projection)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_A_IDS)
@pytest.mark.parametrize("asset_state", ASSET_STATES)
def test_all_29_survive_every_asset_state_without_asset_dependency(reference_id, asset_state):
    projection = _project(reference_id, asset_state=asset_state)
    assert projection.is_valid and not projection.rejections
    assert projection.asset_decisions == ()
    assert reference_id in _sources(projection)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_A_IDS)
@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_all_29_by_68_reference_primitive_compositions(reference_id, primitive_id):
    projection = _project(reference_id, primitive_ids=(primitive_id,))
    assert projection.is_valid and not projection.rejections
    assert {reference_id, primitive_id}.issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_A_IDS)
@pytest.mark.parametrize("engine_id", M1_ENGINE_IDS)
def test_all_29_by_29_reference_engine_compositions(reference_id, engine_id):
    projection = _project(reference_id, engine_ids=(engine_id,))
    assert projection.is_valid and not projection.rejections
    assert {reference_id, engine_id}.issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_A_IDS)
def test_each_tier_a_reference_coexists_with_all_68_primitives(reference_id):
    projection = _project(reference_id, primitive_ids=M4_PRIMITIVE_IDS)
    assert projection.is_valid and not projection.rejections
    assert set(M4_PRIMITIVE_IDS).issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_A_IDS)
def test_each_tier_a_reference_coexists_with_all_29_engines(reference_id):
    projection = _project(reference_id, engine_ids=M1_ENGINE_IDS)
    assert projection.is_valid and not projection.rejections
    assert set(M1_ENGINE_IDS).issubset(_sources(projection))


@pytest.mark.parametrize("left_id,right_id", PAIRS)
def test_all_406_tier_a_pairs_remain_distinct(left_id, right_id):
    left = _project(left_id)
    right = _project(right_id)
    assert left.is_valid and right.is_valid
    assert left.fingerprint != right.fingerprint
    assert _identity(left, left_id) != _identity(right, right_id)


@pytest.mark.parametrize("left_id,right_id", PAIRS)
def test_all_406_a_to_b_to_a_switches_are_deterministic(left_id, right_id):
    a1 = _project(left_id)
    b = _project(right_id)
    a2 = _project(left_id)
    assert a1.is_valid and b.is_valid and a2.is_valid
    assert a1.fingerprint == a2.fingerprint
    assert a1.mechanisms == a2.mechanisms
    assert a1.provenance == a2.provenance


@pytest.mark.parametrize("tier_a_id,prior_id", CROSS_REFERENCE)
def test_all_29_by_96_prior_reference_cross_owner_pairs_remain_distinct(tier_a_id, prior_id):
    tier_a = _project(tier_a_id)
    prior = _project(prior_id)
    assert tier_a.is_valid and prior.is_valid
    identity = _identity(tier_a, tier_a_id)
    assert identity and "cultural-tier-a-owner-scoped-reference" in identity[0]
    assert identity != _identity(prior, prior_id)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_A_IDS)
def test_reading_sanctuary_and_accessibility_keep_identity(reference_id):
    projection = _project(
        reference_id,
        context=SemanticContext(viewport=Viewport.DESKTOP, accessibility_required=True),
        constraints=RuntimeConstraints(reading_sanctuary=True),
    )
    assert projection.is_valid and not projection.rejections
    assert _identity(projection, reference_id)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_A_IDS)
def test_reduced_motion_is_identity_neutral(reference_id):
    normal = _project(reference_id, context=SemanticContext(viewport=Viewport.MOBILE, reduced_motion=False))
    reduced = _project(reference_id, context=SemanticContext(viewport=Viewport.MOBILE, reduced_motion=True))
    assert normal.is_valid and reduced.is_valid
    assert _identity(normal, reference_id) == _identity(reduced, reference_id)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_A_IDS)
def test_epistemic_mode_is_visible_in_runtime_identity_trace(reference_id):
    identity = _identity(_project(reference_id), reference_id)
    assert len(identity) == 1
    assert f"evidence={CULTURAL_TIER_A_EVIDENCE_MODE_BY_ID[reference_id]}" in identity[0]
    assert "project-abstraction-is-not-universal-cultural-truth" in identity[0]


def test_siapo_and_ngatu_bounded_large_field_translation_do_not_collapse():
    siapo = _identity(_project("CA35"), "CA35")
    ngatu = _identity(_project("CA36"), "CA36")
    assert siapo != ngatu
    assert "siapo" in siapo[0]
    assert "ngatu" in ngatu[0]


def test_cultural_material_and_country_firewall_is_runtime_visible():
    for reference_id in CULTURAL_TIER_A_IDS:
        projection = _project(reference_id)
        directives = [
            item.directive
            for item in projection.mechanisms
            if item.source_unit_id == reference_id and item.mechanism_id.endswith("-semantic-firewall")
        ]
        assert len(directives) == 1
        assert "may-not-promote-engine-or-country-lens-into-reference-truth" in directives[0]
