import pytest

from design_dna import (
    ASSET_ON_APPLICABLE,
    ASSET_ON_NOT_APPLICABLE,
    Axis,
    AxisAbsence,
    AbsenceState,
    CompositionRequest,
    DNARegistry,
    DNAUnit,
    DegradationState,
    ENGINE_BY_ID,
    ENVIRONMENT_ENGINE_IDS,
    M1_ENGINE_IDS,
    M1_ENGINES,
    MATERIAL_ENGINE_IDS,
    MechanismContract,
    SemanticContext,
    SemanticZone,
    UnitKind,
    Viewport,
    engine_asset_on_applicable,
    register_m1_engines,
    resolve,
)


def _reference():
    mechanism = MechanismContract(
        id="test-reference-form",
        axis=Axis.FORM,
        zones=(SemanticZone.U3,),
        directive="reference-structure",
        ownership_rank=90,
    )
    absences = tuple(
        AxisAbsence(axis, AbsenceState.NOT_APPLICABLE)
        for axis in Axis
        if axis is not Axis.FORM
    )
    return DNAUnit(
        id="ref-test",
        kind=UnitKind.REFERENCE,
        family="test-reference",
        lineage="test",
        provenance_pointer="tests://m1",
        mechanisms=(mechanism,),
        axis_absences=absences,
    )


def _projection(*engine_ids, context=None):
    registry = DNARegistry([_reference()])
    register_m1_engines(registry)
    return resolve(
        registry,
        CompositionRequest("ref-test", engine_ids=tuple(engine_ids)),
        context or SemanticContext(),
    )


def test_m1_membership_is_exact_locked_15_plus_14():
    assert MATERIAL_ENGINE_IDS == tuple(f"M{i}" for i in range(1, 16))
    assert ENVIRONMENT_ENGINE_IDS == tuple(f"E{i}" for i in range(1, 15))
    assert len(M1_ENGINE_IDS) == 29
    assert len(M1_ENGINES) == 29
    assert tuple(unit.id for unit in M1_ENGINES) == M1_ENGINE_IDS
    assert set(ENGINE_BY_ID) == set(M1_ENGINE_IDS)


def test_every_m1_unit_is_engine_and_covers_all_15_axes_explicitly():
    registry = DNARegistry(M1_ENGINES)
    assert len(registry.list_units(UnitKind.ENGINE)) == 29
    for unit in M1_ENGINES:
        mechanism_axes = {m.axis for m in unit.mechanisms}
        absence_axes = {a.axis for a in unit.axis_absences}
        assert mechanism_axes.isdisjoint(absence_axes)
        assert mechanism_axes | absence_axes == set(Axis)


def test_material_family_names_match_locked_corpus():
    expected = {
        "M1": "Paper / Fibrous Sheet",
        "M2": "Timber / Wood Assembly",
        "M3": "Stone / Masonry",
        "M4": "Concrete / Cast Monolith",
        "M5": "Metal / Fabricated",
        "M6": "Glass / Transparent Panel",
        "M7": "Textile / Woven",
        "M8": "Felt / Appliqué / Layered Cloth",
        "M9": "Barkcloth / Beaten Fiber Sheet",
        "M10": "Mosaic / Tessellated Unit",
        "M11": "Inlay / Host-Insert",
        "M12": "Lattice / Open Frame",
        "M13": "Ceramic / Glazed Unit",
        "M14": "Polished / Reflective Surface",
        "M15": "Patina / Wear",
    }
    assert {engine_id: ENGINE_BY_ID[engine_id].family for engine_id in MATERIAL_ENGINE_IDS} == expected


def test_environment_family_names_match_locked_corpus():
    expected = {
        "E1": "Daylight / Diffuse Day",
        "E2": "Direct Sun / Hard Light",
        "E3": "Night / Low Ambient",
        "E4": "Dawn / Dusk Transition",
        "E5": "Overcast / Diffuse Low-Contrast",
        "E6": "Rain",
        "E7": "Mist / Fog",
        "E8": "Snow / High-Albedo",
        "E9": "Forest / Canopy Filtered Light",
        "E10": "Water / Caustic-Reflective",
        "E11": "Urban Night / Multisource Light",
        "E12": "Interior Warm Local Light",
        "E13": "Desert / High-Exposure Dry Light",
        "E14": "Seasonal / Ecological Change",
    }
    assert {engine_id: ENGINE_BY_ID[engine_id].family for engine_id in ENVIRONMENT_ENGINE_IDS} == expected


def test_materials_own_construction_physics_not_texture_identity():
    for engine_id in MATERIAL_ENGINE_IDS:
        unit = ENGINE_BY_ID[engine_id]
        assert Axis.MATERIAL_CONSTRUCTION in {m.axis for m in unit.mechanisms}
        assert "material" in unit.provenance_pointer.lower()
        assert all("texture" not in m.directive.lower() for m in unit.mechanisms)


def test_environments_own_condition_axes_not_country_identity():
    for engine_id in ENVIRONMENT_ENGINE_IDS:
        unit = ENGINE_BY_ID[engine_id]
        axes = {m.axis for m in unit.mechanisms}
        assert axes & {Axis.LIGHT, Axis.ATMOSPHERE_ENVIRONMENT, Axis.MOTION_TEMPORAL}
        assert all(m.axis not in {Axis.TYPOGRAPHY_SCRIPT, Axis.SYMBOL_ICONOGRAPHY} for m in unit.mechanisms)


def test_engine_catalog_never_claims_historical_or_track_m_identity():
    text = "\n".join(
        [unit.id + " " + unit.family + " " + unit.lineage for unit in M1_ENGINES]
    ).lower()
    assert "track_m_r" not in text
    assert "historical track m" not in text
    assert all(unit.kind is UnitKind.ENGINE for unit in M1_ENGINES)


def test_batch2_asset_applicability_is_exactly_27_plus_e1_e5_na():
    assert ASSET_ON_NOT_APPLICABLE == {"E1", "E5"}
    assert len(ASSET_ON_APPLICABLE) == 27
    assert ASSET_ON_APPLICABLE | ASSET_ON_NOT_APPLICABLE == set(M1_ENGINE_IDS)
    assert not engine_asset_on_applicable("E1")
    assert not engine_asset_on_applicable("E5")
    assert all(engine_asset_on_applicable(i) for i in M1_ENGINE_IDS if i not in {"E1", "E5"})


def test_m1_has_no_actual_assets_before_asset_enrichment_batch():
    assert all(unit.assets == () for unit in M1_ENGINES)
    assert all(unit.identity_survival == "structural-engine-without-assets" for unit in M1_ENGINES)


def test_every_mechanism_has_desktop_tablet_mobile_contract():
    for unit in M1_ENGINES:
        for mechanism in unit.mechanisms:
            assert set(mechanism.viewports) == {"desktop", "tablet", "mobile"}


def test_reading_sanctuary_has_no_direct_m1_engine_ownership():
    for unit in M1_ENGINES:
        assert all(SemanticZone.U7 not in mechanism.zones for mechanism in unit.mechanisms)


def test_m15_narrative_watchpoint_forbids_application_age_status_health_semantics():
    m15 = ENGINE_BY_ID["M15"]
    narrative = next(m for m in m15.mechanisms if m.axis is Axis.NARRATIVE_SEQUENCING)
    text = narrative.directive.lower()
    assert "never-derived-from-application-age-status-or-health" in text
    assert narrative.fallback_directive == "static-neutral-wear-distribution"


def test_transitional_environments_are_presentation_only_and_state_neutral():
    for engine_id in ("E4", "E14"):
        temporal = next(m for m in ENGINE_BY_ID[engine_id].mechanisms if m.axis is Axis.MOTION_TEMPORAL)
        assert "presentation-only" in temporal.directive
        assert "never-mutating-application-state" in temporal.directive


def test_environment_contracts_have_no_live_feed_dependency():
    e5 = " ".join(m.directive for m in ENGINE_BY_ID["E5"].mechanisms)
    e6 = " ".join(m.directive for m in ENGINE_BY_ID["E6"].mechanisms)
    e14 = " ".join(m.directive for m in ENGINE_BY_ID["E14"].mechanisms)
    assert "without-weather-feed" in e5
    assert "without-live-weather-dependency" in e6
    assert "without-live-location-or-weather-feed" in e14


@pytest.mark.parametrize("engine_id", M1_ENGINE_IDS)
def test_every_engine_resolves_individually(engine_id):
    projection = _projection(engine_id)
    assert projection.is_valid
    assert any(item.source_unit_id == engine_id for item in projection.mechanisms)


@pytest.mark.parametrize("engine_id", M1_ENGINE_IDS)
def test_every_engine_resolves_on_mobile_without_identity_substitution(engine_id):
    projection = _projection(engine_id, context=SemanticContext(viewport=Viewport.MOBILE))
    assert projection.is_valid
    own = [item for item in projection.mechanisms if item.source_unit_id == engine_id]
    assert own
    assert all(item.viewport is Viewport.MOBILE for item in own)


@pytest.mark.parametrize("material_id", MATERIAL_ENGINE_IDS)
@pytest.mark.parametrize("environment_id", ENVIRONMENT_ENGINE_IDS)
def test_all_210_material_environment_pairs_are_composable(material_id, environment_id):
    projection = _projection(material_id, environment_id)
    assert projection.is_valid
    owners = {item.source_unit_id for item in projection.mechanisms}
    assert material_id in owners
    assert environment_id in owners


def test_material_and_environment_pair_resolves_without_type_or_registry_failure():
    projection = _projection("M2", "E1")
    assert projection.is_valid
    assert {item.source_unit_id for item in projection.mechanisms} >= {"M2", "E1", "ref-test"}


def test_asset_off_preserves_engine_structural_identity():
    projection = _projection("M10", "E11")
    assert projection.is_valid
    assert any(item.source_unit_id == "M10" for item in projection.mechanisms)
    assert any(item.source_unit_id == "E11" for item in projection.mechanisms)
    assert projection.asset_decisions == ()


def test_accessibility_super_veto_demotes_high_glare_mechanisms_to_fallback():
    projection = _projection("M14", "E8", context=SemanticContext(accessibility_required=True))
    assert projection.is_valid
    unsafe_ids = {"m14-reflection", "e8-high-albedo"}
    resolved = {m.mechanism_id: m for m in projection.mechanisms if m.mechanism_id in unsafe_ids}
    assert set(resolved) == unsafe_ids
    assert all(item.degradation is DegradationState.ACCESSIBILITY_DEMOTED for item in resolved.values())
    assert resolved["m14-reflection"].directive == "matte-low-glare-response"
    assert resolved["e8-high-albedo"].directive == "reduced-albedo-low-glare"


def test_reduced_motion_demotes_rain_caustic_and_seasonal_motion():
    for engine_id, mechanism_id in (
        ("E6", "e6-rain-motion"),
        ("E10", "e10-caustic-motion"),
        ("E14", "e14-seasonal-transition"),
    ):
        projection = _projection(engine_id, context=SemanticContext(reduced_motion=True))
        mechanism = next(m for m in projection.mechanisms if m.mechanism_id == mechanism_id)
        assert mechanism.degradation is DegradationState.ACCESSIBILITY_DEMOTED


def test_mobile_projection_uses_same_canonical_engine_identity():
    desktop = _projection("M12", "E7", context=SemanticContext(viewport=Viewport.DESKTOP))
    mobile = _projection("M12", "E7", context=SemanticContext(viewport=Viewport.MOBILE))
    assert desktop.is_valid and mobile.is_valid
    assert {m.source_unit_id for m in desktop.mechanisms} == {m.source_unit_id for m in mobile.mechanisms}
    assert all(m.viewport is Viewport.MOBILE for m in mobile.mechanisms)


def test_a_b_a_engine_switch_is_deterministic():
    a1 = _projection("M1", "E3")
    b = _projection("M5", "E12")
    a2 = _projection("M1", "E3")
    assert a1.fingerprint == a2.fingerprint
    assert a1.mechanisms == a2.mechanisms
    assert a1.fingerprint != b.fingerprint


def test_registry_registration_helper_is_exact_and_deterministic():
    registry = DNARegistry()
    register_m1_engines(registry)
    assert tuple(unit.id for unit in registry.list_units(UnitKind.ENGINE)) == tuple(sorted(M1_ENGINE_IDS))
