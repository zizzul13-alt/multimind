from design_dna import (
    COUNTRY_WEB_BY_ID,
    COUNTRY_WEB_REFERENCE_IDS,
    COUNTRY_WEB_REFERENCES,
    CULTURAL_TIER_S_IDS,
    DNARegistry,
    M2_REFERENCE_BY_ID,
    UnitKind,
    register_country_web_references,
    register_cultural_tier_s,
    register_m1_engines,
    register_m2_proving_references,
)


def test_country_web_canonical_objects_are_reused_from_m2():
    assert tuple(item.id for item in COUNTRY_WEB_REFERENCES) == COUNTRY_WEB_REFERENCE_IDS
    for item_id in COUNTRY_WEB_REFERENCE_IDS:
        assert COUNTRY_WEB_BY_ID[item_id] is M2_REFERENCE_BY_ID[item_id]


def test_country_web_plus_full_tier_s_plus_engines_register_without_duplicate_ids():
    registry = DNARegistry()
    register_m1_engines(registry)
    register_country_web_references(registry)
    register_cultural_tier_s(registry)

    references = registry.list_units(UnitKind.REFERENCE)
    engines = registry.list_units(UnitKind.ENGINE)
    assert len(references) == 21
    assert len(engines) == 29
    assert {item.id for item in references} == set(COUNTRY_WEB_REFERENCE_IDS) | set(CULTURAL_TIER_S_IDS)


def test_legacy_m2_combined_proving_registrar_remains_compatible_in_isolated_registry():
    registry = DNARegistry()
    register_m2_proving_references(registry)
    assert len(registry.list_units(UnitKind.REFERENCE)) == 9
