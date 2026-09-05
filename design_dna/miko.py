"""Design-DNA M6: Miko Personal Media reference corpus.

Wave F locks 23 independent owner-scoped references. Runtime IDs intentionally
use ``MKREFxx`` instead of the historical ``Fxx`` labels so the future M11
fixture corpus can retain its own F01-F14 namespace without registry collision.
Historical Wave-F IDs remain explicit metadata.

The surviving repository evidence is uneven. This module therefore records
whether a mechanism is directly locked in surviving raw governance, recoverable
from a surviving brief/candidate, or a bounded conservative translation. It
never upgrades title-level EQ3 into a false claim that unavailable row text was
recovered verbatim.

All reference identity remains structural and asset-off safe. Direct characters,
panels, covers, logos, source lettering, franchise palettes and copied source
composition are never required by M6.
"""
from __future__ import annotations

from typing import Dict, Mapping, Tuple

from design_dna.catalog import ALL_VIEWPORTS, MOBILE_VIEWPORT, WIDE_VIEWPORTS, mechanism, unit
from design_dna.models import Axis, DNAUnit, SemanticZone, UnitKind


MIKO_REFERENCE_IDS: Tuple[str, ...] = tuple(f"MKREF{i:02d}" for i in range(1, 24))
MIKO_HISTORICAL_ID_BY_ID: Mapping[str, str] = {
    runtime_id: f"F{index:02d}" for index, runtime_id in enumerate(MIKO_REFERENCE_IDS, 1)
}

MIKO_TITLE_BY_ID: Mapping[str, str] = {
    "MKREF01": "What's Wrong With Being the Villainess?",
    "MKREF02": "There Are No Bad Young Ladies in This World (Noble Lady Reformation Guide)",
    "MKREF03": "The Villainess I Possessed Is Raising Hell",
    "MKREF04": "The Father and the Daughter",
    "MKREF05": "Shut Up, Evil Dragon, I Don't Want to Raise a Child With You Anymore",
    "MKREF06": "She's Not Our Daughter!",
    "MKREF07": "Rojiura de Hirotta Onnanoko ga Bad End-go no Otome Game no Heroine Datta Ken",
    "MKREF08": "Reincarnated as a Villainous Duke to Be Condemned by My Daughter",
    "MKREF09": "My Sister Is the Main Character",
    "MKREF10": "My Daddy Hides His Power",
    "MKREF11": "Love Letter From The Future",
    "MKREF12": "I Will Raise the Villain Properly",
    "MKREF13": "I Need to Raise My Sister Properly",
    "MKREF14": "I Became The Tyrant's Dying Wife",
    "MKREF15": "I Became the Male Lead's Adopted Daughter",
    "MKREF16": "I Became a Patron of Villains",
    "MKREF17": "How Can You Pay Back The Kindness I Raised With Obsession?",
    "MKREF18": "Otome Game Sekai wa Mob ni Kibishii Sekai Desu",
    "MKREF19": "Get Out Of The Way, I'll Decide The Ending Now!",
    "MKREF20": "The Extra's Academy Survival Guide",
    "MKREF21": "Mob Shisai dakedo, Kono Sekai ga Otome Game dato Kizuita node Heroine o Ikusei Shimasu",
    "MKREF22": "50 Ways to Dump the Psychopathic Mastermind",
    "MKREF23": "A Princess Who Reads Fortune.",
}

MIKO_ALIASES_BY_ID: Mapping[str, Tuple[str, ...]] = {
    "MKREF01": ("The Perks of Being a Villainess",),
    "MKREF15": ("The Male Lead's Little Lion Daughter",),
    "MKREF18": ("Trapped in a Dating Sim",),
}

# Medium-family values are deliberately bounded. F05 is title-bounded manhua;
# the Japanese-source titles below are treated as manga. The remaining selected
# reference corpus is the strongly supported Manhwa/Webtoon family. No Miko
# Anime family is invented from adaptation existence.
MIKO_MEDIUM_BY_ID: Mapping[str, str] = {
    **{item: "MANHWA_WEBTOON" for item in MIKO_REFERENCE_IDS},
    "MKREF05": "MANHUA_TITLE_BOUNDED",
    "MKREF07": "MANGA",
    "MKREF08": "MANGA",
    "MKREF18": "MANGA",
    "MKREF21": "MANGA",
}

MIKO_ASSET_ON_APPLICABLE = frozenset(MIKO_REFERENCE_IDS)
MIKO_ASSET_ON_NOT_APPLICABLE = frozenset()

_PROV_LOCK = "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_WAVE_F_LOCK_CHECKPOINT_v1.md"
_PROV_V1_BRIEF = "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_WAVE_F_MIKO_FULL_EQUALIZATION_BRIEF_v1.md"
_PROV_V1_SURROGATE = (
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_WAVE_F_MIKO_CORPUS_EQUALIZATION_v1__MEMORY_RECONSTRUCTION.md"
)
_PROV_V2 = "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_WAVE_F_MIKO_RESIDUAL_EQUALIZATION_BRIEF_v2.md"
_PROV_V3 = "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_WAVE_F_MIKO_COLLISION_EVIDENCE_CLOSURE_BRIEF_v3.md"
_PROV_V4 = "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_WAVE_F_FINAL_THREE_SOURCE_FORENSICS_BRIEF_v4.md"
_PROV_BATCH5 = (
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_5_MIKO_v1__MEMORY_RECONSTRUCTION.md"
)
_PROVENANCE_BASE = f"{_PROV_LOCK};{_PROV_V1_BRIEF};{_PROV_BATCH5}"

_WORK_ZONES = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)
_ACTION_ZONES = (SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8)
_LAYOUT_ZONES = (SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)
_READING_ZONES = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U7, SemanticZone.U8)

# (mechanism label, primary axis, MK primitive fingerprint, evidence mode)
#
# LOCKED_RECOVERED: exact final distinction/mechanism is present in surviving raw lock.
# BRIEF_RECOVERED: named mechanism/candidate survives in a raw Wave-F brief, but the
# final row is not represented as verbatim recovery.
# BOUNDED_TRANSLATION: title membership/EQ3 survives but exact final mechanism row does
# not; runtime shape is a conservative translation over already-locked MK01-MK25.
_PROFILE: Mapping[str, Tuple[str, Axis, Tuple[str, ...], str]] = {
    "MKREF01": ("PROTECTIVE_REPUTATION_SHELL", Axis.INFORMATION, ("MK19", "MK02", "MK17"), "BOUNDED_TRANSLATION"),
    "MKREF02": ("TEMPORARY_EXPERT_AUTHORITY", Axis.INFORMATION, ("MK06", "MK20", "MK23"), "BRIEF_RECOVERED"),
    "MKREF03": ("HOST_WISH_CONTRACT_UNDER_BORROWED_IDENTITY", Axis.NARRATIVE_SEQUENCING, ("MK03", "MK01", "MK15", "MK16"), "LOCKED_RECOVERED"),
    "MKREF04": ("RELATIONAL_REPAIR_WITH_PARENTAL_AUTHORITY_REBALANCING", Axis.INTERACTION, ("MK04", "MK05", "MK24"), "BOUNDED_TRANSLATION"),
    "MKREF05": ("ADVERSARIAL_CO_PARENTING_UNDER_NON_OPTIONAL_SHARED_RESPONSIBILITY", Axis.INTERACTION, ("MK05", "MK17", "MK24", "MK15"), "LOCKED_RECOVERED"),
    "MKREF06": ("DISPUTED_BELONGING_INTERVAL", Axis.INFORMATION, ("MK09", "MK08", "MK17"), "BRIEF_RECOVERED"),
    "MKREF07": ("POST_FAILURE_RECOVERY_WINDOW", Axis.NARRATIVE_SEQUENCING, ("MK04", "MK01", "MK14"), "BRIEF_RECOVERED"),
    "MKREF08": ("PARENTAL_SELF_REFORM_CAUSING_OVERCORRECTION_IN_DEPENDENT_RELATION", Axis.INTERACTION, ("MK04", "MK05", "MK18", "MK24"), "BRIEF_RECOVERED"),
    "MKREF09": ("FATE_SUBSTITUTION_THROUGH_ROLE_ASSUMPTION", Axis.NARRATIVE_SEQUENCING, ("MK03", "MK20", "MK01", "MK18"), "LOCKED_RECOVERED"),
    "MKREF10": ("DEMOTED_POWER_RESERVOIR", Axis.INFORMATION, ("MK10", "MK11", "MK19"), "BOUNDED_TRANSLATION"),
    "MKREF11": ("DISCONTINUOUS_FUTURE_SIGNAL", Axis.NARRATIVE_SEQUENCING, ("MK18", "MK14", "MK23"), "BRIEF_RECOVERED"),
    "MKREF12": ("CARE_ACCUMULATION_WITH_TRAJECTORY_REPAIR", Axis.INTERACTION, ("MK05", "MK01", "MK07", "MK17"), "BOUNDED_TRANSLATION"),
    "MKREF13": ("SIBLING_TRAJECTORY_STEWARDSHIP_WITHOUT_ROLE_SUBSTITUTION", Axis.INTERACTION, ("MK21", "MK07", "MK01", "MK24"), "LOCKED_RECOVERED"),
    "MKREF14": ("DEADLINE_BOUNDED_MUTUAL_STABILIZATION_WITH_PLANNED_EXIT", Axis.NARRATIVE_SEQUENCING, ("MK14", "MK16", "MK24", "MK17"), "LOCKED_RECOVERED"),
    "MKREF15": ("BELONGING_ACCRETION", Axis.INFORMATION, ("MK08", "MK05", "MK17"), "BOUNDED_TRANSLATION"),
    "MKREF16": ("PATRONAGE_THROUGH_INDIRECT_CAPABILITY_DELEGATION", Axis.INFORMATION, ("MK22", "MK06", "MK02"), "BOUNDED_TRANSLATION"),
    "MKREF17": ("REPUTATION_TO_TRUST_ACCRETION_WITH_EXIT_BOUNDARY", Axis.INTERACTION, ("MK19", "MK17", "MK24", "MK16"), "BRIEF_RECOVERED"),
    "MKREF18": ("PERIPHERAL_SYSTEM_LEVERAGE", Axis.INFORMATION, ("MK02", "MK25", "MK03"), "BOUNDED_TRANSLATION"),
    "MKREF19": ("ENDING_AUTHORSHIP_SEIZURE_FROM_A_SUPPORT_ROLE", Axis.NARRATIVE_SEQUENCING, ("MK15", "MK02", "MK03", "MK01"), "BRIEF_RECOVERED"),
    "MKREF20": ("PERIPHERAL_SURVIVAL_LOOP", Axis.INFORMATION, ("MK12", "MK25", "MK13"), "BOUNDED_TRANSLATION"),
    "MKREF21": ("PROACTIVE_TRAJECTORY_GUIDANCE_WITHOUT_OUTCOME_CAPTURE", Axis.INTERACTION, ("MK07", "MK01", "MK25", "MK15"), "BOUNDED_TRANSLATION"),
    "MKREF22": ("ITERATED_EXIT_STRATEGY_UNDER_ASYMMETRIC_COERCION", Axis.INTERACTION, ("MK16", "MK24", "MK13", "MK17"), "BRIEF_RECOVERED"),
    "MKREF23": ("MULTI_SOURCE_ADVISORY_NETWORK_UNDER_OWNER_AGENCY", Axis.INFORMATION, ("MK23", "MK15", "MK02", "MK18"), "BRIEF_RECOVERED"),
}

MIKO_MECHANISM_BY_ID: Mapping[str, str] = {item: value[0] for item, value in _PROFILE.items()}
MIKO_PRIMITIVE_FINGERPRINT_BY_ID: Mapping[str, Tuple[str, ...]] = {item: value[2] for item, value in _PROFILE.items()}
MIKO_EVIDENCE_MODE_BY_ID: Mapping[str, str] = {item: value[3] for item, value in _PROFILE.items()}

_EXTRA_PROVENANCE_BY_ID: Mapping[str, Tuple[str, ...]] = {
    "MKREF01": (_PROV_V1_SURROGATE,),
    "MKREF02": (_PROV_V3,),
    "MKREF03": (_PROV_V4,),
    "MKREF05": (_PROV_V4,),
    "MKREF06": (_PROV_V2, _PROV_V3),
    "MKREF07": (_PROV_V3,),
    "MKREF08": (_PROV_V3,),
    "MKREF09": (_PROV_V3,),
    "MKREF10": (_PROV_V1_SURROGATE,),
    "MKREF11": (_PROV_V2, _PROV_V3),
    "MKREF13": (_PROV_V3,),
    "MKREF14": (_PROV_V4,),
    "MKREF15": (_PROV_V1_SURROGATE,),
    "MKREF17": (_PROV_V3,),
    "MKREF18": (_PROV_V1_SURROGATE,),
    "MKREF19": (_PROV_V3,),
    "MKREF20": (_PROV_V1_SURROGATE,),
    "MKREF22": (_PROV_V2, _PROV_V3),
    "MKREF23": (_PROV_V3,),
}

# Truth guards are declarative data, never resolver branches. They restrict when
# a source mechanism may describe existing application semantics and prevent the
# reference from fabricating relationship, authority, care, timeline or outcome.
_SEMANTIC_GUARD_BY_ID: Mapping[str, str] = {
    "MKREF02": "temporary-authority-requires-an-existing-bounded-advisory-or-expert-role-and-never-creates-permission",
    "MKREF03": "host-wish-contract-requires-distinct-existing-goal-owner-and-executor-role-state-and-never-invents-an-obligation",
    "MKREF04": "parental-authority-repair-may-project-only-from-existing-care-or-authority-relations-and-never-invents-kinship",
    "MKREF05": "shared-responsibility-must-already-exist-and-never-implies-consent-romantic-ownership-or-future-reproductive-choice",
    "MKREF06": "contested-belonging-must-remain-unresolved-when-source-state-is-unresolved-and-never-fabricates-family-membership",
    "MKREF08": "self-reform-and-dependent-relation-must-both-exist-in-semantic-state-and-never-infers-parenthood-or-reconciliation",
    "MKREF09": "role-substitution-requires-an-actual-structural-burden-transfer-and-never-merely-renames-guidance-as-substitution",
    "MKREF11": "future-signal-requires-explicit-forecast-or-future-message-provenance-and-never-presents-uncertainty-as-certainty",
    "MKREF12": "care-and-trajectory-repair-require-existing-events-and-target-state-and-never-fabricate-affection-or-dependency",
    "MKREF13": "sibling-stewardship-requires-existing-sibling-or-equivalent-explicit-relation-and-must-not-transfer-target-role-ownership",
    "MKREF14": "deadline-and-planned-exit-require-existing-bounded-hazard-and-exit-state-and-never-hide-post-crisis-autonomy",
    "MKREF16": "patronage-requires-existing-resource-or-capability-delegation-authority-and-never-creates-resource-control",
    "MKREF17": "trust-accretion-requires-existing-history-and-exit-boundary-and-never-fabricates-trust-reconciliation-or-consent",
    "MKREF19": "ending-authorship-requires-existing-decision-authority-and-never-overrides-user-or-domain-outcome-ownership",
    "MKREF21": "guidance-may-change-only-existing-option-presentation-and-never-captures-target-decision-or-ending-authority",
    "MKREF22": "exit-strategy-requires-existing-exit-intent-constraint-and-boundary-state-and-never-hides-or-delays-an-available-exit",
    "MKREF23": "advisory-network-requires-existing-multiple-advice-sources-and-keeps-final-decision-with-the-recorded-owner",
}


def _slug(value: str) -> str:
    return "-".join("".join(ch.lower() if ch.isalnum() else " " for ch in value).split())


def _zones(axis: Axis) -> Tuple[SemanticZone, ...]:
    if axis is Axis.INTERACTION:
        return _ACTION_ZONES
    if axis is Axis.NARRATIVE_SEQUENCING:
        return _READING_ZONES
    if axis in (Axis.SPACE, Axis.FORM, Axis.MATERIAL_CONSTRUCTION, Axis.SCALE_GRANULARITY, Axis.ATMOSPHERE_ENVIRONMENT):
        return _LAYOUT_ZONES
    return _WORK_ZONES


def _provenance(reference_id: str) -> str:
    extras = _EXTRA_PROVENANCE_BY_ID.get(reference_id, ())
    return ";".join((_PROVENANCE_BASE, *extras))


def _identity_directive(reference_id: str, mechanism_label: str, evidence_mode: str) -> str:
    title = MIKO_TITLE_BY_ID[reference_id]
    historical_id = MIKO_HISTORICAL_ID_BY_ID[reference_id]
    fingerprint = ",".join(MIKO_PRIMITIVE_FINGERPRINT_BY_ID[reference_id])
    parts = [
        f"project-{_slug(mechanism_label)}-as-miko-owner-scoped-reference-{historical_id.lower()}-{_slug(title)}-using-only-existing-semantic-content",
        f"primitive-fingerprint={fingerprint}",
        f"evidence-mode={evidence_mode}",
        "reference-shapes-presentation-only-never-domain-state-actions-permissions-provider-behavior-or-user-data",
        "never-fabricate-kinship-care-affection-trust-consent-capability-authority-history-timeline-resource-control-forecast-certainty-or-outcome-ownership",
        "never-require-or-reproduce-characters-panels-covers-logos-source-lettering-franchise-palette-or-copied-source-composition",
    ]
    guard = _SEMANTIC_GUARD_BY_ID.get(reference_id)
    if guard:
        parts.append(guard)
    return ";".join(parts)


def _fallback_directive(reference_id: str) -> str:
    label = _slug(MIKO_MECHANISM_BY_ID[reference_id])
    return (
        f"asset-off-low-intensity-{label}-using-ordinary-grouping-hierarchy-boundaries-and-existing-state-labels;"
        "all-required-information-actions-state-reading-boundaries-and-exit-controls-remain-immediate-legible-and-conventional"
    )


def _make_reference(reference_id: str) -> DNAUnit:
    mechanism_label, axis, _fingerprint, evidence_mode = _PROFILE[reference_id]
    title = MIKO_TITLE_BY_ID[reference_id]
    medium = MIKO_MEDIUM_BY_ID[reference_id]
    primary = mechanism(
        reference_id,
        "identity",
        axis,
        _identity_directive(reference_id, mechanism_label, evidence_mode),
        zones=_zones(axis),
        fallback=_fallback_directive(reference_id),
        rank=87,
        viewports=ALL_VIEWPORTS,
        accessibility_safe=True,
        reading_safe=True,
    )
    wide = mechanism(
        reference_id,
        "wide-adaptation",
        Axis.ADAPTATION,
        f"wide-view-may-expand-{_slug(mechanism_label)}-without-changing-recorded-role-authority-boundary-history-or-outcome-ownership",
        zones=_LAYOUT_ZONES,
        fallback="ordinary-wide-semantic-layout",
        rank=72,
        viewports=WIDE_VIEWPORTS,
    )
    mobile = mechanism(
        reference_id,
        "mobile-adaptation",
        Axis.ADAPTATION,
        f"mobile-recomposes-{_slug(mechanism_label)}-into-ordered-flow-without-desktop-shrink-scroll-trap-hidden-state-or-hidden-exit",
        zones=_LAYOUT_ZONES,
        fallback="ordinary-mobile-semantic-flow",
        rank=78,
        viewports=MOBILE_VIEWPORT,
    )
    return unit(
        reference_id,
        kind=UnitKind.REFERENCE,
        family=f"MIKO_PERSONAL_MEDIA_{medium}",
        lineage=f"miko-personal-media-{medium.lower()}-{_slug(title)}",
        mechanisms=(primary, wide, mobile),
        provenance=_provenance(reference_id),
        identity_survival=f"asset-off-structural-{_slug(mechanism_label)}",
    )


MIKO_REFERENCES: Tuple[DNAUnit, ...] = tuple(_make_reference(item) for item in MIKO_REFERENCE_IDS)
MIKO_REFERENCE_BY_ID: Dict[str, DNAUnit] = {item.id: item for item in MIKO_REFERENCES}


def miko_reference_asset_on_applicable(reference_id: str) -> bool:
    if reference_id not in MIKO_REFERENCE_BY_ID:
        raise KeyError(reference_id)
    return True


def register_m6_miko_references(registry) -> None:
    for reference in MIKO_REFERENCES:
        registry.register(reference)
