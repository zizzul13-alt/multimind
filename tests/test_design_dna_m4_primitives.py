from itertools import combinations, product
import inspect

import pytest

import design_dna.primitives as primitive_module
from design_dna import (
    AssetState,
    Axis,
    CompositionRequest,
    CULTURAL_TIER_S_BY_ID,
    DNARegistry,
    DegradationState,
    IZZUL_PRIMITIVE_IDS,
    IZZUL_PRIMITIVE_NAMES,
    IZZUL_PRIMITIVES,
    M1_ENGINE_IDS,
    M4_PRIMITIVE_IDS,
    M4_PRIMITIVES,
    MIKO_PRIMITIVE_IDS,
    MIKO_PRIMITIVE_NAMES,
    MIKO_PRIMITIVES,
    PRIMITIVE_BY_ID,
    PRIMITIVE_NAMES,
    RuntimeConstraints,
    SemanticContext,
    SemanticZone,
    TEMPORAL_HISTORICAL_NON_ADDITIVE,
    TEMPORAL_PRIMITIVE_IDS,
    TEMPORAL_PRIMITIVE_NAMES,
    TEMPORAL_PRIMITIVES,
    UnitKind,
    Viewport,
    primitive_asset_on_applicable,
    register_cultural_tier_s,
    register_m1_engines,
    register_m4_primitives,
    resolve,
)

EXPECTED_P_NAMES = {
    "P01": "SCALE_PUNCTUATION", "P02": "NEGATIVE_SPACE_PACING", "P03": "DENSITY_MODULATION",
    "P04": "PROGRESSIVE_REVEAL", "P05": "STATE_OVERLAY", "P06": "TOPOLOGICAL_TRAVERSAL",
    "P07": "LAYERED_WORLD_RULES", "P08": "TEMPORAL_PUNCTUATION", "P09": "STATE_LINKED_DEFORMATION",
    "P10": "DIRECTIONAL_FORCE_FORM", "P11": "ORNAMENT_AS_STRUCTURE", "P12": "MATERIAL_LAYER_REVEAL",
    "P13": "EDITORIAL_SEGMENT_PUNCTUATION", "P14": "RELATIONAL_ANCHOR", "P15": "REPRESENTATIONAL_MISMATCH",
    "P16": "ENVIRONMENTAL_CAUSALITY", "P17": "SYSTEM_WORLD_DUAL_LAYER", "P18": "DETAIL_DENSITY_FOCUS",
    "P19": "CROPPING_AS_COMPOSITION", "P20": "REFRACTIVE_FRAGMENTATION", "P21": "CONFRONTATION_TIME_DILATION",
    "P22": "RULE_CHANGING_STAGE", "P23": "INFRASTRUCTURE_AS_SYSTEM", "P24": "CORRESPONDENCE_AS_OBJECT",
    "P25": "RHYTHMIC_CULTURAL_SPLICE",
}
EXPECTED_MK_NAMES = {
    "MK01": "TRAJECTORY_INTERVENTION", "MK02": "PERIPHERAL_AGENCY", "MK03": "ROLE_REFRAMING",
    "MK04": "POST_CANON_REPAIR", "MK05": "CARE_ACCUMULATION", "MK06": "CAPABILITY_TRANSFER",
    "MK07": "PREVENTIVE_GUIDANCE", "MK08": "CHOSEN_KINSHIP", "MK09": "CONTESTED_BELONGING",
    "MK10": "LATENT_CAPABILITY", "MK11": "CARE_FIRST_HIERARCHY", "MK12": "LOW_PROFILE_SURVIVAL",
    "MK13": "RESOURCE_CONSTRAINED_PLANNING", "MK14": "TIMELINE_DRIFT", "MK15": "ENDING_AUTHORITY",
    "MK16": "EXIT_STRATEGY_SET", "MK17": "RELATIONAL_PERSISTENCE", "MK18": "FUTURE_JUDGMENT_FEEDBACK",
    "MK19": "SOCIAL_PERCEPTION_GAP", "MK20": "VOLUNTARY_ROLE_EXPANSION", "MK21": "SIBLING_GUARDIANSHIP",
    "MK22": "PATRONAGE_INDIRECT_AGENCY", "MK23": "UNCERTAINTY_INTERPRETATION", "MK24": "BOUNDARY_SETTING_IN_CARE",
    "MK25": "SYSTEM_LITERACY_FROM_LOW_STATUS",
}
EXPECTED_TP_NAMES = {
    "TP01": "PERIODICITY", "TP02": "STRUCTURAL_BOUNDARY", "TP03": "INTENSITY_ENVELOPE",
    "TP04": "RESOLUTION", "TP05": "RECURRENCE_WITH_VARIATION", "TP06": "RETURN_RECALL",
    "TP07": "CALL_RESPONSE_HANDOFF", "TP08": "EXPECTATION_DISPLACEMENT", "TP09": "INTERRUPTION",
    "TP10": "NEGATIVE_INTERVAL_RESERVED_GAP", "TP11": "RATE_CHANGE", "TP12": "DENSITY_EVOLUTION",
    "TP13": "LAYER_ENTRY_EXIT", "TP14": "PARALLEL_TEMPORAL_VOICES", "TP15": "ANTICIPATION",
    "TP16": "IRREVERSIBLE_PROGRESSION", "TP17": "TERMINAL_RESOLUTION_AFTERBODY", "TP18": "TEMPORAL_PUNCTUATION",
}
VIEWPORTS = (Viewport.DESKTOP, Viewport.TABLET, Viewport.MOBILE)
REPRESENTATIVE_ENGINES = ("M1", "M5", "M10", "E2", "E11")
P_MK_PAIRS = tuple(product(IZZUL_PRIMITIVE_IDS, MIKO_PRIMITIVE_IDS))
TP_PAIRS = tuple(combinations(TEMPORAL_PRIMITIVE_IDS, 2))
TEMPORAL_LIKE_IDS = ("P08", "P21") + TEMPORAL_PRIMITIVE_IDS


def _registry():
    registry = DNARegistry()
    register_m1_engines(registry)
    register_cultural_tier_s(registry)
    register_m4_primitives(registry)
    return registry


def _project(primitive_ids, *, viewport=Viewport.DESKTOP, engine_ids=(), context=None):
    context = context or SemanticContext(viewport=viewport)
    return resolve(
        _registry(),
        CompositionRequest(
            selected_reference_id="CS07",
            engine_ids=tuple(engine_ids),
            primitive_ids=tuple(primitive_ids),
            asset_state=AssetState.OFF,
        ),
        context,
    )


def test_exact_68_member_census_and_family_counts():
    assert len(IZZUL_PRIMITIVE_IDS) == 25
    assert len(MIKO_PRIMITIVE_IDS) == 25
    assert len(TEMPORAL_PRIMITIVE_IDS) == 18
    assert len(M4_PRIMITIVE_IDS) == 68
    assert len(M4_PRIMITIVES) == 68
    assert tuple(item.id for item in M4_PRIMITIVES) == M4_PRIMITIVE_IDS
    assert set(PRIMITIVE_BY_ID) == set(M4_PRIMITIVE_IDS)
    assert TEMPORAL_HISTORICAL_NON_ADDITIVE == ("TP19", "TP20")
    assert "TP19" not in PRIMITIVE_BY_ID and "TP20" not in PRIMITIVE_BY_ID


def test_exact_locked_names_are_preserved():
    assert IZZUL_PRIMITIVE_NAMES == EXPECTED_P_NAMES
    assert MIKO_PRIMITIVE_NAMES == EXPECTED_MK_NAMES
    assert TEMPORAL_PRIMITIVE_NAMES == EXPECTED_TP_NAMES
    assert PRIMITIVE_NAMES == {**EXPECTED_P_NAMES, **EXPECTED_MK_NAMES, **EXPECTED_TP_NAMES}


def test_p08_and_p21_remain_distinct_from_temporal_tp_family():
    assert "P08" in IZZUL_PRIMITIVE_IDS and "P21" in IZZUL_PRIMITIVE_IDS
    assert "P08" not in TEMPORAL_PRIMITIVE_IDS and "P21" not in TEMPORAL_PRIMITIVE_IDS
    assert PRIMITIVE_BY_ID["P08"].family == "IZZUL_PRIMITIVE"
    assert PRIMITIVE_BY_ID["P21"].family == "IZZUL_PRIMITIVE"
    assert all(PRIMITIVE_BY_ID[item_id].family == "TEMPORAL_PRIMITIVE" for item_id in TEMPORAL_PRIMITIVE_IDS)


@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_all_units_are_atomic_primitives_with_total_axis_accounting(primitive_id):
    item = PRIMITIVE_BY_ID[primitive_id]
    assert item.kind is UnitKind.PRIMITIVE
    mechanism_axes = {m.axis for m in item.mechanisms}
    absence_axes = {a.axis for a in item.axis_absences}
    assert mechanism_axes.isdisjoint(absence_axes)
    assert mechanism_axes | absence_axes == set(Axis)
    assert len(item.mechanisms) == 1


@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_all_primitives_are_asset_not_applicable_and_have_no_asset_dependency(primitive_id):
    item = PRIMITIVE_BY_ID[primitive_id]
    assert primitive_asset_on_applicable(primitive_id) is False
    assert item.assets == ()
    assert all(m.requires_asset_slot is None for m in item.mechanisms)
    assert "atomic-structural" in item.identity_survival


def test_unknown_asset_applicability_fails_closed():
    with pytest.raises(KeyError):
        primitive_asset_on_applicable("P99")


@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_all_provenance_is_repository_bounded(primitive_id):
    pointer = PRIMITIVE_BY_ID[primitive_id].provenance_pointer
    assert pointer.startswith("docs/design-dna/")
    assert "http://" not in pointer and "https://" not in pointer


def test_runtime_module_is_host_core_network_neutral_and_has_no_per_id_runtime_branching():
    source = inspect.getsource(primitive_module).lower()
    for forbidden in ("import reflex", "import streamlit", "from core", "from database", "requests.", "httpx"):
        assert forbidden not in source
    assert "if primitive_id ==" not in source


@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_each_primitive_resolves_across_all_viewports(primitive_id, viewport):
    projection = _project((primitive_id,), viewport=viewport)
    assert projection.is_valid
    assert projection.viewport is viewport
    assert any(m.source_unit_id == primitive_id for m in projection.mechanisms)


@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
def test_each_primitive_is_deterministic(primitive_id):
    first = _project((primitive_id,))
    second = _project((primitive_id,))
    assert first.is_valid and second.is_valid
    assert first.fingerprint == second.fingerprint
    assert first.mechanisms == second.mechanisms
    assert first.provenance == second.provenance


@pytest.mark.parametrize("p_id,mk_id", P_MK_PAIRS)
def test_all_625_izzul_miko_primitive_pairs_resolve_without_contradiction_rejection(p_id, mk_id):
    projection = _project((p_id, mk_id))
    assert projection.is_valid
    assert not projection.rejections


@pytest.mark.parametrize("left_id,right_id", TP_PAIRS)
def test_all_153_temporal_pairs_resolve_without_added_wait_contract_failure(left_id, right_id):
    projection = _project((left_id, right_id))
    assert projection.is_valid
    assert not projection.rejections


@pytest.mark.parametrize("primitive_id", M4_PRIMITIVE_IDS)
@pytest.mark.parametrize("engine_id", REPRESENTATIVE_ENGINES)
def test_all_68_primitives_compose_with_representative_material_environment_engines(primitive_id, engine_id):
    assert engine_id in M1_ENGINE_IDS
    projection = _project((primitive_id,), engine_ids=(engine_id,))
    assert projection.is_valid
    assert any(m.source_unit_id == primitive_id for m in projection.mechanisms)
    assert any(m.source_unit_id == engine_id for m in projection.mechanisms)


@pytest.mark.parametrize("primitive_id", TEMPORAL_LIKE_IDS)
def test_temporal_primitives_obey_no_added_wait_law_and_reduce_to_static_accessible_fallback(primitive_id):
    item = PRIMITIVE_BY_ID[primitive_id]
    text = " ".join(m.directive for m in item.mechanisms).lower()
    assert "not-added-wait-time" in text
    assert "never-delay-provider-or-network-execution" in text
    assert "never-withhold-ready-critical-information" in text
    assert "never-fake-loading-or-typing" in text
    assert "never-block-controls-for-temporal-effect" in text

    context = SemanticContext(viewport=Viewport.DESKTOP, reduced_motion=True, accessibility_required=True)
    projection = _project((primitive_id,), context=context)
    assert projection.is_valid
    resolved = [m for m in projection.mechanisms if m.source_unit_id == primitive_id]
    assert resolved
    assert all(m.degradation is DegradationState.ACCESSIBILITY_DEMOTED for m in resolved)
    assert all("static-immediate" in m.directive for m in resolved)


def test_all_miko_primitives_have_existing_truth_guard_not_story_inference():
    for item in MIKO_PRIMITIVES:
        text = " ".join(m.directive for m in item.mechanisms).lower()
        assert "only-when-corresponding-semantic-fields-or-relations-already-exist" in text
        assert "never-infer-or-create-role-kinship-agency-capability-care-status-hierarchy" in text
        assert "application-state" in text


def test_izzul_primitives_are_presentation_only_and_special_truth_guards_survive():
    for item in IZZUL_PRIMITIVES:
        text = " ".join(m.directive for m in item.mechanisms).lower()
        assert "existing-semantic-content-only" in text
        assert "never-create-domain-state-relationships-chronology-cultural-identity-or-provider-behavior" in text
    p16 = " ".join(m.directive for m in PRIMITIVE_BY_ID["P16"].mechanisms).lower()
    p22 = " ".join(m.directive for m in PRIMITIVE_BY_ID["P22"].mechanisms).lower()
    p25 = " ".join(m.directive for m in PRIMITIVE_BY_ID["P25"].mechanisms).lower()
    assert "never-live-or-invented-environment-state" in p16
    assert "never-create-rules-actions-or-permissions" in p22
    assert "never-asserts-a-cultural-lineage" in p25


def test_primitive_kind_firewall_rejects_primitive_as_reference():
    projection = resolve(
        _registry(),
        CompositionRequest(selected_reference_id="P01"),
        SemanticContext(),
    )
    assert not projection.is_valid
    assert projection.rejections
    assert "expected REFERENCE" in projection.rejections[0].message


def test_a_b_a_primitive_switching_is_reproducible():
    first_a = _project(("P01", "MK01", "TP01"))
    _ = _project(("P25", "MK25", "TP18"))
    second_a = _project(("P01", "MK01", "TP01"))
    assert first_a.is_valid and second_a.is_valid
    assert first_a.fingerprint == second_a.fingerprint
    assert first_a.mechanisms == second_a.mechanisms
