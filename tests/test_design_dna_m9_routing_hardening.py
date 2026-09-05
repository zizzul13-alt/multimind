from design_dna import DNARegistry, UnitKind
from design_dna.cultural_tier_b import (
    CULTURAL_TIER_B_BY_ID,
    CULTURAL_TIER_B_ROUTED_NON_ADDITIVE,
    register_cultural_tier_b,
)


def test_m9_generic_barkcloth_route_is_case_insensitive_and_non_additive():
    registry = DNARegistry()
    register_cultural_tier_b(registry)
    reference_ids = {item.id for item in registry.list_units(UnitKind.REFERENCE)}
    lineages = {item.lineage.lower() for item in registry.list_units(UnitKind.REFERENCE)}

    assert "CB05" not in reference_ids
    assert "CB05" not in CULTURAL_TIER_B_BY_ID
    assert CULTURAL_TIER_B_ROUTED_NON_ADDITIVE["CB05"].startswith("generic Barkcloth -> Material M9")
    assert all("barkcloth" not in lineage for lineage in lineages)


def test_m9_route_metadata_cannot_be_registered_as_a_reference_unit():
    assert set(CULTURAL_TIER_B_ROUTED_NON_ADDITIVE) == {"CB05"}
    assert set(CULTURAL_TIER_B_BY_ID).isdisjoint(CULTURAL_TIER_B_ROUTED_NON_ADDITIVE)
