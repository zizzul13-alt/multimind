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
    TEMPORAL_PRIMITIVE_IDS,
    UnitKind,
    Viewport,
    register_country_web_references,
    register_cultural_tier_s,
    register_m1_engines,
    register_m4_primitives,
    register_m5_izzul_references,
    register_m6_miko_references,
    resolve,
)
from design_dna.track_t import (
    TRACK_T_I_NEAREST_NEGATIVE_BY_ID,
    TRACK_T_I_PRIMITIVE_FINGERPRINT_BY_ID,
    TRACK_T_I_REFERENCE_IDS,
    TRACK_T_I_TOPOLOGY_BY_ID,
    register_m7_track_t_i_references,
)

PAIRS = tuple(combinations(TRACK_T_I_REFERENCE_IDS, 2))
CROSS_OWNER = tuple(
    (temporal_id, other_id)
    for temporal_id in TRACK_T_I_REFERENCE_IDS
    for other_id in (*IZZUL_REFERENCE_IDS, *MIKO_REFERENCE_IDS)
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


def test_combined_m0_to_m7_registry_exact_counts_and_collision_free():
    registry = _registry()
    assert len(registry.list_units(UnitKind.REFERENCE)) == 96
    assert len(registry.list_units(UnitKind.ENGINE)) == 29
    assert len(registry.list_units(UnitKind.PRIMITIVE)) == 68
    all_ids = [item.id for item in registry.list_units()]
    assert len(all_ids) == len(set(all_ids)) == 193
    assert set(TRACK_T_I_REFERENCE_IDS).isdisjoint(COUNTRY_WEB_REFERENCE_IDS)
    assert set(TRACK_T_I_REFERENCE_IDS).isdisjoint(CULTURAL_TIER_S_IDS)
    assert set(TRACK_T_I_REFERENCE_IDS).isdisjoint(IZZUL_REFERENCE_IDS)
    assert set(TRACK_T_I_REFERENCE_IDS).isdisjoint(MIKO_REFERENCE_IDS)


@pytest.mark.parametrize("reference_id", TRACK_T_I_REFERENCE_IDS)
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_all_16_project_on_every_viewport(reference_id, viewport):
    projection = _project(reference_id, context=SemanticContext(viewport=viewport))
    assert projection.is_valid and not projection.rejections
    assert reference_id in _sources(projection)


@pytest.mark.parametrize("reference_id", TRACK_T_I_REFERENCE_IDS)
@pytest.mark.parametrize("asset_state", ASSET_STATES)
def test_all_16_survive_all_asset_states_audio_and_ip_free(reference_id, asset_state):
    projection = _project(reference_id, asset_state=asset_state)
    assert projection.is_valid and not projection.rejections
    assert projection.asset_decisions == ()
    assert reference_id in _sources(projection)


@pytest.mark.parametrize("reference_id", TRACK_T_I_REFERENCE_IDS)
@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_all_16_by_68_reference_primitive_compositions(reference_id, primitive_id):
    projection = _project(reference_id, primitive_ids=(primitive_id,))
    assert projection.is_valid and not projection.rejections
    assert {reference_id, primitive_id}.issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", TRACK_T_I_REFERENCE_IDS)
@pytest.mark.parametrize("engine_id", M1_ENGINE_IDS)
def test_all_16_by_29_reference_engine_compositions(reference_id, engine_id):
    projection = _project(reference_id, engine_ids=(engine_id,))
    assert projection.is_valid and not projection.rejections
    assert {reference_id, engine_id}.issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", TRACK_T_I_REFERENCE_IDS)
def test_declared_temporal_fingerprint_is_explicit_not_hidden_injection(reference_id):
    fingerprint = TRACK_T_I_PRIMITIVE_FINGERPRINT_BY_ID[reference_id]
    base = _project(reference_id)
    explicit = _project(reference_id, primitive_ids=fingerprint)
    assert base.is_valid and explicit.is_valid
    assert set(fingerprint).isdisjoint(_sources(base))
    assert set(fingerprint).issubset(_sources(explicit))


@pytest.mark.parametrize("reference_id", TRACK_T_I_REFERENCE_IDS)
def test_each_ti_reference_coexists_with_all_68_primitives(reference_id):
    projection = _project(reference_id, primitive_ids=M4_PRIMITIVE_IDS)
    assert projection.is_valid and not projection.rejections
    assert set(M4_PRIMITIVE_IDS).issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", TRACK_T_I_REFERENCE_IDS)
def test_each_ti_reference_coexists_with_all_29_engines(reference_id):
    projection = _project(reference_id, engine_ids=M1_ENGINE_IDS)
    assert projection.is_valid and not projection.rejections
    assert set(M1_ENGINE_IDS).issubset(_sources(projection))


@pytest.mark.parametrize("left_id,right_id", PAIRS)
def test_all_120_ti_pairs_remain_distinct(left_id, right_id):
    left = _project(left_id)
    right = _project(right_id)
    assert left.is_valid and right.is_valid
    assert left.fingerprint != right.fingerprint
    assert _identity(left, left_id) != _identity(right, right_id)
    assert TRACK_T_I_TOPOLOGY_BY_ID[left_id] != TRACK_T_I_TOPOLOGY_BY_ID[right_id]


@pytest.mark.parametrize("left_id,right_id", PAIRS)
def test_all_120_a_to_b_to_a_switches_are_deterministic(left_id, right_id):
    a1 = _project(left_id)
    b = _project(right_id)
    a2 = _project(left_id)
    assert a1.is_valid and b.is_valid and a2.is_valid
    assert a1.fingerprint == a2.fingerprint
    assert a1.mechanisms == a2.mechanisms
    assert a1.provenance == a2.provenance


@pytest.mark.parametrize("temporal_id,other_id", CROSS_OWNER)
def test_all_16_by_59_personal_cross_owner_pairs_are_not_recolors(temporal_id, other_id):
    temporal = _project(temporal_id)
    other = _project(other_id)
    assert temporal.is_valid and other.is_valid
    identity = _identity(temporal, temporal_id)
    assert identity and "izzul-track-t-i-owner-scoped-reference" in identity[0]
    assert identity != _identity(other, other_id)


@pytest.mark.parametrize("reference_id", TRACK_T_I_REFERENCE_IDS)
def test_reading_sanctuary_accessibility_demotes_temporal_theatricality_not_identity(reference_id):
    context = SemanticContext(viewport=Viewport.DESKTOP, accessibility_required=True)
    projection = _project(
        reference_id,
        context=context,
        constraints=RuntimeConstraints(reading_sanctuary=True),
    )
    assert projection.is_valid and not projection.rejections
    assert reference_id in _sources(projection)
    assert _identity(projection, reference_id)


@pytest.mark.parametrize("reference_id", TRACK_T_I_REFERENCE_IDS)
def test_reduced_motion_keeps_identity_and_requires_no_animation(reference_id):
    normal = _project(reference_id, context=SemanticContext(viewport=Viewport.MOBILE, reduced_motion=False))
    reduced = _project(reference_id, context=SemanticContext(viewport=Viewport.MOBILE, reduced_motion=True))
    assert normal.is_valid and reduced.is_valid
    assert _identity(normal, reference_id) == _identity(reduced, reference_id)


def test_nearest_neighbor_collision_pairs_are_explicit_and_symmetric_where_locked():
    assert TRACK_T_I_NEAREST_NEGATIVE_BY_ID["TI01"] == "TI04"
    assert TRACK_T_I_NEAREST_NEGATIVE_BY_ID["TI04"] == "TI01"
    assert TRACK_T_I_NEAREST_NEGATIVE_BY_ID["TI02"] == "TI09"
    assert TRACK_T_I_NEAREST_NEGATIVE_BY_ID["TI09"] == "TI02"
    assert TRACK_T_I_NEAREST_NEGATIVE_BY_ID["TI03"] == "TI10"
    assert TRACK_T_I_NEAREST_NEGATIVE_BY_ID["TI10"] == "TI03"
    assert TRACK_T_I_NEAREST_NEGATIVE_BY_ID["TI07"] == "TI08"
    assert TRACK_T_I_NEAREST_NEGATIVE_BY_ID["TI08"] == "TI07"


def test_ti11_ti13_ti16_low_transform_cluster_remains_three_distinct_topologies():
    ids = ("TI11", "TI13", "TI16")
    projections = [_project(item, primitive_ids=TEMPORAL_PRIMITIVE_IDS) for item in ids]
    assert all(item.is_valid and not item.rejections for item in projections)
    assert len({TRACK_T_I_TOPOLOGY_BY_ID[item] for item in ids}) == 3
    assert len({_identity(projection, item)[0] for projection, item in zip(projections, ids)}) == 3
