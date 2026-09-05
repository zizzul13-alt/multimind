from itertools import combinations

import pytest

from design_dna import (
    AssetState,
    CompositionRequest,
    COUNTRY_WEB_REFERENCE_IDS,
    CULTURAL_TIER_S_IDS,
    DNARegistry,
    IZZUL_PRIMITIVE_FINGERPRINT_BY_ID,
    IZZUL_REFERENCE_IDS,
    M1_ENGINE_IDS,
    M4_PRIMITIVE_IDS,
    SemanticContext,
    UnitKind,
    Viewport,
    register_country_web_references,
    register_cultural_tier_s,
    register_m1_engines,
    register_m4_primitives,
    register_m5_izzul_references,
    resolve,
)

REFERENCE_PAIRS = tuple(combinations(IZZUL_REFERENCE_IDS, 2))
ASSET_STATES = (AssetState.AVAILABLE, AssetState.LOADING, AssetState.PARTIAL, AssetState.OFF)
VIEWPORTS = (Viewport.DESKTOP, Viewport.TABLET, Viewport.MOBILE)


def _registry():
    registry = DNARegistry()
    register_m1_engines(registry)
    register_country_web_references(registry)
    register_cultural_tier_s(registry)
    register_m4_primitives(registry)
    register_m5_izzul_references(registry)
    return registry


def _project(reference_id, *, engine_ids=(), primitive_ids=(), asset_state=AssetState.OFF, context=None):
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
    )


def _trace_sources(projection):
    return (
        {item.source_unit_id for item in projection.mechanisms}
        | {item.source_unit_id for item in projection.provenance if item.source_unit_id}
    )


def test_combined_m0_to_m5_registry_has_exact_counts_and_no_collisions():
    registry = _registry()
    assert len(registry.list_units(UnitKind.REFERENCE)) == 57  # 5 Country-Web + 16 Cultural + 36 Izzul
    assert len(registry.list_units(UnitKind.ENGINE)) == 29
    assert len(registry.list_units(UnitKind.PRIMITIVE)) == 68
    all_ids = [item.id for item in registry.list_units()]
    assert len(all_ids) == len(set(all_ids)) == 154
    assert set(COUNTRY_WEB_REFERENCE_IDS).isdisjoint(IZZUL_REFERENCE_IDS)
    assert set(CULTURAL_TIER_S_IDS).isdisjoint(IZZUL_REFERENCE_IDS)


@pytest.mark.parametrize("reference_id", IZZUL_REFERENCE_IDS)
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_every_izzul_reference_projects_on_all_viewports(reference_id, viewport):
    projection = _project(reference_id, context=SemanticContext(viewport=viewport))
    assert projection.is_valid
    assert not projection.rejections
    assert reference_id in _trace_sources(projection)


@pytest.mark.parametrize("reference_id", IZZUL_REFERENCE_IDS)
@pytest.mark.parametrize("asset_state", ASSET_STATES)
def test_every_izzul_reference_survives_all_asset_states_without_direct_ip_dependency(reference_id, asset_state):
    projection = _project(reference_id, asset_state=asset_state)
    assert projection.is_valid
    assert not projection.rejections
    assert projection.asset_decisions == ()
    assert reference_id in _trace_sources(projection)


@pytest.mark.parametrize("reference_id", IZZUL_REFERENCE_IDS)
@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_all_36_by_68_reference_primitive_compositions_are_valid_traceable_and_non_mutating(reference_id, primitive_id):
    projection = _project(reference_id, primitive_ids=(primitive_id,))
    assert projection.is_valid
    assert not projection.rejections
    sources = _trace_sources(projection)
    assert reference_id in sources
    assert primitive_id in sources


@pytest.mark.parametrize("reference_id", IZZUL_REFERENCE_IDS)
@pytest.mark.parametrize("engine_id", M1_ENGINE_IDS)
def test_all_36_by_29_reference_engine_compositions_are_valid_and_traceable(reference_id, engine_id):
    projection = _project(reference_id, engine_ids=(engine_id,))
    assert projection.is_valid
    assert not projection.rejections
    sources = _trace_sources(projection)
    assert reference_id in sources
    assert engine_id in sources


@pytest.mark.parametrize("reference_id", IZZUL_REFERENCE_IDS)
def test_each_reference_can_activate_its_declared_primitive_fingerprint(reference_id):
    fingerprint = IZZUL_PRIMITIVE_FINGERPRINT_BY_ID[reference_id]
    projection = _project(reference_id, primitive_ids=fingerprint)
    assert projection.is_valid
    assert not projection.rejections
    sources = _trace_sources(projection)
    assert reference_id in sources
    assert set(fingerprint).issubset(sources)


@pytest.mark.parametrize("reference_id", IZZUL_REFERENCE_IDS)
def test_each_reference_can_coexist_with_all_68_primitives_simultaneously(reference_id):
    projection = _project(reference_id, primitive_ids=M4_PRIMITIVE_IDS)
    assert projection.is_valid
    assert not projection.rejections
    traced = _trace_sources(projection)
    assert reference_id in traced
    assert set(M4_PRIMITIVE_IDS).issubset(traced)


@pytest.mark.parametrize("reference_id", IZZUL_REFERENCE_IDS)
def test_each_reference_can_coexist_with_all_29_engines_simultaneously(reference_id):
    projection = _project(reference_id, engine_ids=M1_ENGINE_IDS)
    assert projection.is_valid
    assert not projection.rejections
    traced = _trace_sources(projection)
    assert reference_id in traced
    assert set(M1_ENGINE_IDS).issubset(traced)


@pytest.mark.parametrize("left_id,right_id", REFERENCE_PAIRS)
def test_all_630_izzul_reference_pairs_remain_differentiated(left_id, right_id):
    left = _project(left_id)
    right = _project(right_id)
    assert left.is_valid and right.is_valid
    assert left.fingerprint != right.fingerprint
    left_identity = tuple(item.directive for item in left.mechanisms if item.source_unit_id == left_id)
    right_identity = tuple(item.directive for item in right.mechanisms if item.source_unit_id == right_id)
    assert left_identity
    assert right_identity
    assert left_identity != right_identity


@pytest.mark.parametrize("left_id,right_id", REFERENCE_PAIRS)
def test_all_630_a_to_b_to_a_switches_are_deterministic_and_state_neutral(left_id, right_id):
    a1 = _project(left_id)
    b = _project(right_id)
    a2 = _project(left_id)
    assert a1.is_valid and b.is_valid and a2.is_valid
    assert a1.fingerprint == a2.fingerprint
    assert a1.mechanisms == a2.mechanisms
    assert a1.provenance == a2.provenance
    assert a1.warnings == a2.warnings


@pytest.mark.parametrize("reference_id", IZZUL_REFERENCE_IDS)
def test_reading_sanctuary_never_rejects_izzul_reference(reference_id):
    context = SemanticContext(viewport=Viewport.DESKTOP, accessibility_required=True)
    projection = _project(reference_id, context=context)
    assert projection.is_valid
    assert not projection.rejections
    assert reference_id in _trace_sources(projection)


@pytest.mark.parametrize("reference_id", IZZUL_REFERENCE_IDS)
def test_mobile_projection_is_repeatably_deterministic(reference_id):
    context = SemanticContext(viewport=Viewport.MOBILE)
    first = _project(reference_id, primitive_ids=IZZUL_PRIMITIVE_FINGERPRINT_BY_ID[reference_id], context=context)
    second = _project(reference_id, primitive_ids=tuple(reversed(IZZUL_PRIMITIVE_FINGERPRINT_BY_ID[reference_id])), context=context)
    assert first.is_valid and second.is_valid
    assert first.fingerprint == second.fingerprint
    assert first.mechanisms == second.mechanisms
    assert first.provenance == second.provenance


def test_all_36_titles_have_unique_default_projection_fingerprints():
    fingerprints = [_project(reference_id).fingerprint for reference_id in IZZUL_REFERENCE_IDS]
    assert len(fingerprints) == len(set(fingerprints)) == 36
