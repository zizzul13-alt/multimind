from itertools import combinations

import pytest

from design_dna import (
    AssetState,
    CompositionRequest,
    COUNTRY_WEB_REFERENCE_IDS,
    CULTURAL_TIER_S_IDS,
    DNARegistry,
    DegradationState,
    M1_ENGINE_IDS,
    M4_PRIMITIVE_IDS,
    SemanticContext,
    SemanticZone,
    TEMPORAL_PRIMITIVE_IDS,
    UnitKind,
    Viewport,
    register_country_web_references,
    register_cultural_tier_s,
    register_m1_engines,
    register_m4_primitives,
    resolve,
)

IMPLEMENTED_REFERENCE_IDS = COUNTRY_WEB_REFERENCE_IDS + CULTURAL_TIER_S_IDS
PRIMITIVE_PAIRS = tuple(combinations(M4_PRIMITIVE_IDS, 2))
TEMPORAL_LIKE_IDS = ("P08", "P21") + TEMPORAL_PRIMITIVE_IDS
TEMPORAL_PAIRS = tuple(combinations(TEMPORAL_LIKE_IDS, 2))
ASSET_STATES = (AssetState.AVAILABLE, AssetState.LOADING, AssetState.PARTIAL, AssetState.OFF)


def _registry():
    registry = DNARegistry()
    register_m1_engines(registry)
    register_country_web_references(registry)
    register_cultural_tier_s(registry)
    register_m4_primitives(registry)
    return registry


def _project(reference_id="CS07", *, engine_ids=(), primitive_ids=(), asset_state=AssetState.OFF, context=None):
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


def test_combined_runtime_registry_has_exact_current_counts_without_duplicate_ids():
    registry = _registry()
    assert len(registry.list_units(UnitKind.REFERENCE)) == 21
    assert len(registry.list_units(UnitKind.ENGINE)) == 29
    assert len(registry.list_units(UnitKind.PRIMITIVE)) == 68
    all_ids = [item.id for item in registry.list_units()]
    assert len(all_ids) == len(set(all_ids)) == 118


@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_no_primitive_claims_provenance_disclosure_zone_u9(primitive_id):
    registry = _registry()
    primitive = registry.require(primitive_id, UnitKind.PRIMITIVE)
    assert all(SemanticZone.U9 not in mechanism.zones for mechanism in primitive.mechanisms)


@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
@pytest.mark.parametrize("asset_state", ASSET_STATES)
def test_every_primitive_survives_every_asset_state_without_asset_decision(primitive_id, asset_state):
    projection = _project(primitive_ids=(primitive_id,), asset_state=asset_state)
    assert projection.is_valid
    assert projection.asset_decisions == ()
    assert primitive_id in _trace_sources(projection)


@pytest.mark.parametrize("reference_id", IMPLEMENTED_REFERENCE_IDS)
@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_every_implemented_reference_composes_with_every_primitive(reference_id, primitive_id):
    projection = _project(reference_id, primitive_ids=(primitive_id,))
    assert projection.is_valid
    assert not projection.rejections
    sources = _trace_sources(projection)
    assert reference_id in sources
    assert primitive_id in sources


@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
@pytest.mark.parametrize("engine_id", M1_ENGINE_IDS)
def test_every_primitive_composes_with_every_material_environment_engine(primitive_id, engine_id):
    projection = _project(engine_ids=(engine_id,), primitive_ids=(primitive_id,))
    assert projection.is_valid
    assert not projection.rejections
    sources = _trace_sources(projection)
    assert engine_id in sources
    assert primitive_id in sources


@pytest.mark.parametrize("left_id,right_id", PRIMITIVE_PAIRS)
def test_all_2278_primitive_pairs_are_valid_and_traceable(left_id, right_id):
    projection = _project(primitive_ids=(left_id, right_id))
    assert projection.is_valid
    assert not projection.rejections
    sources = _trace_sources(projection)
    assert left_id in sources
    assert right_id in sources


@pytest.mark.parametrize("left_id,right_id", TEMPORAL_PAIRS)
def test_all_temporal_like_pairs_reduce_safely_under_accessibility_and_reduced_motion(left_id, right_id):
    context = SemanticContext(
        viewport=Viewport.DESKTOP,
        reduced_motion=True,
        accessibility_required=True,
    )
    projection = _project(primitive_ids=(left_id, right_id), context=context)
    assert projection.is_valid
    assert not projection.rejections
    sources = _trace_sources(projection)
    assert left_id in sources and right_id in sources

    resolved = [
        item for item in projection.mechanisms
        if item.source_unit_id in {left_id, right_id}
    ]
    assert resolved
    assert all(item.degradation is DegradationState.ACCESSIBILITY_DEMOTED for item in resolved)
    assert all("static-immediate" in item.directive for item in resolved)


def test_all_68_primitives_can_be_requested_together_without_rejection():
    projection = _project(primitive_ids=M4_PRIMITIVE_IDS)
    assert projection.is_valid
    assert not projection.rejections
    traced = _trace_sources(projection)
    assert set(M4_PRIMITIVE_IDS).issubset(traced)


def test_all_68_request_is_order_independent_and_deterministic():
    forward = _project(primitive_ids=M4_PRIMITIVE_IDS)
    reverse = _project(primitive_ids=tuple(reversed(M4_PRIMITIVE_IDS)))
    assert forward.is_valid and reverse.is_valid
    assert forward.fingerprint == reverse.fingerprint
    assert forward.mechanisms == reverse.mechanisms
    assert forward.provenance == reverse.provenance
    assert forward.warnings == reverse.warnings


def test_all_68_mobile_projection_is_valid_and_deterministic():
    context = SemanticContext(viewport=Viewport.MOBILE)
    first = _project(primitive_ids=M4_PRIMITIVE_IDS, context=context)
    second = _project(primitive_ids=M4_PRIMITIVE_IDS, context=context)
    assert first.is_valid and second.is_valid
    assert first.fingerprint == second.fingerprint
    assert first.mechanisms == second.mechanisms
    assert set(M4_PRIMITIVE_IDS).issubset(_trace_sources(first))
