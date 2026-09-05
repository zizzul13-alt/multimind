import inspect

import pytest

import design_dna.izzul as izzul_module
from design_dna import (
    DNARegistry,
    IZZUL_ALIASES_BY_ID,
    IZZUL_ANIME_IDS,
    IZZUL_ASSET_ON_APPLICABLE,
    IZZUL_ASSET_ON_NOT_APPLICABLE,
    IZZUL_EVIDENCE_MODE_BY_ID,
    IZZUL_MANGA_IDS,
    IZZUL_MECHANISM_BY_ID,
    IZZUL_MEDIUM_BY_ID,
    IZZUL_PRIMITIVE_FINGERPRINT_BY_ID,
    IZZUL_PRIMITIVE_IDS,
    IZZUL_REFERENCE_BY_ID,
    IZZUL_REFERENCE_IDS,
    IZZUL_REFERENCES,
    IZZUL_TITLE_BY_ID,
    IZZUL_WEBTOON_IDS,
    SemanticZone,
    UnitKind,
    izzul_reference_asset_on_applicable,
    register_m5_izzul_references,
)

EXPECTED_ANIME = (
    "Chainsaw Man",
    "The Tatami Galaxy",
    "Samurai Champloo",
    "Mushishi",
    "Psycho-Pass",
    "Mononoke",
    "Serial Experiments Lain",
    "Ping Pong the Animation",
    "Land of the Lustrous",
    "Mob Psycho 100",
    "Cowboy Bebop",
    "Neon Genesis Evangelion",
    "Violet Evergarden",
    "Ghost in the Shell",
    "Made in Abyss",
)
EXPECTED_MANGA = (
    "Fire Punch",
    "BLAME!",
    "Berserk",
    "AKIRA",
    "Vagabond",
    "Witch Hat Atelier",
    "Dorohedoro",
    "Girls' Last Tour",
    "Oyasumi Punpun",
    "JoJo's Bizarre Adventure",
    "Nausicaä of the Valley of the Wind",
)
EXPECTED_WEBTOON = (
    "Tyrant of the Tower Defense Game",
    "Tower of God",
    "Omniscient Reader's Viewpoint",
    "Solo Leveling",
    "The Horizon",
    "The Boxer",
    "Bastard",
    "The Legend of the Northern Blade",
    "Her Summon",
    "The Greatest Estate Developer",
)


def test_exact_m5_census_and_partition_are_locked():
    assert len(IZZUL_ANIME_IDS) == 15
    assert len(IZZUL_MANGA_IDS) == 11
    assert len(IZZUL_WEBTOON_IDS) == 10
    assert len(IZZUL_REFERENCE_IDS) == len(set(IZZUL_REFERENCE_IDS)) == 36
    assert IZZUL_REFERENCE_IDS == IZZUL_ANIME_IDS + IZZUL_MANGA_IDS + IZZUL_WEBTOON_IDS
    assert tuple(IZZUL_TITLE_BY_ID[item] for item in IZZUL_ANIME_IDS) == EXPECTED_ANIME
    assert tuple(IZZUL_TITLE_BY_ID[item] for item in IZZUL_MANGA_IDS) == EXPECTED_MANGA
    assert tuple(IZZUL_TITLE_BY_ID[item] for item in IZZUL_WEBTOON_IDS) == EXPECTED_WEBTOON


def test_medium_metadata_matches_locked_15_11_10_partition():
    assert sum(value == "ANIME" for value in IZZUL_MEDIUM_BY_ID.values()) == 15
    assert sum(value == "MANGA" for value in IZZUL_MEDIUM_BY_ID.values()) == 11
    assert sum(value == "MANHWA_WEBTOON" for value in IZZUL_MEDIUM_BY_ID.values()) == 10
    assert set(IZZUL_MEDIUM_BY_ID) == set(IZZUL_REFERENCE_IDS)


def test_tyrant_historical_alias_is_metadata_not_duplicate_reference():
    assert IZZUL_ALIASES_BY_ID == {"IZW01": ("I Became the Tyrant of a Defense Game",)}
    assert "I Became the Tyrant of a Defense Game" not in IZZUL_TITLE_BY_ID.values()


def test_every_reference_is_asset_applicable_but_m5_requires_zero_assets():
    assert IZZUL_ASSET_ON_APPLICABLE == frozenset(IZZUL_REFERENCE_IDS)
    assert IZZUL_ASSET_ON_NOT_APPLICABLE == frozenset()
    for reference in IZZUL_REFERENCES:
        assert reference.assets == ()
        assert izzul_reference_asset_on_applicable(reference.id) is True
        assert "asset-off" in reference.identity_survival


def test_unknown_asset_applicability_lookup_fails_closed():
    with pytest.raises(KeyError):
        izzul_reference_asset_on_applicable("UNKNOWN")


def test_all_reference_units_validate_and_are_reference_kind():
    assert len(IZZUL_REFERENCES) == 36
    assert len(IZZUL_REFERENCE_BY_ID) == 36
    for reference in IZZUL_REFERENCES:
        reference.validate()
        assert reference.kind is UnitKind.REFERENCE
        assert reference.id in IZZUL_TITLE_BY_ID
        assert reference.mechanisms
        assert reference.provenance_pointer
        assert all(SemanticZone.U9 not in mechanism.zones for mechanism in reference.mechanisms)


def test_all_fingerprints_use_only_locked_izzul_primitives():
    allowed = set(IZZUL_PRIMITIVE_IDS)
    assert set(IZZUL_PRIMITIVE_FINGERPRINT_BY_ID) == set(IZZUL_REFERENCE_IDS)
    for reference_id, fingerprint in IZZUL_PRIMITIVE_FINGERPRINT_BY_ID.items():
        assert fingerprint
        assert len(fingerprint) == len(set(fingerprint))
        assert set(fingerprint).issubset(allowed), reference_id


def test_evidence_mode_is_explicit_and_bounded_for_every_reference():
    assert set(IZZUL_EVIDENCE_MODE_BY_ID) == set(IZZUL_REFERENCE_IDS)
    assert set(IZZUL_EVIDENCE_MODE_BY_ID.values()) == {"LOCKED_RECOVERED", "CONSERVATIVE_TRANSLATION"}
    assert sum(value == "LOCKED_RECOVERED" for value in IZZUL_EVIDENCE_MODE_BY_ID.values()) >= 15
    assert sum(value == "CONSERVATIVE_TRANSLATION" for value in IZZUL_EVIDENCE_MODE_BY_ID.values()) >= 1


def test_directives_disclose_evidence_mode_and_never_require_direct_ip():
    banned_required = ("require-character", "require-panel", "require-logo", "require-franchise", "copied-composition-required")
    for reference in IZZUL_REFERENCES:
        identity = next(item for item in reference.mechanisms if item.id.endswith("-identity"))
        assert "evidence-mode=" in identity.directive
        assert "never-require-or-reproduce" in identity.directive
        assert not any(token in identity.directive for token in banned_required)


def test_tyrant_final_wave_e_lock_is_preserved():
    assert IZZUL_MECHANISM_BY_ID["IZW01"] == "STRATEGIC_CONTEXT_INTERVALIZATION"
    assert IZZUL_PRIMITIVE_FINGERPRINT_BY_ID["IZW01"] == ("P02", "P13", "P05", "P17")
    identity = next(item for item in IZZUL_REFERENCE_BY_ID["IZW01"].mechanisms if item.id.endswith("-identity"))
    assert "real-existing-planning-or-context-information" in identity.directive
    assert "fictional-game-state" in identity.directive
    assert "MULTIMIND_DESIGN_DNA_WAVE_E_RESIDUAL_CLOSURE_v5.md" in IZZUL_REFERENCE_BY_ID["IZW01"].provenance_pointer


def test_her_summon_final_wave_e_lock_is_preserved():
    assert IZZUL_MECHANISM_BY_ID["IZW09"] == "DIFFERENTIAL_TEXTURE_FIGURE_GROUND_STAGING"
    assert IZZUL_PRIMITIVE_FINGERPRINT_BY_ID["IZW09"] == ("P18", "P03", "P02", "P16")
    identity = next(item for item in IZZUL_REFERENCE_BY_ID["IZW09"].mechanisms if item.id.endswith("-identity"))
    assert "P16-environmental-causality-is-conditional" in identity.directive
    assert "real-context-is-causal-or-informative" in identity.directive
    assert "HER_SUMMON_DEEP_CLOSURE_v6" in IZZUL_REFERENCE_BY_ID["IZW09"].provenance_pointer


@pytest.mark.parametrize(
    "reference_id,mechanism",
    (
        ("IZM01", "STATIC_FRAME_TEMPORAL_TRACE_ABRUPT_CONTRAST"),
        ("IZW05", "CONTRASTIVE_NEGATIVE_SPACE_TONAL_DENSITY_PACING"),
        ("IZW06", "SCROLL_REVEAL_GEOMETRY_BOUNDED_SEQUENTIAL_IMPACT"),
        ("IZW08", "SPATIALLY_TRACEABLE_FORCE_PATH_CHOREOGRAPHY"),
        ("IZW10", "TECHNICAL_CONTEXT_EXAGGERATED_REACTION_REGISTER_SWITCH"),
    ),
)
def test_wave_e_v3_recovered_mechanism_reformulations_are_preserved(reference_id, mechanism):
    assert IZZUL_MECHANISM_BY_ID[reference_id] == mechanism
    assert IZZUL_EVIDENCE_MODE_BY_ID[reference_id] == "LOCKED_RECOVERED"
    assert "WAVE_E_IZZUL_CORPUS_EQUALIZATION_v3" in IZZUL_REFERENCE_BY_ID[reference_id].provenance_pointer


@pytest.mark.parametrize(
    "reference_id,mechanism",
    (
        ("IZA04", "QUIET_THRESHOLD_PROGRESSIVE_REVEAL"),
        ("IZA05", "INSTITUTIONAL_SYSTEM_STATE_MEDIATION"),
        ("IZA06", "ORNAMENT_AS_PLANAR_SPATIAL_PARTITION"),
        ("IZA07", "MEDIATED_PRESENCE_NETWORK_AMBIGUITY"),
        ("IZA08", "MOTION_INDUCED_DEFORMATION"),
        ("IZA09", "REFRACTIVE_FRAGMENTATION_STATE"),
        ("IZA12", "OPERATIONAL_TYPOGRAPHY_SYSTEM_HIERARCHY"),
        ("IZA13", "CORRESPONDENCE_DOCUMENT_MATERIALITY"),
        ("IZA14", "EMBODIED_SYSTEM_NETWORK_BOUNDARY"),
        ("IZA15", "LAYERED_DEPTH_IRREVERSIBLE_TRAVERSAL"),
    ),
)
def test_surviving_b7_mechanism_lineage_is_preserved(reference_id, mechanism):
    assert IZZUL_MECHANISM_BY_ID[reference_id] == mechanism
    assert IZZUL_EVIDENCE_MODE_BY_ID[reference_id] == "LOCKED_RECOVERED"


def test_registration_adds_exactly_36_unique_references():
    registry = DNARegistry()
    register_m5_izzul_references(registry)
    assert tuple(item.id for item in registry.list_units(UnitKind.REFERENCE)) == tuple(sorted(IZZUL_REFERENCE_IDS))


def test_catalog_has_no_framework_core_provider_database_or_network_imports():
    source = inspect.getsource(izzul_module)
    banned = (
        "import reflex",
        "from reflex",
        "import streamlit",
        "from streamlit",
        "from core",
        "import core",
        "from providers",
        "import providers",
        "from database",
        "import database",
        "requests.",
        "httpx.",
    )
    assert not any(token in source for token in banned)


def test_m5_catalog_contains_no_runtime_per_id_if_forest():
    source = inspect.getsource(izzul_module)
    # Two explicit ID conditions are allowed only for provenance and hard truth
    # guards (Tyrant/Her Summon); mass title behavior must stay data-driven.
    assert source.count('reference_id == "') <= 4
