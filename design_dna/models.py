"""Framework-neutral Design-DNA M0 runtime contracts.

This package intentionally has no dependency on Streamlit, Reflex, application/core,
providers, persistence, or browser types. It is the canonical runtime seam that
future presentation hosts consume through adapters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Optional, Tuple


def _freeze_map(value: Optional[Mapping[str, str]]) -> Mapping[str, str]:
    return MappingProxyType(dict(value or {}))


class UnitKind(str, Enum):
    REFERENCE = "REFERENCE"
    ENGINE = "ENGINE"
    PRIMITIVE = "PRIMITIVE"
    FIXTURE = "FIXTURE"


class Axis(str, Enum):
    FORM = "FORM"
    SPACE = "SPACE"
    INFORMATION = "INFORMATION"
    MATERIAL_CONSTRUCTION = "MATERIAL_CONSTRUCTION"
    LIGHT = "LIGHT"
    COLOR = "COLOR"
    TYPOGRAPHY_SCRIPT = "TYPOGRAPHY_SCRIPT"
    MOTION_TEMPORAL = "MOTION_TEMPORAL"
    NARRATIVE_SEQUENCING = "NARRATIVE_SEQUENCING"
    INTERACTION = "INTERACTION"
    ATMOSPHERE_ENVIRONMENT = "ATMOSPHERE_ENVIRONMENT"
    SOUND_RHYTHM = "SOUND_RHYTHM"
    ADAPTATION = "ADAPTATION"
    SYMBOL_ICONOGRAPHY = "SYMBOL_ICONOGRAPHY"
    SCALE_GRANULARITY = "SCALE_GRANULARITY"


class SemanticZone(str, Enum):
    U1 = "U1_SHELL"
    U2 = "U2_PRIMARY_CONTEXT"
    U3 = "U3_PRIMARY_WORK_SURFACE"
    U4 = "U4_WORK_ITEM"
    U5 = "U5_PRIMARY_ACTION"
    U6 = "U6_SYSTEM_STATE"
    U7 = "U7_READING_SANCTUARY"
    U8 = "U8_AUXILIARY_CONTEXT"
    U9 = "U9_PROVENANCE_DISCLOSURE"


ALL_ZONES: Tuple[SemanticZone, ...] = tuple(SemanticZone)


class Viewport(str, Enum):
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


class AssetState(str, Enum):
    AVAILABLE = "available"
    LOADING = "loading"
    PARTIAL = "partial"
    OFF = "off"


class DegradationState(str, Enum):
    FULL = "full"
    SAFE_SUBSTITUTE = "safe_substitute"
    ASSET_OFF_STRUCTURAL = "asset_off_structural"
    ACCESSIBILITY_DEMOTED = "accessibility_demoted"
    READING_SANCTUARY_DEMOTED = "reading_sanctuary_demoted"
    PERFORMANCE_DEMOTED = "performance_demoted"
    SAFE_BASELINE = "safe_baseline"


class FailureCode(str, Enum):
    LICENSE_SCOPE_VIOLATION = "LICENSE_SCOPE_VIOLATION"
    ASSET_DEPENDENCY_FAILURE = "ASSET_DEPENDENCY_FAILURE"
    OWNERSHIP_COLLISION = "OWNERSHIP_COLLISION"
    CONTRADICTION_OVERFLOW = "CONTRADICTION_OVERFLOW"
    FORBIDDEN_PROJECTION = "FORBIDDEN_PROJECTION"
    FALLBACK_IDENTITY_COLLAPSE = "FALLBACK_IDENTITY_COLLAPSE"
    UNEXPLAINABLE_COMPOSITION = "UNEXPLAINABLE_COMPOSITION"
    MECHANISM_EVIDENCE_GAP = "MECHANISM_EVIDENCE_GAP"


@dataclass(frozen=True)
class MechanismContract:
    """One resolver-readable mechanism scoped by axis × zone × viewport/state."""

    id: str
    axis: Axis
    zones: Tuple[SemanticZone, ...]
    directive: str
    fallback_directive: str = ""
    ownership_rank: int = 50
    viewports: Tuple[str, ...] = ("all",)
    states: Tuple[str, ...] = ("all",)
    compatible_with: Tuple[str, ...] = ()
    conflicts_with: Tuple[str, ...] = ()
    accessibility_safe: bool = True
    reading_safe: bool = True
    requires_asset_slot: Optional[str] = None
    host_capability: Optional[str] = None

    def validate(self) -> None:
        if not self.id.strip():
            raise ValueError("MechanismContract.id must be non-empty")
        if not isinstance(self.axis, Axis):
            raise TypeError("MechanismContract.axis must be Axis")
        if not self.zones or any(not isinstance(z, SemanticZone) for z in self.zones):
            raise ValueError("MechanismContract.zones must contain canonical semantic zones")
        if not self.directive.strip():
            raise ValueError("MechanismContract.directive must be non-empty")
        if not 0 <= self.ownership_rank <= 100:
            raise ValueError("MechanismContract.ownership_rank must be in [0, 100]")
        if not self.viewports or any(not str(v).strip() for v in self.viewports):
            raise ValueError("MechanismContract.viewports must be non-empty")
        if not self.states or any(not str(v).strip() for v in self.states):
            raise ValueError("MechanismContract.states must be non-empty")
        if self.requires_asset_slot is not None and not self.requires_asset_slot.strip():
            raise ValueError("requires_asset_slot must be non-empty when provided")


@dataclass(frozen=True)
class AssetIntent:
    """Asset intent is optional enrichment; structural fallback is mandatory."""

    slot: str
    asset_id: str
    production_eligible: bool
    license_status: str
    fallback_directive: str
    ownership_rank: int = 50
    provenance_pointer: str = ""

    def validate(self) -> None:
        if not self.slot.strip() or not self.asset_id.strip():
            raise ValueError("AssetIntent slot and asset_id must be non-empty")
        if not self.license_status.strip():
            raise ValueError("AssetIntent.license_status must be explicit")
        if not self.fallback_directive.strip():
            raise ValueError("AssetIntent requires structural fallback")
        if not 0 <= self.ownership_rank <= 100:
            raise ValueError("AssetIntent.ownership_rank must be in [0, 100]")


@dataclass(frozen=True)
class DNAUnit:
    id: str
    kind: UnitKind
    family: str
    lineage: str
    provenance_pointer: str
    mechanisms: Tuple[MechanismContract, ...] = ()
    assets: Tuple[AssetIntent, ...] = ()
    compatible_unit_ids: Tuple[str, ...] = ()
    conflicting_unit_ids: Tuple[str, ...] = ()
    identity_survival: str = "structural"

    def validate(self) -> None:
        if not self.id.strip():
            raise ValueError("DNAUnit.id must be non-empty")
        if not isinstance(self.kind, UnitKind):
            raise TypeError("DNAUnit.kind must be UnitKind")
        if not self.family.strip() or not self.lineage.strip():
            raise ValueError("DNAUnit family and lineage must be explicit")
        if not self.provenance_pointer.strip():
            raise ValueError("DNAUnit.provenance_pointer must be explicit")
        mechanism_ids = set()
        for mechanism in self.mechanisms:
            mechanism.validate()
            if mechanism.id in mechanism_ids:
                raise ValueError(f"Duplicate mechanism id '{mechanism.id}' in unit '{self.id}'")
            mechanism_ids.add(mechanism.id)
        asset_slots = set()
        for asset in self.assets:
            asset.validate()
            if asset.slot in asset_slots:
                raise ValueError(f"Duplicate asset slot '{asset.slot}' in unit '{self.id}'")
            asset_slots.add(asset.slot)
        if not self.identity_survival.strip():
            raise ValueError("DNAUnit.identity_survival must be explicit")


@dataclass(frozen=True)
class CompositionRequest:
    selected_reference_id: str
    engine_ids: Tuple[str, ...] = ()
    primitive_ids: Tuple[str, ...] = ()
    archetype_id: str = "chat_first"
    asset_state: AssetState = AssetState.OFF
    modifiers: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(self, "modifiers", _freeze_map(self.modifiers))

    def validate(self) -> None:
        if not self.selected_reference_id.strip():
            raise ValueError("CompositionRequest.selected_reference_id must be non-empty")
        if not self.archetype_id.strip():
            raise ValueError("CompositionRequest.archetype_id must be non-empty")
        if not isinstance(self.asset_state, AssetState):
            raise TypeError("CompositionRequest.asset_state must be AssetState")
        if len(set(self.engine_ids)) != len(self.engine_ids):
            raise ValueError("CompositionRequest.engine_ids must not contain duplicates")
        if len(set(self.primitive_ids)) != len(self.primitive_ids):
            raise ValueError("CompositionRequest.primitive_ids must not contain duplicates")


@dataclass(frozen=True)
class SemanticContext:
    active_zones: Tuple[SemanticZone, ...] = ALL_ZONES
    viewport: Viewport = Viewport.DESKTOP
    interaction_state: str = "default"
    reading_heavy_zones: Tuple[SemanticZone, ...] = (SemanticZone.U7,)
    reduced_motion: bool = False
    accessibility_required: bool = True
    language: str = ""
    script: str = ""
    host_capabilities: Tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.active_zones or any(not isinstance(z, SemanticZone) for z in self.active_zones):
            raise ValueError("SemanticContext.active_zones must contain canonical zones")
        if not isinstance(self.viewport, Viewport):
            raise TypeError("SemanticContext.viewport must be Viewport")
        if not self.interaction_state.strip():
            raise ValueError("SemanticContext.interaction_state must be non-empty")


@dataclass(frozen=True)
class RuntimeConstraints:
    contradiction_budget: int = 2
    dominance_cap: int = 2
    blocked_axes: Tuple[Axis, ...] = ()
    blocked_mechanism_ids: Tuple[str, ...] = ()
    reading_sanctuary: bool = True
    safe_baseline_directive: str = "semantic-default"

    def validate(self) -> None:
        if self.contradiction_budget < 0:
            raise ValueError("contradiction_budget must be >= 0")
        if self.dominance_cap < 1:
            raise ValueError("dominance_cap must be >= 1")
        if any(not isinstance(axis, Axis) for axis in self.blocked_axes):
            raise TypeError("blocked_axes must contain Axis values")
        if not self.safe_baseline_directive.strip():
            raise ValueError("safe_baseline_directive must be non-empty")


@dataclass(frozen=True)
class ResolvedMechanism:
    axis: Axis
    zone: SemanticZone
    directive: str
    source_unit_id: str
    mechanism_id: str
    ownership_rank: int
    degradation: DegradationState = DegradationState.FULL


@dataclass(frozen=True)
class AssetDecision:
    slot: str
    asset_id: str
    source_unit_id: str
    action: str
    directive: str
    degradation: DegradationState
    reason: str = ""


@dataclass(frozen=True)
class ProvenanceRecord:
    action: str
    source_unit_id: str
    mechanism_id: str
    axis: Optional[Axis]
    zone: Optional[SemanticZone]
    reason: str


@dataclass(frozen=True)
class ResolutionIssue:
    code: FailureCode
    message: str
    source_unit_id: str = ""
    mechanism_id: str = ""
    axis: Optional[Axis] = None
    zone: Optional[SemanticZone] = None


@dataclass(frozen=True)
class ThemeProjection:
    composition_id: str
    fingerprint: str
    viewport: Viewport
    mechanisms: Tuple[ResolvedMechanism, ...]
    asset_decisions: Tuple[AssetDecision, ...]
    provenance: Tuple[ProvenanceRecord, ...]
    warnings: Tuple[ResolutionIssue, ...] = ()
    rejections: Tuple[ResolutionIssue, ...] = ()
    accessibility_applied: bool = False
    reading_sanctuary_applied: bool = False
    reduced_motion_applied: bool = False

    @property
    def is_valid(self) -> bool:
        return not self.rejections
