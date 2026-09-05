from design_dna import (
    DNARegistry,
    TEMPORAL_PRIMITIVE_IDS,
    UnitKind,
)
from design_dna.track_t import (
    TRACK_T_I_ASSET_ON_APPLICABLE,
    TRACK_T_I_ASSET_ON_NOT_APPLICABLE,
    TRACK_T_I_HISTORICAL_NON_ADDITIVE_PRIMITIVES,
    TRACK_T_I_NEAREST_NEGATIVE_BY_ID,
    TRACK_T_I_PRIMITIVE_FINGERPRINT_BY_ID,
    TRACK_T_I_REFERENCE_BY_ID,
    TRACK_T_I_REFERENCE_IDS,
    TRACK_T_I_REFERENCES,
    TRACK_T_I_TITLE_BY_ID,
    TRACK_T_I_TOPOLOGY_BY_ID,
    register_m7_track_t_i_references,
    track_t_i_reference_asset_on_applicable,
)


def test_exact_locked_denominator_titles_and_ids():
    assert TRACK_T_I_REFERENCE_IDS == tuple(f"TI{i:02d}" for i in range(1, 17))
    assert len(TRACK_T_I_TITLE_BY_ID) == len(TRACK_T_I_TOPOLOGY_BY_ID) == 16
    assert TRACK_T_I_TITLE_BY_ID["TI01"].startswith("Night Train")
    assert "Fukashigi no Carte" in TRACK_T_I_TITLE_BY_ID["TI12"]
    assert TRACK_T_I_TITLE_BY_ID["TI16"].startswith("Asayake to Nettaigyo")
    assert TRACK_T_I_HISTORICAL_NON_ADDITIVE_PRIMITIVES == ("TP19", "TP20")


def test_16_way_topology_and_nearest_negative_maps_are_total_and_self_distinct():
    assert set(TRACK_T_I_TOPOLOGY_BY_ID) == set(TRACK_T_I_REFERENCE_IDS)
    assert set(TRACK_T_I_NEAREST_NEGATIVE_BY_ID) == set(TRACK_T_I_REFERENCE_IDS)
    assert len(set(TRACK_T_I_TOPOLOGY_BY_ID.values())) == 16
    for reference_id, nearest in TRACK_T_I_NEAREST_NEGATIVE_BY_ID.items():
        assert nearest in TRACK_T_I_REFERENCE_IDS
        assert nearest != reference_id


def test_temporal_fingerprints_use_only_additive_tp01_tp18():
    additive = set(TEMPORAL_PRIMITIVE_IDS)
    assert len(additive) == 18
    assert set(TRACK_T_I_PRIMITIVE_FINGERPRINT_BY_ID) == set(TRACK_T_I_REFERENCE_IDS)
    for fingerprint in TRACK_T_I_PRIMITIVE_FINGERPRINT_BY_ID.values():
        assert fingerprint
        assert set(fingerprint).issubset(additive)
        assert not set(fingerprint).intersection(TRACK_T_I_HISTORICAL_NON_ADDITIVE_PRIMITIVES)


def test_every_reference_is_host_neutral_asset_off_safe_and_has_temporal_identity():
    assert len(TRACK_T_I_REFERENCES) == 16
    for reference in TRACK_T_I_REFERENCES:
        reference.validate()
        assert reference.kind is UnitKind.REFERENCE
        assert reference.assets == ()
        assert "asset-off" in reference.identity_survival
        directives = [item.directive for item in reference.mechanisms if item.id.endswith("-identity")]
        assert len(directives) == 1
        directive = directives[0]
        assert TRACK_T_I_TOPOLOGY_BY_ID[reference.id] in directive
        assert "designed-pacing-never-adds-wait-time" in directive
        assert "unresolved-tie-demotes-to-no-reference-specific-projection" in directive


def test_assets_are_optional_not_identity_dependencies():
    assert TRACK_T_I_ASSET_ON_APPLICABLE == frozenset(TRACK_T_I_REFERENCE_IDS)
    assert TRACK_T_I_ASSET_ON_NOT_APPLICABLE == frozenset()
    for reference_id in TRACK_T_I_REFERENCE_IDS:
        assert track_t_i_reference_asset_on_applicable(reference_id)


def test_registration_adds_exactly_16_unique_references():
    registry = DNARegistry()
    register_m7_track_t_i_references(registry)
    assert tuple(item.id for item in registry.list_units(UnitKind.REFERENCE)) == TRACK_T_I_REFERENCE_IDS
    assert set(TRACK_T_I_REFERENCE_BY_ID) == set(TRACK_T_I_REFERENCE_IDS)
