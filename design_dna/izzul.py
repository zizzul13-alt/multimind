"""Design-DNA M5: Izzul Personal Media reference corpus.

The 36-member corpus and medium partition are locked. The original final
row-by-row Batch-4 prose does not survive verbatim in the repository, so this
module distinguishes recovered locks from conservative implementation
translations instead of pretending to reconstruct unavailable wording.

Runtime references are structural and asset-off safe. Direct-IP media may be
eligible enrichment in a later asset batch, but no character, panel, logo,
franchise palette, costume, source lettering or copied composition is required
for identity here.
"""
from __future__ import annotations

from typing import Dict, Mapping, Tuple

from design_dna.catalog import ALL_VIEWPORTS, MOBILE_VIEWPORT, WIDE_VIEWPORTS, mechanism, unit
from design_dna.models import Axis, DNAUnit, SemanticZone, UnitKind


IZZUL_ANIME_IDS: Tuple[str, ...] = tuple(f"IZA{i:02d}" for i in range(1, 16))
IZZUL_MANGA_IDS: Tuple[str, ...] = tuple(f"IZM{i:02d}" for i in range(1, 12))
IZZUL_WEBTOON_IDS: Tuple[str, ...] = tuple(f"IZW{i:02d}" for i in range(1, 11))
IZZUL_REFERENCE_IDS: Tuple[str, ...] = IZZUL_ANIME_IDS + IZZUL_MANGA_IDS + IZZUL_WEBTOON_IDS

IZZUL_TITLE_BY_ID: Mapping[str, str] = {
    "IZA01": "Chainsaw Man",
    "IZA02": "The Tatami Galaxy",
    "IZA03": "Samurai Champloo",
    "IZA04": "Mushishi",
    "IZA05": "Psycho-Pass",
    "IZA06": "Mononoke",
    "IZA07": "Serial Experiments Lain",
    "IZA08": "Ping Pong the Animation",
    "IZA09": "Land of the Lustrous",
    "IZA10": "Mob Psycho 100",
    "IZA11": "Cowboy Bebop",
    "IZA12": "Neon Genesis Evangelion",
    "IZA13": "Violet Evergarden",
    "IZA14": "Ghost in the Shell",
    "IZA15": "Made in Abyss",
    "IZM01": "Fire Punch",
    "IZM02": "BLAME!",
    "IZM03": "Berserk",
    "IZM04": "AKIRA",
    "IZM05": "Vagabond",
    "IZM06": "Witch Hat Atelier",
    "IZM07": "Dorohedoro",
    "IZM08": "Girls' Last Tour",
    "IZM09": "Oyasumi Punpun",
    "IZM10": "JoJo's Bizarre Adventure",
    "IZM11": "Nausicaä of the Valley of the Wind",
    "IZW01": "Tyrant of the Tower Defense Game",
    "IZW02": "Tower of God",
    "IZW03": "Omniscient Reader's Viewpoint",
    "IZW04": "Solo Leveling",
    "IZW05": "The Horizon",
    "IZW06": "The Boxer",
    "IZW07": "Bastard",
    "IZW08": "The Legend of the Northern Blade",
    "IZW09": "Her Summon",
    "IZW10": "The Greatest Estate Developer",
}

IZZUL_MEDIUM_BY_ID: Mapping[str, str] = {
    **{item: "ANIME" for item in IZZUL_ANIME_IDS},
    **{item: "MANGA" for item in IZZUL_MANGA_IDS},
    **{item: "MANHWA_WEBTOON" for item in IZZUL_WEBTOON_IDS},
}

# Historical/source alias is metadata only; it is not a second corpus member.
IZZUL_ALIASES_BY_ID: Mapping[str, Tuple[str, ...]] = {
    "IZW01": ("I Became the Tyrant of a Defense Game",),
}

# Every Izzul title is asset-applicable in the global ledger, but M5 ships no
# actual source assets and requires none for FULL structural identity.
IZZUL_ASSET_ON_APPLICABLE = frozenset(IZZUL_REFERENCE_IDS)
IZZUL_ASSET_ON_NOT_APPLICABLE = frozenset()

_PROV_LOCK = "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_WAVE_E_LOCK_CHECKPOINT_v1.md"
_PROV_B7 = (
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_B7_IZZUL_CORPUS_v1__MEMORY_RECONSTRUCTION.md"
)
_PROV_BATCH4 = (
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_4_IZZUL_v1__MEMORY_RECONSTRUCTION.md"
)
_PROV_V3 = (
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_WAVE_E_IZZUL_CORPUS_EQUALIZATION_v3__MEMORY_RECONSTRUCTION.md"
)
_PROV_V5 = "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_WAVE_E_RESIDUAL_CLOSURE_v5.md"
_PROV_V6 = (
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_WAVE_E_HER_SUMMON_DEEP_CLOSURE_v6__MEMORY_RECONSTRUCTION.md"
)
_PROVENANCE_BASE = f"{_PROV_LOCK};{_PROV_B7};{_PROV_BATCH4}"

_WORK_ZONES = (
    SemanticZone.U2,
    SemanticZone.U3,
    SemanticZone.U4,
    SemanticZone.U8,
)
_ACTION_ZONES = (
    SemanticZone.U3,
    SemanticZone.U4,
    SemanticZone.U5,
    SemanticZone.U6,
    SemanticZone.U8,
)
_LAYOUT_ZONES = (
    SemanticZone.U1,
    SemanticZone.U2,
    SemanticZone.U3,
    SemanticZone.U4,
    SemanticZone.U8,
)
_READING_ZONES = (
    SemanticZone.U2,
    SemanticZone.U3,
    SemanticZone.U4,
    SemanticZone.U7,
    SemanticZone.U8,
)

# (mechanism label, primary axis, primitive fingerprint, evidence mode)
#
# LOCKED_RECOVERED means the mechanism/fingerprint is directly recoverable from
# surviving Wave-E/B7/Batch-4 material. CONSERVATIVE_TRANSLATION means the title
# identity and mechanism lineage survive but the exact final historical row is
# unavailable; the fingerprint is an implementation-bounded composition of the
# already-locked P01-P25 ontology and is not represented as verbatim history.
_PROFILE: Mapping[str, Tuple[str, Axis, Tuple[str, ...], str]] = {
    "IZA01": ("ABRUPT_REGISTER_PUNCTUATION", Axis.NARRATIVE_SEQUENCING, ("P01", "P08", "P13"), "CONSERVATIVE_TRANSLATION"),
    "IZA02": ("DENSE_RECURSIVE_BRANCHING_FLOW", Axis.NARRATIVE_SEQUENCING, ("P03", "P04", "P06", "P08"), "CONSERVATIVE_TRANSLATION"),
    "IZA03": ("RHYTHMIC_CULTURAL_REGISTER_SPLICE", Axis.SOUND_RHYTHM, ("P25", "P08", "P13"), "CONSERVATIVE_TRANSLATION"),
    "IZA04": ("QUIET_THRESHOLD_PROGRESSIVE_REVEAL", Axis.NARRATIVE_SEQUENCING, ("P02", "P04", "P16"), "LOCKED_RECOVERED"),
    "IZA05": ("INSTITUTIONAL_SYSTEM_STATE_MEDIATION", Axis.INFORMATION, ("P05", "P17", "P23"), "LOCKED_RECOVERED"),
    "IZA06": ("ORNAMENT_AS_PLANAR_SPATIAL_PARTITION", Axis.FORM, ("P11", "P19"), "LOCKED_RECOVERED"),
    "IZA07": ("MEDIATED_PRESENCE_NETWORK_AMBIGUITY", Axis.INFORMATION, ("P05", "P06", "P17"), "LOCKED_RECOVERED"),
    "IZA08": ("MOTION_INDUCED_DEFORMATION", Axis.MOTION_TEMPORAL, ("P09", "P10"), "LOCKED_RECOVERED"),
    "IZA09": ("REFRACTIVE_FRAGMENTATION_STATE", Axis.FORM, ("P20", "P09"), "LOCKED_RECOVERED"),
    "IZA10": ("EXPRESSIVE_DEFORMATION_SCALE_RELEASE", Axis.FORM, ("P09", "P01"), "CONSERVATIVE_TRANSLATION"),
    "IZA11": ("EPISODIC_RHYTHMIC_REGISTER_SHIFT", Axis.NARRATIVE_SEQUENCING, ("P13", "P25", "P08"), "CONSERVATIVE_TRANSLATION"),
    "IZA12": ("OPERATIONAL_TYPOGRAPHY_SYSTEM_HIERARCHY", Axis.TYPOGRAPHY_SCRIPT, ("P05", "P13", "P17"), "LOCKED_RECOVERED"),
    "IZA13": ("CORRESPONDENCE_DOCUMENT_MATERIALITY", Axis.MATERIAL_CONSTRUCTION, ("P24", "P12"), "LOCKED_RECOVERED"),
    "IZA14": ("EMBODIED_SYSTEM_NETWORK_BOUNDARY", Axis.INFORMATION, ("P17", "P23", "P05"), "LOCKED_RECOVERED"),
    "IZA15": ("LAYERED_DEPTH_IRREVERSIBLE_TRAVERSAL", Axis.SPACE, ("P06", "P07", "P16"), "LOCKED_RECOVERED"),
    "IZM01": ("STATIC_FRAME_TEMPORAL_TRACE_ABRUPT_CONTRAST", Axis.NARRATIVE_SEQUENCING, ("P08", "P15"), "LOCKED_RECOVERED"),
    "IZM02": ("INFRASTRUCTURE_SCALE_TOPOLOGICAL_TRAVERSAL", Axis.SPACE, ("P06", "P23", "P07"), "CONSERVATIVE_TRANSLATION"),
    "IZM03": ("MONUMENTAL_SCALE_DETAIL_FOCUS", Axis.SCALE_GRANULARITY, ("P01", "P18"), "CONSERVATIVE_TRANSLATION"),
    "IZM04": ("DIRECTIONAL_FORCE_INFRASTRUCTURE_SCALE", Axis.FORM, ("P10", "P01", "P23"), "CONSERVATIVE_TRANSLATION"),
    "IZM05": ("NEGATIVE_SPACE_CROPPED_FOCUS", Axis.SPACE, ("P02", "P19"), "CONSERVATIVE_TRANSLATION"),
    "IZM06": ("ORNAMENT_CONSTRUCTION_REVEAL", Axis.FORM, ("P11", "P12"), "LOCKED_RECOVERED"),
    "IZM07": ("LAYERED_WORLD_MATERIAL_REGISTER", Axis.MATERIAL_CONSTRUCTION, ("P07", "P12"), "CONSERVATIVE_TRANSLATION"),
    "IZM08": ("QUIET_INFRASTRUCTURE_ENVIRONMENTAL_INTERVAL", Axis.SPACE, ("P02", "P16", "P23"), "CONSERVATIVE_TRANSLATION"),
    "IZM09": ("REPRESENTATIONAL_MISMATCH_NEGATIVE_SPACE", Axis.FORM, ("P15", "P02"), "CONSERVATIVE_TRANSLATION"),
    "IZM10": ("DIRECTIONAL_SCALE_CROPPING_COMPOSITION", Axis.FORM, ("P10", "P01", "P19"), "CONSERVATIVE_TRANSLATION"),
    "IZM11": ("ECOLOGICAL_LAYERED_WORLD_CAUSALITY", Axis.ATMOSPHERE_ENVIRONMENT, ("P07", "P16", "P23"), "CONSERVATIVE_TRANSLATION"),
    "IZW01": ("STRATEGIC_CONTEXT_INTERVALIZATION", Axis.INFORMATION, ("P02", "P13", "P05", "P17"), "LOCKED_RECOVERED"),
    "IZW02": ("LAYERED_RULED_VERTICAL_TRAVERSAL", Axis.SPACE, ("P07", "P06", "P01"), "CONSERVATIVE_TRANSLATION"),
    "IZW03": ("SYSTEM_WORLD_DUAL_LAYER_STATE_OVERLAY", Axis.INFORMATION, ("P05", "P07", "P17"), "LOCKED_RECOVERED"),
    "IZW04": ("SCALE_PUNCTUATED_PROGRESSIVE_SYSTEM_REVEAL", Axis.SCALE_GRANULARITY, ("P01", "P04", "P05"), "LOCKED_RECOVERED"),
    "IZW05": ("CONTRASTIVE_NEGATIVE_SPACE_TONAL_DENSITY_PACING", Axis.SPACE, ("P02", "P03"), "LOCKED_RECOVERED"),
    "IZW06": ("SCROLL_REVEAL_GEOMETRY_BOUNDED_SEQUENTIAL_IMPACT", Axis.NARRATIVE_SEQUENCING, ("P04", "P08", "P21"), "LOCKED_RECOVERED"),
    "IZW07": ("CONFRONTATION_REVEAL_NEGATIVE_SPACE", Axis.NARRATIVE_SEQUENCING, ("P04", "P21", "P02"), "CONSERVATIVE_TRANSLATION"),
    "IZW08": ("SPATIALLY_TRACEABLE_FORCE_PATH_CHOREOGRAPHY", Axis.FORM, ("P10", "P19"), "LOCKED_RECOVERED"),
    "IZW09": ("DIFFERENTIAL_TEXTURE_FIGURE_GROUND_STAGING", Axis.SCALE_GRANULARITY, ("P18", "P03", "P02", "P16"), "LOCKED_RECOVERED"),
    "IZW10": ("TECHNICAL_CONTEXT_EXAGGERATED_REACTION_REGISTER_SWITCH", Axis.NARRATIVE_SEQUENCING, ("P15", "P13", "P05"), "LOCKED_RECOVERED"),
}

IZZUL_MECHANISM_BY_ID: Mapping[str, str] = {item: value[0] for item, value in _PROFILE.items()}
IZZUL_PRIMITIVE_FINGERPRINT_BY_ID: Mapping[str, Tuple[str, ...]] = {item: value[2] for item, value in _PROFILE.items()}
IZZUL_EVIDENCE_MODE_BY_ID: Mapping[str, str] = {item: value[3] for item, value in _PROFILE.items()}

# Declarative exception metadata keeps the family free of runtime per-reference
# branch logic while preserving the hard source-specific locks.
_EXTRA_PROVENANCE_BY_ID: Mapping[str, Tuple[str, ...]] = {
    "IZM01": (_PROV_V3,),
    "IZW01": (_PROV_V5,),
    "IZW05": (_PROV_V3,),
    "IZW06": (_PROV_V3,),
    "IZW08": (_PROV_V3,),
    "IZW09": (_PROV_V6,),
    "IZW10": (_PROV_V3,),
}
_EXTRA_GUARD_BY_ID: Mapping[str, str] = {
    "IZW01": (
        "strategic-context-must-correspond-to-real-existing-planning-or-context-information-"
        "never-fictional-game-state"
    ),
    "IZW09": (
        "P16-environmental-causality-is-conditional-and-may-activate-only-when-real-context-"
        "is-causal-or-informative"
    ),
}


def _slug(value: str) -> str:
    return "-".join("".join(ch.lower() if ch.isalnum() else " " for ch in value).split())


def _zones(axis: Axis) -> Tuple[SemanticZone, ...]:
    if axis in (Axis.SPACE, Axis.FORM, Axis.MATERIAL_CONSTRUCTION, Axis.SCALE_GRANULARITY, Axis.ATMOSPHERE_ENVIRONMENT):
        return _LAYOUT_ZONES
    if axis in (Axis.INFORMATION, Axis.INTERACTION):
        return _ACTION_ZONES
    if axis in (Axis.TYPOGRAPHY_SCRIPT, Axis.NARRATIVE_SEQUENCING, Axis.MOTION_TEMPORAL, Axis.SOUND_RHYTHM):
        return _READING_ZONES
    return _WORK_ZONES


def _provenance(reference_id: str) -> str:
    extras = _EXTRA_PROVENANCE_BY_ID.get(reference_id, ())
    return ";".join((_PROVENANCE_BASE, *extras))


def _identity_directive(reference_id: str, mechanism_label: str, evidence_mode: str) -> str:
    title = IZZUL_TITLE_BY_ID[reference_id]
    fingerprint = ",".join(IZZUL_PRIMITIVE_FINGERPRINT_BY_ID[reference_id])
    parts = [
        f"project-{_slug(mechanism_label)}-as-the-{_slug(title)}-reference-identity-using-only-existing-semantic-content",
        f"primitive-fingerprint={fingerprint}",
        f"evidence-mode={evidence_mode}",
        "reference-shapes-presentation-only-never-domain-state-actions-permissions-provider-behavior-or-user-data",
        "never-require-or-reproduce-characters-panels-logos-source-lettering-costumes-franchise-palette-or-copied-composition",
    ]
    guard = _EXTRA_GUARD_BY_ID.get(reference_id)
    if guard:
        parts.append(guard)
    return ";".join(parts)


def _fallback_directive(reference_id: str) -> str:
    label = _slug(IZZUL_MECHANISM_BY_ID[reference_id])
    return (
        f"asset-off-low-intensity-{label}-using-ordinary-spacing-grouping-hierarchy-and-semantic-boundaries;"
        "all-required-information-actions-state-and-reading-remain-immediate-legible-and-conventional"
    )


def _make_reference(reference_id: str) -> DNAUnit:
    mechanism_label, axis, _fingerprint, evidence_mode = _PROFILE[reference_id]
    title = IZZUL_TITLE_BY_ID[reference_id]
    medium = IZZUL_MEDIUM_BY_ID[reference_id]
    primary = mechanism(
        reference_id,
        "identity",
        axis,
        _identity_directive(reference_id, mechanism_label, evidence_mode),
        zones=_zones(axis),
        fallback=_fallback_directive(reference_id),
        rank=86,
        viewports=ALL_VIEWPORTS,
        accessibility_safe=True,
        reading_safe=axis not in (Axis.MOTION_TEMPORAL,),
    )
    wide = mechanism(
        reference_id,
        "wide-adaptation",
        Axis.ADAPTATION,
        f"wide-view-may-expand-{_slug(mechanism_label)}-without-changing-semantic-order-state-or-actions",
        zones=_LAYOUT_ZONES,
        fallback="ordinary-wide-semantic-layout",
        rank=72,
        viewports=WIDE_VIEWPORTS,
    )
    mobile = mechanism(
        reference_id,
        "mobile-adaptation",
        Axis.ADAPTATION,
        f"mobile-recomposes-{_slug(mechanism_label)}-into-ordered-flow-without-desktop-shrink-scroll-trap-or-hidden-state",
        zones=_LAYOUT_ZONES,
        fallback="ordinary-mobile-semantic-flow",
        rank=78,
        viewports=MOBILE_VIEWPORT,
    )
    return unit(
        reference_id,
        kind=UnitKind.REFERENCE,
        family=f"IZZUL_PERSONAL_MEDIA_{medium}",
        lineage=f"izzul-personal-media-{medium.lower()}-{_slug(title)}",
        mechanisms=(primary, wide, mobile),
        provenance=_provenance(reference_id),
        identity_survival=f"asset-off-structural-{_slug(mechanism_label)}",
    )


IZZUL_REFERENCES: Tuple[DNAUnit, ...] = tuple(_make_reference(item) for item in IZZUL_REFERENCE_IDS)
IZZUL_REFERENCE_BY_ID: Dict[str, DNAUnit] = {item.id: item for item in IZZUL_REFERENCES}


def izzul_reference_asset_on_applicable(reference_id: str) -> bool:
    if reference_id not in IZZUL_REFERENCE_BY_ID:
        raise KeyError(reference_id)
    return True


def register_m5_izzul_references(registry) -> None:
    for reference in IZZUL_REFERENCES:
        registry.register(reference)
