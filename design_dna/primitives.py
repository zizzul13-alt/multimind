"""Design-DNA M4: canonical 68 additive primitives.

M4 is deliberately data-oriented. Atomic primitives transform presentation of
already-existing semantic state; they never create domain state, story truth,
relationships, cultural claims, permissions, provider timing, or hidden wait time.
"""
from __future__ import annotations

from typing import Dict, Tuple

from design_dna.catalog import mechanism, unit
from design_dna.models import Axis, DNAUnit, SemanticZone, UnitKind

IZZUL_PRIMITIVE_IDS = tuple(f"P{i:02d}" for i in range(1, 26))
MIKO_PRIMITIVE_IDS = tuple(f"MK{i:02d}" for i in range(1, 26))
TEMPORAL_PRIMITIVE_IDS = tuple(f"TP{i:02d}" for i in range(1, 19))
TEMPORAL_HISTORICAL_NON_ADDITIVE = ("TP19", "TP20")
M4_PRIMITIVE_IDS = IZZUL_PRIMITIVE_IDS + MIKO_PRIMITIVE_IDS + TEMPORAL_PRIMITIVE_IDS

IZZUL_PRIMITIVE_NAMES: Dict[str, str] = {
    "P01": "SCALE_PUNCTUATION", "P02": "NEGATIVE_SPACE_PACING", "P03": "DENSITY_MODULATION",
    "P04": "PROGRESSIVE_REVEAL", "P05": "STATE_OVERLAY", "P06": "TOPOLOGICAL_TRAVERSAL",
    "P07": "LAYERED_WORLD_RULES", "P08": "TEMPORAL_PUNCTUATION", "P09": "STATE_LINKED_DEFORMATION",
    "P10": "DIRECTIONAL_FORCE_FORM", "P11": "ORNAMENT_AS_STRUCTURE", "P12": "MATERIAL_LAYER_REVEAL",
    "P13": "EDITORIAL_SEGMENT_PUNCTUATION", "P14": "RELATIONAL_ANCHOR", "P15": "REPRESENTATIONAL_MISMATCH",
    "P16": "ENVIRONMENTAL_CAUSALITY", "P17": "SYSTEM_WORLD_DUAL_LAYER", "P18": "DETAIL_DENSITY_FOCUS",
    "P19": "CROPPING_AS_COMPOSITION", "P20": "REFRACTIVE_FRAGMENTATION", "P21": "CONFRONTATION_TIME_DILATION",
    "P22": "RULE_CHANGING_STAGE", "P23": "INFRASTRUCTURE_AS_SYSTEM", "P24": "CORRESPONDENCE_AS_OBJECT",
    "P25": "RHYTHMIC_CULTURAL_SPLICE",
}
MIKO_PRIMITIVE_NAMES: Dict[str, str] = {
    "MK01": "TRAJECTORY_INTERVENTION", "MK02": "PERIPHERAL_AGENCY", "MK03": "ROLE_REFRAMING",
    "MK04": "POST_CANON_REPAIR", "MK05": "CARE_ACCUMULATION", "MK06": "CAPABILITY_TRANSFER",
    "MK07": "PREVENTIVE_GUIDANCE", "MK08": "CHOSEN_KINSHIP", "MK09": "CONTESTED_BELONGING",
    "MK10": "LATENT_CAPABILITY", "MK11": "CARE_FIRST_HIERARCHY", "MK12": "LOW_PROFILE_SURVIVAL",
    "MK13": "RESOURCE_CONSTRAINED_PLANNING", "MK14": "TIMELINE_DRIFT", "MK15": "ENDING_AUTHORITY",
    "MK16": "EXIT_STRATEGY_SET", "MK17": "RELATIONAL_PERSISTENCE", "MK18": "FUTURE_JUDGMENT_FEEDBACK",
    "MK19": "SOCIAL_PERCEPTION_GAP", "MK20": "VOLUNTARY_ROLE_EXPANSION", "MK21": "SIBLING_GUARDIANSHIP",
    "MK22": "PATRONAGE_INDIRECT_AGENCY", "MK23": "UNCERTAINTY_INTERPRETATION", "MK24": "BOUNDARY_SETTING_IN_CARE",
    "MK25": "SYSTEM_LITERACY_FROM_LOW_STATUS",
}
TEMPORAL_PRIMITIVE_NAMES: Dict[str, str] = {
    "TP01": "PERIODICITY", "TP02": "STRUCTURAL_BOUNDARY", "TP03": "INTENSITY_ENVELOPE",
    "TP04": "RESOLUTION", "TP05": "RECURRENCE_WITH_VARIATION", "TP06": "RETURN_RECALL",
    "TP07": "CALL_RESPONSE_HANDOFF", "TP08": "EXPECTATION_DISPLACEMENT", "TP09": "INTERRUPTION",
    "TP10": "NEGATIVE_INTERVAL_RESERVED_GAP", "TP11": "RATE_CHANGE", "TP12": "DENSITY_EVOLUTION",
    "TP13": "LAYER_ENTRY_EXIT", "TP14": "PARALLEL_TEMPORAL_VOICES", "TP15": "ANTICIPATION",
    "TP16": "IRREVERSIBLE_PROGRESSION", "TP17": "TERMINAL_RESOLUTION_AFTERBODY", "TP18": "TEMPORAL_PUNCTUATION",
}
PRIMITIVE_NAMES: Dict[str, str] = {**IZZUL_PRIMITIVE_NAMES, **MIKO_PRIMITIVE_NAMES, **TEMPORAL_PRIMITIVE_NAMES}

_PROV_P = (
    "docs/design-dna/corpora/CORPUS_INDEX.md;"
    "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_4_LOCK_CHECKPOINT_v1.md;"
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_4_IZZUL_v1__MEMORY_RECONSTRUCTION.md"
)
_PROV_MK = (
    "docs/design-dna/corpora/CORPUS_INDEX.md;"
    "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_5_LOCK_CHECKPOINT_v1.md"
)
_PROV_TP = (
    "docs/design-dna/corpora/CORPUS_INDEX.md;"
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_TRACK_T_I_16_EQ3_FULL_EQUALIZATION_v2__MEMORY_RECONSTRUCTION.md"
)

_WORK_ZONES = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U6, SemanticZone.U8)
_LAYOUT_ZONES = (SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)
_ACTION_ZONES = (SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8)
_TEMPORAL_ZONES = (SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)

_P_AXIS: Dict[str, Axis] = {
    "P01": Axis.SCALE_GRANULARITY, "P02": Axis.SPACE, "P03": Axis.INFORMATION,
    "P04": Axis.NARRATIVE_SEQUENCING, "P05": Axis.INFORMATION, "P06": Axis.NARRATIVE_SEQUENCING,
    "P07": Axis.INFORMATION, "P08": Axis.MOTION_TEMPORAL, "P09": Axis.FORM, "P10": Axis.FORM,
    "P11": Axis.FORM, "P12": Axis.MATERIAL_CONSTRUCTION, "P13": Axis.NARRATIVE_SEQUENCING,
    "P14": Axis.INFORMATION, "P15": Axis.FORM, "P16": Axis.ATMOSPHERE_ENVIRONMENT,
    "P17": Axis.INFORMATION, "P18": Axis.INFORMATION, "P19": Axis.SPACE, "P20": Axis.FORM,
    "P21": Axis.MOTION_TEMPORAL, "P22": Axis.INTERACTION, "P23": Axis.INFORMATION,
    "P24": Axis.INFORMATION, "P25": Axis.NARRATIVE_SEQUENCING,
}
_MK_AXIS: Dict[str, Axis] = {
    "MK01": Axis.NARRATIVE_SEQUENCING, "MK02": Axis.INFORMATION, "MK03": Axis.INFORMATION,
    "MK04": Axis.NARRATIVE_SEQUENCING, "MK05": Axis.INFORMATION, "MK06": Axis.NARRATIVE_SEQUENCING,
    "MK07": Axis.INFORMATION, "MK08": Axis.INFORMATION, "MK09": Axis.INFORMATION, "MK10": Axis.INFORMATION,
    "MK11": Axis.INFORMATION, "MK12": Axis.NARRATIVE_SEQUENCING, "MK13": Axis.INFORMATION,
    "MK14": Axis.NARRATIVE_SEQUENCING, "MK15": Axis.NARRATIVE_SEQUENCING, "MK16": Axis.INFORMATION,
    "MK17": Axis.INFORMATION, "MK18": Axis.INFORMATION, "MK19": Axis.INFORMATION,
    "MK20": Axis.NARRATIVE_SEQUENCING, "MK21": Axis.INFORMATION, "MK22": Axis.INFORMATION,
    "MK23": Axis.INFORMATION, "MK24": Axis.INTERACTION, "MK25": Axis.INFORMATION,
}
_P_EXTRA_GUARDS: Dict[str, str] = {
    "P16": ";environmental-causality-must-come-from-existing-context-and-never-live-or-invented-environment-state",
    "P22": ";rule-change-cues-may-reflect-only-an-existing-application-state-transition-and-never-create-rules-actions-or-permissions",
    "P25": ";rhythmic-cultural-splice-never-asserts-a-cultural-lineage-without-a-separately-governed-reference",
}


def _zones(axis: Axis):
    if axis is Axis.MOTION_TEMPORAL:
        return _TEMPORAL_ZONES
    if axis in (Axis.FORM, Axis.SPACE, Axis.MATERIAL_CONSTRUCTION, Axis.ATMOSPHERE_ENVIRONMENT):
        return _LAYOUT_ZONES
    if axis is Axis.INTERACTION:
        return _ACTION_ZONES
    return _WORK_ZONES


def _slug(name: str) -> str:
    return name.lower().replace("_", "-")


def _izzul_directive(primitive_id: str, name: str) -> str:
    return (
        f"apply-{_slug(name)}-as-an-atomic-presentation-mechanism-over-existing-semantic-content-only;"
        "never-create-domain-state-relationships-chronology-cultural-identity-or-provider-behavior"
        + _P_EXTRA_GUARDS.get(primitive_id, "")
    )


def _miko_directive(name: str) -> str:
    return (
        f"apply-{_slug(name)}-only-when-corresponding-semantic-fields-or-relations-already-exist;"
        "never-infer-or-create-role-kinship-agency-capability-care-status-hierarchy-trajectory-timeline-ending-judgment-"
        "social-perception-resource-condition-or-application-state"
    )


def _temporal_directive(name: str) -> str:
    return (
        f"apply-{_slug(name)}-to-already-available-presentation-state-only;"
        "designed-pacing-is-not-added-wait-time;never-delay-provider-or-network-execution;never-withhold-ready-critical-information;"
        "never-fake-loading-or-typing;never-block-controls-for-temporal-effect"
    )


def _make_primitive(primitive_id: str, name: str, family: str, axis: Axis, provenance: str, directive: str) -> DNAUnit:
    is_temporal = axis is Axis.MOTION_TEMPORAL
    fallback = "static-immediate-presentation-with-no-added-wait-and-all-ready-information-visible" if is_temporal else ""
    primary = mechanism(
        primitive_id,
        "atomic",
        axis,
        directive,
        zones=_zones(axis),
        fallback=fallback,
        rank=64,
        accessibility_safe=not is_temporal,
        reading_safe=not is_temporal,
    )
    return unit(
        primitive_id,
        kind=UnitKind.PRIMITIVE,
        family=family,
        lineage=f"{family.lower()}-{_slug(name)}",
        mechanisms=(primary,),
        provenance=provenance,
        identity_survival="atomic-structural-primitive-without-assets",
    )


IZZUL_PRIMITIVES: Tuple[DNAUnit, ...] = tuple(
    _make_primitive(item_id, IZZUL_PRIMITIVE_NAMES[item_id], "IZZUL_PRIMITIVE", _P_AXIS[item_id], _PROV_P,
                    _izzul_directive(item_id, IZZUL_PRIMITIVE_NAMES[item_id]))
    for item_id in IZZUL_PRIMITIVE_IDS
)
MIKO_PRIMITIVES: Tuple[DNAUnit, ...] = tuple(
    _make_primitive(item_id, MIKO_PRIMITIVE_NAMES[item_id], "MIKO_PRIMITIVE", _MK_AXIS[item_id], _PROV_MK,
                    _miko_directive(MIKO_PRIMITIVE_NAMES[item_id]))
    for item_id in MIKO_PRIMITIVE_IDS
)
TEMPORAL_PRIMITIVES: Tuple[DNAUnit, ...] = tuple(
    _make_primitive(item_id, TEMPORAL_PRIMITIVE_NAMES[item_id], "TEMPORAL_PRIMITIVE", Axis.MOTION_TEMPORAL, _PROV_TP,
                    _temporal_directive(TEMPORAL_PRIMITIVE_NAMES[item_id]))
    for item_id in TEMPORAL_PRIMITIVE_IDS
)
M4_PRIMITIVES: Tuple[DNAUnit, ...] = IZZUL_PRIMITIVES + MIKO_PRIMITIVES + TEMPORAL_PRIMITIVES
PRIMITIVE_BY_ID: Dict[str, DNAUnit] = {item.id: item for item in M4_PRIMITIVES}


def primitive_asset_on_applicable(primitive_id: str) -> bool:
    if primitive_id not in PRIMITIVE_BY_ID:
        raise KeyError(primitive_id)
    return False


def register_m4_primitives(registry) -> None:
    for primitive in M4_PRIMITIVES:
        registry.register(primitive)
