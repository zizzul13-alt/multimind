"""Design-DNA M4: canonical 68 additive atomic primitives.

Primitives alter presentation of already-existing semantic state only. They never
create domain/story/cultural truth, permissions, provider timing, or hidden wait.
"""
from __future__ import annotations
from typing import Dict, Tuple

from design_dna.catalog import mechanism, unit
from design_dna.models import Axis, DNAUnit, SemanticZone, UnitKind


def _indexed(prefix: str, names: Tuple[str, ...]) -> Dict[str, str]:
    return {f"{prefix}{index:02d}": name for index, name in enumerate(names, 1)}


IZZUL_PRIMITIVE_NAMES = _indexed("P", (
    "SCALE_PUNCTUATION", "NEGATIVE_SPACE_PACING", "DENSITY_MODULATION", "PROGRESSIVE_REVEAL",
    "STATE_OVERLAY", "TOPOLOGICAL_TRAVERSAL", "LAYERED_WORLD_RULES", "TEMPORAL_PUNCTUATION",
    "STATE_LINKED_DEFORMATION", "DIRECTIONAL_FORCE_FORM", "ORNAMENT_AS_STRUCTURE", "MATERIAL_LAYER_REVEAL",
    "EDITORIAL_SEGMENT_PUNCTUATION", "RELATIONAL_ANCHOR", "REPRESENTATIONAL_MISMATCH", "ENVIRONMENTAL_CAUSALITY",
    "SYSTEM_WORLD_DUAL_LAYER", "DETAIL_DENSITY_FOCUS", "CROPPING_AS_COMPOSITION", "REFRACTIVE_FRAGMENTATION",
    "CONFRONTATION_TIME_DILATION", "RULE_CHANGING_STAGE", "INFRASTRUCTURE_AS_SYSTEM", "CORRESPONDENCE_AS_OBJECT",
    "RHYTHMIC_CULTURAL_SPLICE",
))
MIKO_PRIMITIVE_NAMES = _indexed("MK", (
    "TRAJECTORY_INTERVENTION", "PERIPHERAL_AGENCY", "ROLE_REFRAMING", "POST_CANON_REPAIR", "CARE_ACCUMULATION",
    "CAPABILITY_TRANSFER", "PREVENTIVE_GUIDANCE", "CHOSEN_KINSHIP", "CONTESTED_BELONGING", "LATENT_CAPABILITY",
    "CARE_FIRST_HIERARCHY", "LOW_PROFILE_SURVIVAL", "RESOURCE_CONSTRAINED_PLANNING", "TIMELINE_DRIFT",
    "ENDING_AUTHORITY", "EXIT_STRATEGY_SET", "RELATIONAL_PERSISTENCE", "FUTURE_JUDGMENT_FEEDBACK",
    "SOCIAL_PERCEPTION_GAP", "VOLUNTARY_ROLE_EXPANSION", "SIBLING_GUARDIANSHIP", "PATRONAGE_INDIRECT_AGENCY",
    "UNCERTAINTY_INTERPRETATION", "BOUNDARY_SETTING_IN_CARE", "SYSTEM_LITERACY_FROM_LOW_STATUS",
))
TEMPORAL_PRIMITIVE_NAMES = _indexed("TP", (
    "PERIODICITY", "STRUCTURAL_BOUNDARY", "INTENSITY_ENVELOPE", "RESOLUTION", "RECURRENCE_WITH_VARIATION",
    "RETURN_RECALL", "CALL_RESPONSE_HANDOFF", "EXPECTATION_DISPLACEMENT", "INTERRUPTION",
    "NEGATIVE_INTERVAL_RESERVED_GAP", "RATE_CHANGE", "DENSITY_EVOLUTION", "LAYER_ENTRY_EXIT",
    "PARALLEL_TEMPORAL_VOICES", "ANTICIPATION", "IRREVERSIBLE_PROGRESSION", "TERMINAL_RESOLUTION_AFTERBODY",
    "TEMPORAL_PUNCTUATION",
))

IZZUL_PRIMITIVE_IDS = tuple(IZZUL_PRIMITIVE_NAMES)
MIKO_PRIMITIVE_IDS = tuple(MIKO_PRIMITIVE_NAMES)
TEMPORAL_PRIMITIVE_IDS = tuple(TEMPORAL_PRIMITIVE_NAMES)
TEMPORAL_HISTORICAL_NON_ADDITIVE = ("TP19", "TP20")
M4_PRIMITIVE_IDS = IZZUL_PRIMITIVE_IDS + MIKO_PRIMITIVE_IDS + TEMPORAL_PRIMITIVE_IDS
PRIMITIVE_NAMES = {**IZZUL_PRIMITIVE_NAMES, **MIKO_PRIMITIVE_NAMES, **TEMPORAL_PRIMITIVE_NAMES}

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

_WORK = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U6, SemanticZone.U8)
_LAYOUT = (SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)
_ACTION = (SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8)
_TEMPORAL = (SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)

_P_AXIS_GROUPS = {
    Axis.SCALE_GRANULARITY: ("P01",),
    Axis.SPACE: ("P02", "P19"),
    Axis.INFORMATION: ("P03", "P05", "P07", "P14", "P17", "P18", "P23", "P24"),
    Axis.NARRATIVE_SEQUENCING: ("P04", "P06", "P13", "P25"),
    Axis.MOTION_TEMPORAL: ("P08", "P21"),
    Axis.FORM: ("P09", "P10", "P11", "P15", "P20"),
    Axis.MATERIAL_CONSTRUCTION: ("P12",),
    Axis.ATMOSPHERE_ENVIRONMENT: ("P16",),
    Axis.INTERACTION: ("P22",),
}
_P_AXIS = {item_id: axis for axis, ids in _P_AXIS_GROUPS.items() for item_id in ids}
_MK_NARRATIVE = frozenset(("MK01", "MK04", "MK06", "MK12", "MK14", "MK15", "MK20"))
_MK_INTERACTION = frozenset(("MK24",))
_MK_AXIS = {
    item_id: (Axis.NARRATIVE_SEQUENCING if item_id in _MK_NARRATIVE else Axis.INTERACTION if item_id in _MK_INTERACTION else Axis.INFORMATION)
    for item_id in MIKO_PRIMITIVE_IDS
}

_NO_WAIT = (
    ";designed-pacing-is-not-added-wait-time;never-delay-provider-or-network-execution;"
    "never-withhold-ready-critical-information;never-fake-loading-or-typing;never-block-controls-for-temporal-effect"
)
_P_EXTRA_GUARDS = {
    "P08": _NO_WAIT,
    "P16": ";environmental-causality-must-come-from-existing-context-and-never-live-or-invented-environment-state",
    "P21": _NO_WAIT,
    "P22": ";rule-change-cues-may-reflect-only-an-existing-application-state-transition-and-never-create-rules-actions-or-permissions",
    "P25": ";rhythmic-cultural-splice-never-asserts-a-cultural-lineage-without-a-separately-governed-reference",
}


def _zones(axis: Axis):
    if axis is Axis.MOTION_TEMPORAL:
        return _TEMPORAL
    if axis in (Axis.FORM, Axis.SPACE, Axis.MATERIAL_CONSTRUCTION, Axis.ATMOSPHERE_ENVIRONMENT):
        return _LAYOUT
    if axis is Axis.INTERACTION:
        return _ACTION
    return _WORK


def _slug(name: str) -> str:
    return name.lower().replace("_", "-")


def _p_directive(item_id: str, name: str) -> str:
    return (
        f"apply-{_slug(name)}-as-an-atomic-presentation-mechanism-over-existing-semantic-content-only;"
        "never-create-domain-state-relationships-chronology-cultural-identity-or-provider-behavior"
        + _P_EXTRA_GUARDS.get(item_id, "")
    )


def _mk_directive(name: str) -> str:
    return (
        f"apply-{_slug(name)}-only-when-corresponding-semantic-fields-or-relations-already-exist;"
        "never-infer-or-create-role-kinship-agency-capability-care-status-hierarchy-trajectory-timeline-ending-judgment-"
        "social-perception-resource-condition-or-application-state"
    )


def _tp_directive(name: str) -> str:
    return f"apply-{_slug(name)}-to-already-available-presentation-state-only" + _NO_WAIT


def _primitive(item_id: str, name: str, family: str, axis: Axis, provenance: str, directive: str) -> DNAUnit:
    temporal = axis is Axis.MOTION_TEMPORAL
    primary = mechanism(
        item_id, "atomic", axis, directive, zones=_zones(axis), rank=64,
        fallback="static-immediate-presentation-with-no-added-wait-and-all-ready-information-visible" if temporal else "",
        accessibility_safe=not temporal, reading_safe=not temporal,
    )
    return unit(
        item_id, kind=UnitKind.PRIMITIVE, family=family, lineage=f"{family.lower()}-{_slug(name)}",
        mechanisms=(primary,), provenance=provenance,
        identity_survival="atomic-structural-primitive-without-assets",
    )


IZZUL_PRIMITIVES: Tuple[DNAUnit, ...] = tuple(
    _primitive(item_id, name, "IZZUL_PRIMITIVE", _P_AXIS[item_id], _PROV_P, _p_directive(item_id, name))
    for item_id, name in IZZUL_PRIMITIVE_NAMES.items()
)
MIKO_PRIMITIVES: Tuple[DNAUnit, ...] = tuple(
    _primitive(item_id, name, "MIKO_PRIMITIVE", _MK_AXIS[item_id], _PROV_MK, _mk_directive(name))
    for item_id, name in MIKO_PRIMITIVE_NAMES.items()
)
TEMPORAL_PRIMITIVES: Tuple[DNAUnit, ...] = tuple(
    _primitive(item_id, name, "TEMPORAL_PRIMITIVE", Axis.MOTION_TEMPORAL, _PROV_TP, _tp_directive(name))
    for item_id, name in TEMPORAL_PRIMITIVE_NAMES.items()
)
M4_PRIMITIVES = IZZUL_PRIMITIVES + MIKO_PRIMITIVES + TEMPORAL_PRIMITIVES
PRIMITIVE_BY_ID = {item.id: item for item in M4_PRIMITIVES}


def primitive_asset_on_applicable(primitive_id: str) -> bool:
    if primitive_id not in PRIMITIVE_BY_ID:
        raise KeyError(primitive_id)
    return False


def register_m4_primitives(registry) -> None:
    for primitive in M4_PRIMITIVES:
        registry.register(primitive)
