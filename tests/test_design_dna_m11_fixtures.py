import pytest

from design_dna import (
    AssetState,
    CompositionRequest,
    DNARegistry,
    UnitKind,
    UnitKindMismatchError,
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
)
from design_dna.fixtures import (
    FIXTURE_ASSET_ON_APPLICABLE,
    FIXTURE_ASSET_ON_NOT_APPLICABLE,
    FIXTURE_BY_ID,
    FIXTURE_COMPOSITION_BY_ID,
    FIXTURE_EVIDENCE_STATE_BY_ID,
    M11_FIXTURE_IDS,
    M11_FIXTURES,
    M11_HISTORICAL_NON_ADDITIVE,
    fixture_asset_on_applicable,
    fixture_projection_contract,
    register_m11_fixtures,
)
from design_dna.track_m_r import register_track_m_r

ASSET_STATES = tuple(AssetState)
VIEWPORTS = tuple(Viewport)


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
    register_m11_fixtures(registry)
    return registry


def test_exact_additive_fixture_denominator_and_f11_firewall():
    assert M11_FIXTURE_IDS == (
        "F01", "F02", "F03", "F04", "F05", "F06", "F07",
        "F08", "F09", "F10", "F12", "F13", "F14", "F15",
    )
    assert len(M11_FIXTURE_IDS) == len(M11_FIXTURES) == len(FIXTURE_BY_ID) == 14
    assert set(M11_HISTORICAL_NON_ADDITIVE) == {"F11"}
    assert "F11" not in FIXTURE_BY_ID


def test_fixture_is_its_own_unit_kind_and_registry_reaches_exact_271():
    registry = _registry()
    assert len(registry.list_units(UnitKind.REFERENCE)) == 160
    assert len(registry.list_units(UnitKind.ENGINE)) == 29
    assert len(registry.list_units(UnitKind.PRIMITIVE)) == 68
    assert len(registry.list_units(UnitKind.FIXTURE)) == 14
    assert len(registry.list_units()) == 271
    assert all(item.kind is UnitKind.FIXTURE for item in registry.list_units(UnitKind.FIXTURE))


def test_fixture_cannot_be_smuggled_into_reference_selection():
    registry = _registry()
    with pytest.raises(UnitKindMismatchError):
        registry.select(CompositionRequest(selected_reference_id="F02"))


def test_asset_applicability_arithmetic_and_no_fixture_owned_collage_assets():
    assert FIXTURE_ASSET_ON_APPLICABLE == {
        "F01", "F02", "F04", "F07", "F08", "F09", "F12", "F13", "F15",
    }
    assert FIXTURE_ASSET_ON_NOT_APPLICABLE == {"F03", "F05", "F06", "F10", "F14"}
    assert FIXTURE_ASSET_ON_APPLICABLE.isdisjoint(FIXTURE_ASSET_ON_NOT_APPLICABLE)
    assert FIXTURE_ASSET_ON_APPLICABLE | FIXTURE_ASSET_ON_NOT_APPLICABLE == set(M11_FIXTURE_IDS)
    assert sum(bool(unit.assets) for unit in M11_FIXTURES) == 0


def test_recovered_compositions_are_bounded_and_missing_marriages_are_not_fabricated():
    assert FIXTURE_COMPOSITION_BY_ID["F02"] == "Rinpa × Japan High-Density Information × Chat-first"
    assert FIXTURE_COMPOSITION_BY_ID["F03"] == "Czech Cubism × Netherlands Concept-First Web × Agent Canvas"
    assert FIXTURE_COMPOSITION_BY_ID["F05"] == "Quipu × China Service Convergence × Command Center"
    assert FIXTURE_COMPOSITION_BY_ID["F06"] == "Neo-Concrete × Silicon Valley Product Web × Workspace"
    assert FIXTURE_COMPOSITION_BY_ID["F12"] == "Māori Wharenui Relational × Aotearoa Bicultural Web × Research Lab"
    assert FIXTURE_COMPOSITION_BY_ID["F13"] == "Art Deco × Italy Editorial lens × Minimal SaaS"
    assert FIXTURE_COMPOSITION_BY_ID["F14"] == "Marshallese Navigation × Germany Rational lens × Agent Canvas"
    assert FIXTURE_COMPOSITION_BY_ID["F15"] == "Japan Print/Ink × U.S./Silicon Valley Product Web × Chat-first"
    unknown = {fixture_id for fixture_id, value in FIXTURE_COMPOSITION_BY_ID.items() if value.startswith("UNKNOWN_ORIGINAL_COMPOSITION")}
    assert unknown == {"F01", "F04", "F07", "F08", "F09", "F10"}
    assert all(FIXTURE_EVIDENCE_STATE_BY_ID[item] == "BOUNDED_EVIDENCE_GAP" for item in unknown)


@pytest.mark.parametrize("fixture_id", M11_FIXTURE_IDS)
@pytest.mark.parametrize("viewport", VIEWPORTS)
@pytest.mark.parametrize("asset_state", ASSET_STATES)
def test_all_fixtures_project_deterministically_across_viewport_and_asset_state(fixture_id, viewport, asset_state):
    first = fixture_projection_contract(fixture_id, viewport=viewport, asset_state=asset_state)
    second = fixture_projection_contract(fixture_id, viewport=viewport, asset_state=asset_state)
    assert first == second
    assert first.fixture_id == fixture_id
    assert first.fixture_owned_asset is False
    assert "semantic-state-precedes-presentation" in first.structural_directives
    assert "fixture-selection-never-promotes-or-mutates-underlying-reference-truth" in first.structural_directives
    if asset_state is AssetState.OFF:
        assert first.asset_enrichment_allowed is False
    else:
        assert first.asset_enrichment_allowed is fixture_asset_on_applicable(fixture_id)


@pytest.mark.parametrize("fixture_id", M11_FIXTURE_IDS)
def test_reading_sanctuary_is_superior_to_fixture_theatricality(fixture_id):
    projection = fixture_projection_contract(fixture_id, reading_sanctuary=True)
    assert any("reading-sanctuary-demotes" in item for item in projection.structural_directives)


@pytest.mark.parametrize("fixture_id", M11_FIXTURE_IDS)
def test_reduced_motion_preserves_identity_and_only_changes_transition_law(fixture_id):
    normal = fixture_projection_contract(fixture_id, reduced_motion=False)
    reduced = fixture_projection_contract(fixture_id, reduced_motion=True)
    assert normal.fixture_id == reduced.fixture_id
    assert normal.composition == reduced.composition
    assert normal.evidence_state == reduced.evidence_state
    assert any("reduced-motion-removes" in item for item in reduced.structural_directives)


@pytest.mark.parametrize("fixture_id", M11_FIXTURE_IDS)
def test_evidence_gap_fixture_explicitly_fails_closed_instead_of_inventing_marriage(fixture_id):
    projection = fixture_projection_contract(fixture_id)
    if projection.evidence_state == "BOUNDED_EVIDENCE_GAP":
        assert projection.composition.startswith("UNKNOWN_ORIGINAL_COMPOSITION")
        assert "unknown-original-marriage-remains-explicit-and-must-not-be-invented" in projection.structural_directives
    else:
        assert not projection.composition.startswith("UNKNOWN_ORIGINAL_COMPOSITION")


def test_unknown_fixture_and_wrong_runtime_types_fail_explicitly():
    with pytest.raises(KeyError):
        fixture_projection_contract("F11")
    with pytest.raises(KeyError):
        fixture_asset_on_applicable("F11")
    with pytest.raises(TypeError):
        fixture_projection_contract("F02", viewport="mobile")
    with pytest.raises(TypeError):
        fixture_projection_contract("F02", asset_state="off")
