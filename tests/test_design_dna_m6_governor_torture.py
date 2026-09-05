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
    MIKO_MECHANISM_BY_ID,
    MIKO_PRIMITIVE_FINGERPRINT_BY_ID,
    MIKO_PRIMITIVE_IDS,
    MIKO_REFERENCE_IDS,
    RuntimeConstraints,
    SemanticContext,
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

MIKO_PAIRS = tuple(combinations(MIKO_REFERENCE_IDS, 2))
CROSS_OWNER_PAIRS = tuple((miko_id, izzul_id) for miko_id in MIKO_REFERENCE_IDS for izzul_id in IZZUL_REFERENCE_IDS)
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


def _trace_sources(projection):
    return (
        {item.source_unit_id for item in projection.mechanisms}
        | {item.source_unit_id for item in projection.provenance if item.source_unit_id}
    )


def _identity_directives(projection, reference_id):
    return tuple(
        item.directive
        for item in projection.mechanisms
        if item.source_unit_id == reference_id and item.mechanism_id.endswith("-identity")
    )


def test_combined_m0_to_m6_registry_has_exact_counts_and_no_collisions():
    registry = _registry()
    assert len(registry.list_units(UnitKind.REFERENCE)) == 80  # 5 Country-Web + 16 Cultural + 36 Izzul + 23 Miko
    assert len(registry.list_units(UnitKind.ENGINE)) == 29
    assert len(registry.list_units(UnitKind.PRIMITIVE)) == 68
    all_ids = [item.id for item in registry.list_units()]
    assert len(all_ids) == len(set(all_ids)) == 177
    assert set(COUNTRY_WEB_REFERENCE_IDS).isdisjoint(MIKO_REFERENCE_IDS)
    assert set(CULTURAL_TIER_S_IDS).isdisjoint(MIKO_REFERENCE_IDS)
    assert set(IZZUL_REFERENCE_IDS).isdisjoint(MIKO_REFERENCE_IDS)


@pytest.mark.parametrize("reference_id", MIKO_REFERENCE_IDS)
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_every_miko_reference_projects_on_all_viewports(reference_id, viewport):
    projection = _project(reference_id, context=SemanticContext(viewport=viewport))
    assert projection.is_valid
    assert not projection.rejections
    assert reference_id in _trace_sources(projection)


@pytest.mark.parametrize("reference_id", MIKO_REFERENCE_IDS)
@pytest.mark.parametrize("asset_state", ASSET_STATES)
def test_every_miko_reference_survives_all_asset_states_without_direct_ip_dependency(reference_id, asset_state):
    projection = _project(reference_id, asset_state=asset_state)
    assert projection.is_valid
    assert not projection.rejections
    assert projection.asset_decisions == ()
    assert reference_id in _trace_sources(projection)


@pytest.mark.parametrize("reference_id", MIKO_REFERENCE_IDS)
@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_all_23_by_68_reference_primitive_compositions_are_valid_traceable_and_non_mutating(reference_id, primitive_id):
    projection = _project(reference_id, primitive_ids=(primitive_id,))
    assert projection.is_valid
    assert not projection.rejections
    sources = _trace_sources(projection)
    assert reference_id in sources
    assert primitive_id in sources


@pytest.mark.parametrize("reference_id", MIKO_REFERENCE_IDS)
@pytest.mark.parametrize("engine_id", M1_ENGINE_IDS)
def test_all_23_by_29_reference_engine_compositions_are_valid_and_traceable(reference_id, engine_id):
    projection = _project(reference_id, engine_ids=(engine_id,))
    assert projection.is_valid
    assert not projection.rejections
    sources = _trace_sources(projection)
    assert reference_id in sources
    assert engine_id in sources


@pytest.mark.parametrize("reference_id", MIKO_REFERENCE_IDS)
def test_each_reference_can_activate_its_declared_mk_fingerprint_without_hidden_dependency(reference_id):
    fingerprint = MIKO_PRIMITIVE_FINGERPRINT_BY_ID[reference_id]
    reference_only = _project(reference_id)
    explicit = _project(reference_id, primitive_ids=fingerprint)
    assert reference_only.is_valid and explicit.is_valid
    assert not reference_only.rejections and not explicit.rejections
    reference_only_sources = _trace_sources(reference_only)
    explicit_sources = _trace_sources(explicit)
    assert reference_id in reference_only_sources
    assert set(fingerprint).isdisjoint(reference_only_sources)
    assert set(fingerprint).issubset(explicit_sources)


@pytest.mark.parametrize("reference_id", MIKO_REFERENCE_IDS)
def test_each_miko_reference_can_coexist_with_all_68_primitives_simultaneously(reference_id):
    projection = _project(reference_id, primitive_ids=M4_PRIMITIVE_IDS)
    assert projection.is_valid
    assert not projection.rejections
    traced = _trace_sources(projection)
    assert reference_id in traced
    assert set(M4_PRIMITIVE_IDS).issubset(traced)


@pytest.mark.parametrize("reference_id", MIKO_REFERENCE_IDS)
def test_each_miko_reference_can_coexist_with_all_29_engines_simultaneously(reference_id):
    projection = _project(reference_id, engine_ids=M1_ENGINE_IDS)
    assert projection.is_valid
    assert not projection.rejections
    traced = _trace_sources(projection)
    assert reference_id in traced
    assert set(M1_ENGINE_IDS).issubset(traced)


@pytest.mark.parametrize("left_id,right_id", MIKO_PAIRS)
def test_all_253_miko_reference_pairs_remain_differentiated(left_id, right_id):
    left = _project(left_id)
    right = _project(right_id)
    assert left.is_valid and right.is_valid
    assert left.fingerprint != right.fingerprint
    left_identity = _identity_directives(left, left_id)
    right_identity = _identity_directives(right, right_id)
    assert left_identity and right_identity
    assert left_identity != right_identity
    assert MIKO_MECHANISM_BY_ID[left_id] != MIKO_MECHANISM_BY_ID[right_id]


@pytest.mark.parametrize("left_id,right_id", MIKO_PAIRS)
def test_all_253_miko_a_to_b_to_a_switches_are_deterministic_and_state_neutral(left_id, right_id):
    a1 = _project(left_id)
    b = _project(right_id)
    a2 = _project(left_id)
    assert a1.is_valid and b.is_valid and a2.is_valid
    assert a1.fingerprint == a2.fingerprint
    assert a1.mechanisms == a2.mechanisms
    assert a1.provenance == a2.provenance
    assert a1.warnings == a2.warnings


@pytest.mark.parametrize("miko_id,izzul_id", CROSS_OWNER_PAIRS)
def test_all_23_by_36_miko_vs_izzul_owner_pairs_are_structurally_distinct_not_recolors(miko_id, izzul_id):
    miko_projection = _project(miko_id)
    izzul_projection = _project(izzul_id)
    assert miko_projection.is_valid and izzul_projection.is_valid
    miko_identity = _identity_directives(miko_projection, miko_id)
    izzul_identity = _identity_directives(izzul_projection, izzul_id)
    assert miko_identity and izzul_identity
    assert miko_identity != izzul_identity
    assert "miko-owner-scoped-reference" in miko_identity[0]
    assert "miko-owner-scoped-reference" not in izzul_identity[0]
    assert set(MIKO_PRIMITIVE_FINGERPRINT_BY_ID[miko_id]).issubset(set(MIKO_PRIMITIVE_IDS))
    assert set(IZZUL_PRIMITIVE_FINGERPRINT_BY_ID[izzul_id]).isdisjoint(set(MIKO_PRIMITIVE_IDS))


@pytest.mark.parametrize("reference_id", MIKO_REFERENCE_IDS)
def test_reading_sanctuary_and_accessibility_never_reject_miko_reference(reference_id):
    context = SemanticContext(
        viewport=Viewport.DESKTOP,
        accessibility_required=True,
        reading_heavy_zones=(
            # Stress normal work/reading surfaces, not provenance ownership U9.
            *SemanticContext().reading_heavy_zones,
        ),
    )
    projection = _project(reference_id, context=context, constraints=RuntimeConstraints(reading_sanctuary=True))
    assert projection.is_valid
    assert not projection.rejections
    assert reference_id in _trace_sources(projection)


@pytest.mark.parametrize("reference_id", MIKO_REFERENCE_IDS)
def test_reduced_motion_never_changes_miko_semantic_identity_or_rejects(reference_id):
    normal = _project(reference_id, context=SemanticContext(viewport=Viewport.MOBILE, reduced_motion=False))
    reduced = _project(reference_id, context=SemanticContext(viewport=Viewport.MOBILE, reduced_motion=True))
    assert normal.is_valid and reduced.is_valid
    assert not normal.rejections and not reduced.rejections
    assert reference_id in _trace_sources(normal)
    assert reference_id in _trace_sources(reduced)
    assert _identity_directives(normal, reference_id) == _identity_directives(reduced, reference_id)


@pytest.mark.parametrize("reference_id", MIKO_REFERENCE_IDS)
def test_mobile_projection_with_declared_fingerprint_is_repeatably_deterministic(reference_id):
    context = SemanticContext(viewport=Viewport.MOBILE)
    fingerprint = MIKO_PRIMITIVE_FINGERPRINT_BY_ID[reference_id]
    first = _project(reference_id, primitive_ids=fingerprint, context=context)
    second = _project(reference_id, primitive_ids=tuple(reversed(fingerprint)), context=context)
    assert first.is_valid and second.is_valid
    assert first.fingerprint == second.fingerprint
    assert first.mechanisms == second.mechanisms
    assert first.provenance == second.provenance


def test_all_23_titles_have_unique_default_projection_fingerprints():
    fingerprints = [_project(reference_id).fingerprint for reference_id in MIKO_REFERENCE_IDS]
    assert len(fingerprints) == len(set(fingerprints)) == 23


def test_f09_f13_role_substitution_collision_stays_distinct_under_shared_all_68_context():
    f09 = _project("MKREF09", primitive_ids=M4_PRIMITIVE_IDS)
    f13 = _project("MKREF13", primitive_ids=M4_PRIMITIVE_IDS)
    assert f09.is_valid and f13.is_valid
    assert _identity_directives(f09, "MKREF09") != _identity_directives(f13, "MKREF13")
    assert "burden-transfer" in _identity_directives(f09, "MKREF09")[0]
    assert "must-not-transfer-target-role-ownership" in _identity_directives(f13, "MKREF13")[0]


def test_f18_f20_peripheral_agency_collision_stays_distinct_under_low_status_system_context():
    f18 = _project("MKREF18", primitive_ids=("MK02", "MK25"))
    f20 = _project("MKREF20", primitive_ids=("MK02", "MK25"))
    assert f18.is_valid and f20.is_valid
    assert MIKO_MECHANISM_BY_ID["MKREF18"] == "PERIPHERAL_SYSTEM_LEVERAGE"
    assert MIKO_MECHANISM_BY_ID["MKREF20"] == "PERIPHERAL_SURVIVAL_LOOP"
    assert _identity_directives(f18, "MKREF18") != _identity_directives(f20, "MKREF20")


def test_f11_f23_uncertainty_collision_preserves_forecast_vs_advisory_ownership():
    f11 = _project("MKREF11", primitive_ids=("MK23",))
    f23 = _project("MKREF23", primitive_ids=("MK23",))
    assert f11.is_valid and f23.is_valid
    assert "future-message-provenance" in _identity_directives(f11, "MKREF11")[0]
    assert "keeps-final-decision-with-the-recorded-owner" in _identity_directives(f23, "MKREF23")[0]


def test_f14_f17_f22_exit_cluster_preserves_deadline_trust_and_coercion_distinctions():
    projections = {item: _project(item, primitive_ids=("MK16", "MK24")) for item in ("MKREF14", "MKREF17", "MKREF22")}
    assert all(item.is_valid and not item.rejections for item in projections.values())
    directives = {item: _identity_directives(projection, item)[0] for item, projection in projections.items()}
    assert len(set(directives.values())) == 3
    assert "bounded-hazard-and-exit-state" in directives["MKREF14"]
    assert "trust-accretion-requires-existing-history-and-exit-boundary" in directives["MKREF17"]
    assert "exit-strategy-requires-existing-exit-intent-constraint-and-boundary-state" in directives["MKREF22"]
