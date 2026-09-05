from design_dna import DNARegistry, UnitKind
from design_dna.cultural_tier_a import (
    CULTURAL_TIER_A_ASSET_ON_APPLICABLE,
    CULTURAL_TIER_A_ASSET_ON_NOT_APPLICABLE,
    CULTURAL_TIER_A_BY_ID,
    CULTURAL_TIER_A_EVIDENCE_MODE_BY_ID,
    CULTURAL_TIER_A_HISTORICAL_NON_ADDITIVE,
    CULTURAL_TIER_A_IDS,
    CULTURAL_TIER_A_NAME_BY_ID,
    CULTURAL_TIER_A_RECOVERED_EXAMPLE_IDS,
    CULTURAL_TIER_A_REFERENCES,
    cultural_tier_a_asset_on_applicable,
    register_cultural_tier_a,
)

EXPECTED_IDS = (
    "CA01", "CA04", "CA08", "CA09", "CA10", "CA11", "CA12", "CA13",
    "CA14", "CA15", "CA16", "CA17", "CA18", "CA19", "CA20", "CA21",
    "CA22", "CA23", "CA24", "CA25", "CA26", "CA27", "CA28", "CA29",
    "CA30", "CA32", "CA34", "CA35", "CA36",
)


def test_locked_additive_denominator_and_canonical_gap_preservation():
    assert CULTURAL_TIER_A_IDS == EXPECTED_IDS
    assert len(CULTURAL_TIER_A_IDS) == 29
    assert len(CULTURAL_TIER_A_NAME_BY_ID) == 29
    assert CULTURAL_TIER_A_NAME_BY_ID["CA01"] == "Batik"
    assert CULTURAL_TIER_A_NAME_BY_ID["CA34"] == "Māori Wharenui"
    assert CULTURAL_TIER_A_NAME_BY_ID["CA36"] == "Ngatu"


def test_seven_historical_holds_are_accounted_but_not_additive():
    assert CULTURAL_TIER_A_HISTORICAL_NON_ADDITIVE == {
        "CA02": "Vernacular Street",
        "CA03": "Poetic Editorial",
        "CA05": "Computational Experimental",
        "CA06": "Calligraphic Kinetic",
        "CA07": "Miniature Narrative Field",
        "CA31": "Gingerbread",
        "CA33": "Constructive Symbol Grid",
    }
    assert set(CULTURAL_TIER_A_IDS).isdisjoint(CULTURAL_TIER_A_HISTORICAL_NON_ADDITIVE)


def test_epistemic_modes_do_not_overclaim_uniform_row_recovery():
    assert len(CULTURAL_TIER_A_RECOVERED_EXAMPLE_IDS) == 12
    assert set(CULTURAL_TIER_A_EVIDENCE_MODE_BY_ID) == set(CULTURAL_TIER_A_IDS)
    assert sum(mode == "RECOVERED_MECHANISM_EXAMPLE" for mode in CULTURAL_TIER_A_EVIDENCE_MODE_BY_ID.values()) == 12
    assert sum(mode == "BOUNDED_TRANSLATION" for mode in CULTURAL_TIER_A_EVIDENCE_MODE_BY_ID.values()) == 17


def test_recovered_examples_keep_surviving_mechanism_distinctions():
    directives = {
        ref_id: next(item.directive for item in CULTURAL_TIER_A_BY_ID[ref_id].mechanisms if item.id.endswith("-identity"))
        for ref_id in CULTURAL_TIER_A_RECOVERED_EXAMPLE_IDS
    }
    assert "resist-and-layer" in directives["CA01"]
    assert "reusable-promotional-carrier" in directives["CA04"]
    assert "staged-descent-depth-and-reveal" in directives["CA08"]
    assert "interlocking-geometry" in directives["CA11"]
    assert "radial-enclosure" in directives["CA12"]
    assert "modular-cut-and-joined" in directives["CA13"]
    assert "perimeter-gate-core" in directives["CA17"]
    assert "controlled-asymmetry" in directives["CA18"]


def test_every_tier_a_unit_is_host_neutral_asset_off_safe_and_truth_bounded():
    assert len(CULTURAL_TIER_A_REFERENCES) == 29
    for reference in CULTURAL_TIER_A_REFERENCES:
        reference.validate()
        assert reference.kind is UnitKind.REFERENCE
        assert reference.assets == ()
        assert "asset-off" in reference.identity_survival
        identity = [item.directive for item in reference.mechanisms if item.id.endswith("-identity")]
        assert len(identity) == 1
        assert "project-abstraction-is-not-universal-cultural-truth" in identity[0]
        firewall = [item.directive for item in reference.mechanisms if item.id.endswith("-semantic-firewall")]
        assert len(firewall) == 1
        assert "may-not-invent-chronology-hierarchy-authority" in firewall[0]


def test_asset_applicable_is_not_asset_required():
    assert CULTURAL_TIER_A_ASSET_ON_APPLICABLE == frozenset(CULTURAL_TIER_A_IDS)
    assert CULTURAL_TIER_A_ASSET_ON_NOT_APPLICABLE == frozenset()
    for ref_id in CULTURAL_TIER_A_IDS:
        assert cultural_tier_a_asset_on_applicable(ref_id)
        assert CULTURAL_TIER_A_BY_ID[ref_id].assets == ()


def test_registration_adds_exactly_29_unique_references():
    registry = DNARegistry()
    register_cultural_tier_a(registry)
    assert tuple(item.id for item in registry.list_units(UnitKind.REFERENCE)) == CULTURAL_TIER_A_IDS
