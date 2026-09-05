from itertools import combinations

import pytest

from design_dna import (
    AssetState,
    CompositionRequest,
    COUNTRY_WEB_REFERENCE_IDS,
    CULTURAL_TIER_A_IDS,
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
    register_cultural_tier_a,
    register_cultural_tier_s,
    register_m1_engines,
    register_m4_primitives,
    register_m5_izzul_references,
    register_m6_miko_references,
    register_m7_track_t_i_references,
    resolve,
)
from design_dna.cultural_tier_b import (
    CULTURAL_TIER_B_ASSET_ON_APPLICABLE,
    CULTURAL_TIER_B_BY_ID,
    CULTURAL_TIER_B_EVIDENCE_MODE_BY_ID,
    CULTURAL_TIER_B_IDS,
    CULTURAL_TIER_B_RECOVERED_EXAMPLE_IDS,
    CULTURAL_TIER_B_ROUTED_NON_ADDITIVE,
    cultural_tier_b_asset_on_applicable,
    register_cultural_tier_b,
)

PAIRS = tuple(combinations(CULTURAL_TIER_B_IDS, 2))
PRIOR_REFERENCE_IDS = (
    *COUNTRY_WEB_REFERENCE_IDS,
    *CULTURAL_TIER_S_IDS,
    *CULTURAL_TIER_A_IDS,
    *IZZUL_REFERENCE_IDS,
    *MIKO_REFERENCE_IDS,
    *TRACK_T_I_REFERENCE_IDS,
)
CROSS_REFERENCE = tuple(
    (tier_b_id, prior_id)
    for tier_b_id in CULTURAL_TIER_B_IDS
    for prior_id in PRIOR_REFERENCE_IDS
)
ASSET_STATES = (AssetState.AVAILABLE, AssetState.LOADING, AssetState.PARTIAL, AssetState.OFF)
VIEWPORTS = (Viewport.DESKTOP, Viewport.TABLET, Viewport.MOBILE)


def _registry():
    registry = DNARegistry()
    register_m1_engines(registry)
    register_country_web_references(registry)
    register_cultural_tier_s(registry)
    register_cultural_tier_a(registry)
    register_m4_primitives(registry)
    register_m5_izzul_references(registry)
    register_m6_miko_references(registry)
    register_m7_track_t_i_references(registry)
    register_cultural_tier_b(registry)
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
    return tuple(sorted({
        item.directive
        for item in projection.mechanisms
        if item.source_unit_id == reference_id and item.mechanism_id.endswith("-identity")
    }))


def test_combined_m0_to_m9_registry_exact_counts_and_collision_free():
    registry = _registry()
    assert len(PRIOR_REFERENCE_IDS) == 125
    assert len(CULTURAL_TIER_B_IDS) == 10
    assert len(registry.list_units(UnitKind.REFERENCE)) == 135
    assert len(registry.list_units(UnitKind.ENGINE)) == 29
    assert len(registry.list_units(UnitKind.PRIMITIVE)) == 68
    all_ids = [item.id for item in registry.list_units()]
    assert len(all_ids) == len(set(all_ids)) == 232
    assert set(CULTURAL_TIER_B_IDS).isdisjoint(PRIOR_REFERENCE_IDS)


def test_tier_b_exact_denominator_and_historical_routing_gap_are_locked():
    assert CULTURAL_TIER_B_IDS == (
        "CB01", "CB02", "CB03", "CB04", "CB06",
        "CB07", "CB08", "CB09", "CB10", "CB11",
    )
    assert "CB05" not in CULTURAL_TIER_B_BY_ID
    assert CULTURAL_TIER_B_ROUTED_NON_ADDITIVE == {
        "CB05": "generic Barkcloth -> Material M9; historical routing retained",
    }


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_B_IDS)
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_all_10_project_on_every_viewport(reference_id, viewport):
    projection = _project(reference_id, context=SemanticContext(viewport=viewport))
    assert projection.is_valid and not projection.rejections
    assert reference_id in _sources(projection)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_B_IDS)
@pytest.mark.parametrize("asset_state", ASSET_STATES)
def test_all_10_survive_every_asset_state_without_mandatory_assets(reference_id, asset_state):
    projection = _project(reference_id, asset_state=asset_state)
    assert projection.is_valid and not projection.rejections
    assert projection.asset_decisions == ()
    assert reference_id in _sources(projection)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_B_IDS)
@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_all_10_by_68_reference_primitive_compositions(reference_id, primitive_id):
    projection = _project(reference_id, primitive_ids=(primitive_id,))
    assert projection.is_valid and not projection.rejections
    assert {reference_id, primitive_id}.issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_B_IDS)
@pytest.mark.parametrize("engine_id", M1_ENGINE_IDS)
def test_all_10_by_29_reference_engine_compositions(reference_id, engine_id):
    projection = _project(reference_id, engine_ids=(engine_id,))
    assert projection.is_valid and not projection.rejections
    assert {reference_id, engine_id}.issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_B_IDS)
def test_each_tier_b_reference_coexists_with_all_68_primitives(reference_id):
    projection = _project(reference_id, primitive_ids=M4_PRIMITIVE_IDS)
    assert projection.is_valid and not projection.rejections
    assert set(M4_PRIMITIVE_IDS).issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_B_IDS)
def test_each_tier_b_reference_coexists_with_all_29_engines(reference_id):
    projection = _project(reference_id, engine_ids=M1_ENGINE_IDS)
    assert projection.is_valid and not projection.rejections
    assert set(M1_ENGINE_IDS).issubset(_sources(projection))


@pytest.mark.parametrize("left_id,right_id", PAIRS)
def test_all_45_tier_b_pairs_remain_distinct(left_id, right_id):
    left = _project(left_id)
    right = _project(right_id)
    assert left.is_valid and right.is_valid
    assert left.fingerprint != right.fingerprint
    assert _identity(left, left_id) != _identity(right, right_id)


@pytest.mark.parametrize("left_id,right_id", PAIRS)
def test_all_45_a_to_b_to_a_switches_are_deterministic(left_id, right_id):
    a1 = _project(left_id)
    b = _project(right_id)
    a2 = _project(left_id)
    assert a1.is_valid and b.is_valid and a2.is_valid
    assert a1.fingerprint == a2.fingerprint
    assert a1.mechanisms == a2.mechanisms
    assert a1.provenance == a2.provenance


@pytest.mark.parametrize("tier_b_id,prior_id", CROSS_REFERENCE)
def test_all_10_by_125_prior_reference_cross_owner_pairs_remain_distinct(tier_b_id, prior_id):
    tier_b = _project(tier_b_id)
    prior = _project(prior_id)
    assert tier_b.is_valid and prior.is_valid
    identity = _identity(tier_b, tier_b_id)
    assert identity and "cultural-tier-b-owner-scoped-reference" in identity[0]
    assert identity != _identity(prior, prior_id)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_B_IDS)
def test_reading_sanctuary_and_accessibility_keep_identity(reference_id):
    projection = _project(
        reference_id,
        context=SemanticContext(viewport=Viewport.DESKTOP, accessibility_required=True),
        constraints=RuntimeConstraints(reading_sanctuary=True),
    )
    assert projection.is_valid and not projection.rejections
    assert _identity(projection, reference_id)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_B_IDS)
def test_reduced_motion_is_identity_neutral(reference_id):
    normal = _project(reference_id, context=SemanticContext(viewport=Viewport.MOBILE, reduced_motion=False))
    reduced = _project(reference_id, context=SemanticContext(viewport=Viewport.MOBILE, reduced_motion=True))
    assert normal.is_valid and reduced.is_valid
    assert _identity(normal, reference_id) == _identity(reduced, reference_id)


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_B_IDS)
def test_epistemic_mode_is_visible_in_runtime_identity_trace(reference_id):
    identity = _identity(_project(reference_id), reference_id)
    assert len(identity) == 1
    assert f"evidence={CULTURAL_TIER_B_EVIDENCE_MODE_BY_ID[reference_id]}" in identity[0]
    assert "historical-research-tier-is-not-quality-rank" in identity[0]
    assert "project-abstraction-is-not-universal-cultural-truth" in identity[0]


@pytest.mark.parametrize("reference_id", CULTURAL_TIER_B_IDS)
def test_all_10_asset_applicability_rows_are_locked_but_assets_remain_optional(reference_id):
    assert reference_id in CULTURAL_TIER_B_ASSET_ON_APPLICABLE
    assert cultural_tier_b_asset_on_applicable(reference_id) is True
    assert CULTURAL_TIER_B_BY_ID[reference_id].assets == ()


def test_recovered_vs_bounded_epistemic_partition_is_exact():
    assert CULTURAL_TIER_B_RECOVERED_EXAMPLE_IDS == {"CB02", "CB03", "CB04", "CB06", "CB09"}
    assert sum(mode == "RECOVERED_MECHANISM_EXAMPLE" for mode in CULTURAL_TIER_B_EVIDENCE_MODE_BY_ID.values()) == 5
    assert sum(mode == "BOUNDED_TRANSLATION" for mode in CULTURAL_TIER_B_EVIDENCE_MODE_BY_ID.values()) == 5


def test_routed_generic_barkcloth_cannot_be_selected_as_cultural_reference():
    registry = _registry()
    assert "CB05" not in {item.id for item in registry.list_units(UnitKind.REFERENCE)}
    assert all("Barkcloth" not in item.lineage for item in registry.list_units(UnitKind.REFERENCE))


def test_masi_does_not_collapse_into_generic_barkcloth_or_generic_tapa():
    identity = _identity(_project("CB06"), "CB06")[0]
    assert "masi-lineage" in identity
    assert "generic-tapa" in identity
    assert "generic-barkcloth" in identity


def test_liyelaa_and_dumbara_recovered_lineages_remain_distinct():
    liyelaa = _identity(_project("CB04"), "CB04")[0]
    dumbara = _identity(_project("CB09"), "CB09")[0]
    assert "liyelaa-jehun" in liyelaa
    assert "dumbara-rata-kalala" in dumbara
    assert liyelaa != dumbara


def test_turkmen_subgroup_scope_is_not_silently_collapsed():
    identity = _identity(_project("CB11"), "CB11")[0]
    assert "without-collapsing-subgroup-scope" in identity
