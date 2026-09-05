import inspect

import pytest

import design_dna.miko as miko_module
from design_dna import (
    DNARegistry,
    MIKO_ALIASES_BY_ID,
    MIKO_ASSET_ON_APPLICABLE,
    MIKO_ASSET_ON_NOT_APPLICABLE,
    MIKO_EVIDENCE_MODE_BY_ID,
    MIKO_HISTORICAL_ID_BY_ID,
    MIKO_MECHANISM_BY_ID,
    MIKO_MEDIUM_BY_ID,
    MIKO_PRIMITIVE_FINGERPRINT_BY_ID,
    MIKO_PRIMITIVE_IDS,
    MIKO_REFERENCE_BY_ID,
    MIKO_REFERENCE_IDS,
    MIKO_REFERENCES,
    MIKO_TITLE_BY_ID,
    SemanticZone,
    UnitKind,
    miko_reference_asset_on_applicable,
    register_m6_miko_references,
)

EXPECTED_TITLES = (
    "What's Wrong With Being the Villainess?",
    "There Are No Bad Young Ladies in This World (Noble Lady Reformation Guide)",
    "The Villainess I Possessed Is Raising Hell",
    "The Father and the Daughter",
    "Shut Up, Evil Dragon, I Don't Want to Raise a Child With You Anymore",
    "She's Not Our Daughter!",
    "Rojiura de Hirotta Onnanoko ga Bad End-go no Otome Game no Heroine Datta Ken",
    "Reincarnated as a Villainous Duke to Be Condemned by My Daughter",
    "My Sister Is the Main Character",
    "My Daddy Hides His Power",
    "Love Letter From The Future",
    "I Will Raise the Villain Properly",
    "I Need to Raise My Sister Properly",
    "I Became The Tyrant's Dying Wife",
    "I Became the Male Lead's Adopted Daughter",
    "I Became a Patron of Villains",
    "How Can You Pay Back The Kindness I Raised With Obsession?",
    "Otome Game Sekai wa Mob ni Kibishii Sekai Desu",
    "Get Out Of The Way, I'll Decide The Ending Now!",
    "The Extra's Academy Survival Guide",
    "Mob Shisai dakedo, Kono Sekai ga Otome Game dato Kizuita node Heroine o Ikusei Shimasu",
    "50 Ways to Dump the Psychopathic Mastermind",
    "A Princess Who Reads Fortune.",
)


def _identity(reference_id):
    return next(item for item in MIKO_REFERENCE_BY_ID[reference_id].mechanisms if item.id.endswith("-identity"))


def test_exact_m6_census_and_historical_wave_f_mapping_are_locked():
    assert len(MIKO_REFERENCE_IDS) == len(set(MIKO_REFERENCE_IDS)) == 23
    assert MIKO_REFERENCE_IDS == tuple(f"MKREF{i:02d}" for i in range(1, 24))
    assert tuple(MIKO_TITLE_BY_ID[item] for item in MIKO_REFERENCE_IDS) == EXPECTED_TITLES
    assert tuple(MIKO_HISTORICAL_ID_BY_ID[item] for item in MIKO_REFERENCE_IDS) == tuple(f"F{i:02d}" for i in range(1, 24))


def test_runtime_ids_do_not_consume_future_fixture_f_namespace():
    assert all(not item.startswith("F") for item in MIKO_REFERENCE_IDS)
    assert set(MIKO_REFERENCE_IDS).isdisjoint({f"F{i:02d}" for i in range(1, 15)})


def test_known_aliases_are_metadata_not_duplicate_references():
    assert MIKO_ALIASES_BY_ID["MKREF01"] == ("The Perks of Being a Villainess",)
    assert MIKO_ALIASES_BY_ID["MKREF15"] == ("The Male Lead's Little Lion Daughter",)
    assert MIKO_ALIASES_BY_ID["MKREF18"] == ("Trapped in a Dating Sim",)
    for aliases in MIKO_ALIASES_BY_ID.values():
        for alias in aliases:
            assert alias not in MIKO_TITLE_BY_ID.values()


def test_medium_metadata_is_bounded_and_does_not_invent_anime_family():
    assert set(MIKO_MEDIUM_BY_ID) == set(MIKO_REFERENCE_IDS)
    assert sum(value == "MANHWA_WEBTOON" for value in MIKO_MEDIUM_BY_ID.values()) == 18
    assert sum(value == "MANGA" for value in MIKO_MEDIUM_BY_ID.values()) == 4
    assert sum(value == "MANHUA_TITLE_BOUNDED" for value in MIKO_MEDIUM_BY_ID.values()) == 1
    assert "ANIME" not in MIKO_MEDIUM_BY_ID.values()


def test_every_reference_is_asset_applicable_but_m6_requires_zero_assets():
    assert MIKO_ASSET_ON_APPLICABLE == frozenset(MIKO_REFERENCE_IDS)
    assert MIKO_ASSET_ON_NOT_APPLICABLE == frozenset()
    for reference in MIKO_REFERENCES:
        assert reference.assets == ()
        assert miko_reference_asset_on_applicable(reference.id) is True
        assert "asset-off" in reference.identity_survival


def test_unknown_asset_applicability_lookup_fails_closed():
    with pytest.raises(KeyError):
        miko_reference_asset_on_applicable("UNKNOWN")


def test_all_reference_units_validate_and_are_reference_kind():
    assert len(MIKO_REFERENCES) == 23
    assert len(MIKO_REFERENCE_BY_ID) == 23
    for reference in MIKO_REFERENCES:
        reference.validate()
        assert reference.kind is UnitKind.REFERENCE
        assert reference.id in MIKO_TITLE_BY_ID
        assert reference.mechanisms
        assert reference.provenance_pointer
        assert all(SemanticZone.U9 not in item.zones for item in reference.mechanisms)


def test_all_fingerprints_use_only_locked_miko_primitives():
    allowed = set(MIKO_PRIMITIVE_IDS)
    assert set(MIKO_PRIMITIVE_FINGERPRINT_BY_ID) == set(MIKO_REFERENCE_IDS)
    for reference_id, fingerprint in MIKO_PRIMITIVE_FINGERPRINT_BY_ID.items():
        assert fingerprint
        assert len(fingerprint) == len(set(fingerprint))
        assert set(fingerprint).issubset(allowed), reference_id


def test_evidence_modes_are_explicit_and_do_not_overclaim_missing_rows():
    assert set(MIKO_EVIDENCE_MODE_BY_ID) == set(MIKO_REFERENCE_IDS)
    assert set(MIKO_EVIDENCE_MODE_BY_ID.values()) == {
        "LOCKED_RECOVERED",
        "BRIEF_RECOVERED",
        "BOUNDED_TRANSLATION",
    }
    assert sum(value == "LOCKED_RECOVERED" for value in MIKO_EVIDENCE_MODE_BY_ID.values()) == 5
    assert sum(value == "BRIEF_RECOVERED" for value in MIKO_EVIDENCE_MODE_BY_ID.values()) == 9
    assert sum(value == "BOUNDED_TRANSLATION" for value in MIKO_EVIDENCE_MODE_BY_ID.values()) == 9


def test_every_identity_directive_is_truth_guarded_and_direct_ip_free():
    banned_required = (
        "require-character",
        "require-panel",
        "require-logo",
        "require-cover",
        "copied-source-composition-required",
    )
    for reference_id in MIKO_REFERENCE_IDS:
        directive = _identity(reference_id).directive
        assert "evidence-mode=" in directive
        assert "primitive-fingerprint=" in directive
        assert "never-fabricate-kinship-care-affection-trust-consent-capability-authority-history-timeline-resource-control-forecast-certainty-or-outcome-ownership" in directive
        assert "never-require-or-reproduce" in directive
        assert not any(token in directive for token in banned_required)


@pytest.mark.parametrize(
    "reference_id,mechanism",
    (
        ("MKREF03", "HOST_WISH_CONTRACT_UNDER_BORROWED_IDENTITY"),
        ("MKREF05", "ADVERSARIAL_CO_PARENTING_UNDER_NON_OPTIONAL_SHARED_RESPONSIBILITY"),
        ("MKREF09", "FATE_SUBSTITUTION_THROUGH_ROLE_ASSUMPTION"),
        ("MKREF13", "SIBLING_TRAJECTORY_STEWARDSHIP_WITHOUT_ROLE_SUBSTITUTION"),
        ("MKREF14", "DEADLINE_BOUNDED_MUTUAL_STABILIZATION_WITH_PLANNED_EXIT"),
    ),
)
def test_wave_f_final_lock_mechanisms_survive_exactly(reference_id, mechanism):
    assert MIKO_MECHANISM_BY_ID[reference_id] == mechanism
    assert MIKO_EVIDENCE_MODE_BY_ID[reference_id] == "LOCKED_RECOVERED"
    assert "MULTIMIND_DESIGN_DNA_WAVE_F_LOCK_CHECKPOINT_v1.md" in MIKO_REFERENCE_BY_ID[reference_id].provenance_pointer


def test_f09_f13_collision_lock_is_projection_behavior_not_wording_only():
    f09 = _identity("MKREF09").directive
    f13 = _identity("MKREF13").directive
    assert "actual-structural-burden-transfer" in f09
    assert "must-not-transfer-target-role-ownership" in f13
    assert MIKO_PRIMITIVE_FINGERPRINT_BY_ID["MKREF09"] != MIKO_PRIMITIVE_FINGERPRINT_BY_ID["MKREF13"]
    assert f09 != f13


def test_f05_consent_and_boundary_firewall_is_hard_coded_as_data():
    directive = _identity("MKREF05").directive
    assert "shared-responsibility-must-already-exist" in directive
    assert "never-implies-consent-romantic-ownership-or-future-reproductive-choice" in directive


def test_f14_finite_care_window_preserves_exit_and_autonomy():
    directive = _identity("MKREF14").directive
    fallback = _identity("MKREF14").fallback
    assert "bounded-hazard-and-exit-state" in directive
    assert "never-hide-post-crisis-autonomy" in directive
    assert "exit-controls-remain-immediate" in fallback


def test_future_uncertainty_and_advisory_authority_never_become_truth_claims():
    f11 = _identity("MKREF11").directive
    f23 = _identity("MKREF23").directive
    assert "future-message-provenance" in f11
    assert "never-presents-uncertainty-as-certainty" in f11
    assert "multiple-advice-sources" in f23
    assert "keeps-final-decision-with-the-recorded-owner" in f23


def test_registration_adds_exactly_23_unique_references():
    registry = DNARegistry()
    register_m6_miko_references(registry)
    assert tuple(item.id for item in registry.list_units(UnitKind.REFERENCE)) == tuple(sorted(MIKO_REFERENCE_IDS))


def test_catalog_has_no_framework_core_provider_database_or_network_imports():
    source = inspect.getsource(miko_module)
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


def test_m6_catalog_has_no_runtime_per_reference_if_forest():
    source = inspect.getsource(miko_module)
    assert 'reference_id == "' not in source
