from itertools import combinations

import pytest

from design_dna import (
    AssetState,
    CompositionRequest,
    COUNTRY_WEB_REFERENCE_IDS,
    CULTURAL_TIER_A_IDS,
    CULTURAL_TIER_B_IDS,
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
    register_cultural_tier_b,
    register_cultural_tier_s,
    register_m1_engines,
    register_m4_primitives,
    register_m5_izzul_references,
    register_m6_miko_references,
    register_m7_track_t_i_references,
    resolve,
)
from design_dna.track_m_r import (
    TRACK_M_R_ASSET_ON_APPLICABLE,
    TRACK_M_R_ASSET_ON_NOT_APPLICABLE,
    TRACK_M_R_BY_ID,
    TRACK_M_R_CONSTRUCTION_BY_ID,
    TRACK_M_R_EVIDENCE_MODE_BY_ID,
    TRACK_M_R_IDS,
    TRACK_M_R_NAME_BY_ID,
    TRACK_M_R_RECOVERED_EXAMPLE_IDS,
    TRACK_M_R_ROUTED_NON_MEMBERS,
    TRACK_M_R_SELECTOR_POLICY_BY_ID,
    TRACK_M_R_V6_HARDENED_IDS,
    register_track_m_r,
    track_m_r_asset_on_applicable,
)

PAIRS = tuple(combinations(TRACK_M_R_IDS, 2))
PRIOR_REFERENCE_IDS = (
    *COUNTRY_WEB_REFERENCE_IDS,
    *CULTURAL_TIER_S_IDS,
    *CULTURAL_TIER_A_IDS,
    *IZZUL_REFERENCE_IDS,
    *MIKO_REFERENCE_IDS,
    *TRACK_T_I_REFERENCE_IDS,
    *CULTURAL_TIER_B_IDS,
)
CROSS_REFERENCE = tuple(
    (track_m_r_id, prior_id)
    for track_m_r_id in TRACK_M_R_IDS
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
    register_track_m_r(registry)
    return registry


def _project(reference_id, *, engine_ids=(), primitive_ids=(), asset_state=AssetState.OFF,
             context=None, constraints=None, modifiers=None):
    context = context or SemanticContext(viewport=Viewport.DESKTOP)
    return resolve(
        _registry(),
        CompositionRequest(
            selected_reference_id=reference_id,
            engine_ids=tuple(engine_ids),
            primitive_ids=tuple(primitive_ids),
            asset_state=asset_state,
            modifiers={} if modifiers is None else modifiers,
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


def test_combined_m0_to_m10_registry_exact_counts_and_collision_free():
    registry = _registry()
    assert len(PRIOR_REFERENCE_IDS) == 135
    assert len(TRACK_M_R_IDS) == 25
    assert len(registry.list_units(UnitKind.REFERENCE)) == 160
    assert len(registry.list_units(UnitKind.ENGINE)) == 29
    assert len(registry.list_units(UnitKind.PRIMITIVE)) == 68
    all_ids = [item.id for item in registry.list_units()]
    assert len(all_ids) == len(set(all_ids)) == 257
    assert set(TRACK_M_R_IDS).isdisjoint(PRIOR_REFERENCE_IDS)


def test_track_m_r_exact_denominator_names_and_historical_firewall_are_locked():
    assert TRACK_M_R_IDS == tuple(f"MR-{index:03d}" for index in range(1, 26))
    assert len(TRACK_M_R_NAME_BY_ID) == 25
    assert set(TRACK_M_R_NAME_BY_ID) == set(TRACK_M_R_IDS)
    assert "Aklan Piña" in TRACK_M_R_NAME_BY_ID.values()
    assert TRACK_M_R_ROUTED_NON_MEMBERS == {
        "Kanga": "ROUTE_CULTURAL",
        "Māori Wharenui": "ROUTE_CULTURAL_ARCHITECTURE",
        "Dumbara": "HISTORICAL_ROUTE_NOT_TRACK_M_R_MEMBER",
        "Liyelaa": "HISTORICAL_ROUTE_NOT_TRACK_M_R_MEMBER",
        "generic Barkcloth": "ROUTE_M9_ENGINE_PROCESS",
        "Bidri ware": "COMPARATOR_MERGE_ROUTE_NOT_TRACK_M_R_MEMBER",
    }


def test_epistemic_partition_is_exact_and_no_row_is_unclassified():
    assert TRACK_M_R_RECOVERED_EXAMPLE_IDS == {
        "MR-002", "MR-003", "MR-009", "MR-013",
        "MR-017", "MR-019", "MR-023", "MR-025",
    }
    assert TRACK_M_R_V6_HARDENED_IDS == {
        "MR-004", "MR-005", "MR-006", "MR-012", "MR-014", "MR-018", "MR-021",
    }
    modes = tuple(TRACK_M_R_EVIDENCE_MODE_BY_ID.values())
    assert modes.count("RECOVERED_MECHANISM_EXAMPLE") == 8
    assert modes.count("V6_SELECTOR_HARDENED") == 7
    assert modes.count("BOUNDED_EQ3_TRANSLATION") == 10


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_all_25_project_on_every_viewport(reference_id, viewport):
    projection = _project(reference_id, context=SemanticContext(viewport=viewport))
    assert projection.is_valid and not projection.rejections
    assert reference_id in _sources(projection)
    assert _identity(projection, reference_id)


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
@pytest.mark.parametrize("asset_state", ASSET_STATES)
def test_all_25_survive_every_asset_state_without_mandatory_assets(reference_id, asset_state):
    projection = _project(reference_id, asset_state=asset_state)
    assert projection.is_valid and not projection.rejections
    assert projection.asset_decisions == ()
    assert reference_id in _sources(projection)


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_all_25_by_68_reference_primitive_compositions(reference_id, primitive_id):
    projection = _project(reference_id, primitive_ids=(primitive_id,))
    assert projection.is_valid and not projection.rejections
    assert {reference_id, primitive_id}.issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
@pytest.mark.parametrize("engine_id", M1_ENGINE_IDS)
def test_all_25_by_29_reference_engine_compositions(reference_id, engine_id):
    projection = _project(reference_id, engine_ids=(engine_id,))
    assert projection.is_valid and not projection.rejections
    assert {reference_id, engine_id}.issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
def test_each_track_m_r_reference_coexists_with_all_68_primitives(reference_id):
    projection = _project(reference_id, primitive_ids=M4_PRIMITIVE_IDS)
    assert projection.is_valid and not projection.rejections
    assert set(M4_PRIMITIVE_IDS).issubset(_sources(projection))


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
def test_each_track_m_r_reference_coexists_with_all_29_engines(reference_id):
    projection = _project(reference_id, engine_ids=M1_ENGINE_IDS)
    assert projection.is_valid and not projection.rejections
    assert set(M1_ENGINE_IDS).issubset(_sources(projection))


@pytest.mark.parametrize("left_id,right_id", PAIRS)
def test_all_300_track_m_r_pairs_remain_distinct(left_id, right_id):
    left = _project(left_id)
    right = _project(right_id)
    assert left.is_valid and right.is_valid
    assert left.fingerprint != right.fingerprint
    assert _identity(left, left_id) != _identity(right, right_id)


@pytest.mark.parametrize("left_id,right_id", PAIRS)
def test_all_300_a_to_b_to_a_switches_are_deterministic(left_id, right_id):
    a1 = _project(left_id)
    b = _project(right_id)
    a2 = _project(left_id)
    assert a1.is_valid and b.is_valid and a2.is_valid
    assert a1.fingerprint == a2.fingerprint
    assert a1.mechanisms == a2.mechanisms
    assert a1.provenance == a2.provenance


@pytest.mark.parametrize("track_m_r_id,prior_id", CROSS_REFERENCE)
def test_all_25_by_135_prior_reference_cross_owner_pairs_remain_distinct(track_m_r_id, prior_id):
    current = _project(track_m_r_id)
    prior = _project(prior_id)
    assert current.is_valid and prior.is_valid
    identity = _identity(current, track_m_r_id)
    assert identity and "track-m-r-reconstructed-named-material-reference" in identity[0]
    assert identity != _identity(prior, prior_id)


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
def test_reading_sanctuary_and_accessibility_keep_structural_identity(reference_id):
    projection = _project(
        reference_id,
        context=SemanticContext(viewport=Viewport.DESKTOP, accessibility_required=True),
        constraints=RuntimeConstraints(reading_sanctuary=True),
    )
    assert projection.is_valid and not projection.rejections
    assert _identity(projection, reference_id)


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
def test_reduced_motion_is_identity_neutral(reference_id):
    normal = _project(reference_id, context=SemanticContext(viewport=Viewport.MOBILE, reduced_motion=False))
    reduced = _project(reference_id, context=SemanticContext(viewport=Viewport.MOBILE, reduced_motion=True))
    assert normal.is_valid and reduced.is_valid
    assert _identity(normal, reference_id) == _identity(reduced, reference_id)


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
def test_runtime_identity_trace_exposes_epistemic_and_selector_policy(reference_id):
    identity = _identity(_project(reference_id), reference_id)
    assert len(identity) == 1
    assert f"evidence={TRACK_M_R_EVIDENCE_MODE_BY_ID[reference_id]}" in identity[0]
    assert f"selector_policy={TRACK_M_R_SELECTOR_POLICY_BY_ID[reference_id]}" in identity[0]
    assert "named-reference-identity-is-not-engine-family" in identity[0]
    assert "reconstructed-track-m-r-is-not-lost-historical-track-m" in identity[0]


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
def test_all_25_asset_applicability_rows_are_locked_but_assets_remain_optional(reference_id):
    assert reference_id in TRACK_M_R_ASSET_ON_APPLICABLE
    assert track_m_r_asset_on_applicable(reference_id) is True
    assert TRACK_M_R_BY_ID[reference_id].assets == ()
    assert TRACK_M_R_ASSET_ON_NOT_APPLICABLE == frozenset()


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
def test_construction_contracts_are_reference_specific_and_not_generic_wallpaper(reference_id):
    directive = TRACK_M_R_CONSTRUCTION_BY_ID[reference_id]
    assert len(directive) > 80
    assert "wallpaper" in directive or any(token in directive for token in (
        "interlacement", "resist", "backing", "inlay", "stencil", "relief", "beaten", "lattice",
        "weave", "felt", "ceramic", "strips", "layered", "process", "pile", "paper", "stone",
        "lacquer", "firing", "glass",
    ))


def test_masi_and_siapo_asset_off_collision_is_causal_not_label_based():
    masi = _identity(_project("MR-005"), "MR-005")[0]
    siapo = _identity(_project("MR-006"), "MR-006")[0]
    assert "MASK_ABOVE_SHEET" in masi
    assert "RELIEF_BELOW_SHEET" in siapo
    assert "underlying-relief-rubbing-does-not-qualify" in masi
    assert "mask-above-stencil-causality-does-not-qualify" in siapo
    assert masi != siapo


def test_damascene_true_mechanical_inlay_rejects_paint_or_overlay_identity():
    identity = _identity(_project("MR-004"), "MR-004")[0]
    assert "TRUE_MECHANICAL_INLAY_ONLY" in identity
    assert "prepared-recess" in identity
    assert "mechanically-seated-or-hammered" in identity
    assert "painted-or-surface-overlay-lines-do-not-qualify" in identity


def test_kente_shared_invariant_does_not_invent_branch_specific_weaving_claims():
    identity = _identity(_project("MR-012"), "MR-012")[0]
    assert "narrow-woven-strips-assembled-by-sewing-into-a-larger-macro-cloth" in identity
    assert "branch-specific-heddle-supplementary-weft-count-width-or-motif-claims-are-not-inferred" in identity


def test_kuba_is_one_branch_at_a_time_and_never_synthesizes_variant_families():
    identity = _identity(_project("MR-014"), "MR-014")[0]
    assert "ONE_SUPPORTED_KUBA_BRANCH_AT_A_TIME" in identity
    assert "forbids-blending" in identity
    assert "one-fictional-mechanism" in identity


def test_turkmen_subgroup_or_gul_cannot_infer_knot_type():
    identity = _identity(_project("MR-018"), "MR-018")[0]
    assert "OBJECT_TECHNICAL_SELECTOR_REQUIRED" in identity
    assert "SUBGROUP_OR_GUL_DOES_NOT_FIX_KNOT_TYPE" in identity
    assert "may-be-used-to-infer-symmetric-or-asymmetric-knot-type" in identity


def test_japanese_conservation_is_not_a_universal_japanese_joint_abstraction():
    identity = _identity(_project("MR-021"), "MR-021")[0]
    assert "ONE_SUPPORTED_CONSERVATION_OPERATION_AT_A_TIME" in identity
    assert "NO_UNIVERSAL_JAPANESE_JOINT" in identity
    assert "without-synthesizing-the-unesco-skill-set-into-a-universal-japanese-joint" in identity


def test_urushi_and_mezza_filigrana_have_explicit_optical_accessibility_demotions():
    urushi = _project("MR-023", context=SemanticContext(accessibility_required=True))
    glass = _project("MR-025", context=SemanticContext(accessibility_required=True))
    urushi_directives = " ".join(item.directive for item in urushi.mechanisms if item.source_unit_id == "MR-023")
    glass_directives = " ".join(item.directive for item in glass.mechanisms if item.source_unit_id == "MR-025")
    assert "low-glare-structural-layer-cues" in urushi_directives
    assert "high-contrast-internal-line-structure" in glass_directives


@pytest.mark.parametrize("reference_id", TRACK_M_R_V6_HARDENED_IDS)
def test_v6_hardened_rows_are_explicitly_fail_closed_for_unknown_or_cross_branch_inference(reference_id):
    policy = TRACK_M_R_SELECTOR_POLICY_BY_ID[reference_id]
    assert any(token in policy for token in (
        "UNKNOWN", "REQUIRE_EVIDENCE", "ONE_SUPPORTED", "REQUIRED",
    ))


@pytest.mark.parametrize("reference_id", TRACK_M_R_IDS)
def test_arbitrary_modifiers_change_request_fingerprint_but_do_not_activate_hidden_reference_branch(reference_id):
    baseline = _project(reference_id)
    modified = _project(reference_id, modifiers={"variant": "invented", "technique": "invented"})
    assert baseline.is_valid and modified.is_valid
    assert baseline.fingerprint != modified.fingerprint
    assert _identity(baseline, reference_id) == _identity(modified, reference_id)
    baseline_own = tuple(
        item for item in baseline.mechanisms if item.source_unit_id == reference_id
    )
    modified_own = tuple(
        item for item in modified.mechanisms if item.source_unit_id == reference_id
    )
    assert baseline_own == modified_own


def test_unknown_track_m_r_id_fails_closed_in_asset_policy_lookup():
    with pytest.raises(KeyError):
        track_m_r_asset_on_applicable("MR-999")
