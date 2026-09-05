"""Deterministic Design-DNA M0 marriage resolver.

The resolver is intentionally pure with respect to application state and host
frameworks: it consumes immutable-ish contract values and returns ThemeProjection.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Dict, Iterable, List, Sequence, Tuple

from design_dna.models import (
    AssetDecision,
    AssetIntent,
    AssetState,
    Axis,
    CompositionRequest,
    DNAUnit,
    DegradationState,
    FailureCode,
    MechanismContract,
    ProvenanceRecord,
    ResolutionIssue,
    ResolvedMechanism,
    RuntimeConstraints,
    SemanticContext,
    SemanticZone,
    ThemeProjection,
)
from design_dna.registry import DNARegistry, RegistryError


@dataclass(frozen=True)
class _Candidate:
    unit: DNAUnit
    mechanism: MechanismContract
    zone: SemanticZone
    directive: str
    degradation: DegradationState


def _composition_id(request: CompositionRequest) -> str:
    engines = ",".join(sorted(request.engine_ids))
    primitives = ",".join(sorted(request.primitive_ids))
    return f"{request.selected_reference_id}|E:{engines}|P:{primitives}|A:{request.archetype_id}"


def _unit_payload(unit: DNAUnit) -> dict:
    return {
        "id": unit.id,
        "kind": unit.kind.value,
        "family": unit.family,
        "lineage": unit.lineage,
        "provenance_pointer": unit.provenance_pointer,
        "identity_survival": unit.identity_survival,
        "compatible_unit_ids": sorted(unit.compatible_unit_ids),
        "conflicting_unit_ids": sorted(unit.conflicting_unit_ids),
        "mechanisms": [
            {
                "id": m.id,
                "axis": m.axis.value,
                "zones": sorted(z.value for z in m.zones),
                "directive": m.directive,
                "fallback_directive": m.fallback_directive,
                "ownership_rank": m.ownership_rank,
                "viewports": sorted(m.viewports),
                "states": sorted(m.states),
                "compatible_with": sorted(m.compatible_with),
                "conflicts_with": sorted(m.conflicts_with),
                "accessibility_safe": m.accessibility_safe,
                "reading_safe": m.reading_safe,
                "requires_asset_slot": m.requires_asset_slot,
                "host_capability": m.host_capability,
            }
            for m in sorted(unit.mechanisms, key=lambda item: item.id)
        ],
        "assets": [
            {
                "slot": a.slot,
                "asset_id": a.asset_id,
                "production_eligible": a.production_eligible,
                "license_status": a.license_status,
                "fallback_directive": a.fallback_directive,
                "ownership_rank": a.ownership_rank,
                "provenance_pointer": a.provenance_pointer,
            }
            for a in sorted(unit.assets, key=lambda item: (item.slot, item.asset_id))
        ],
    }


def _request_payload(request: CompositionRequest) -> dict:
    return {
        "selected_reference_id": request.selected_reference_id,
        "engine_ids": sorted(request.engine_ids),
        "primitive_ids": sorted(request.primitive_ids),
        "archetype_id": request.archetype_id,
        "asset_state": request.asset_state.value,
        "modifiers": dict(sorted(request.modifiers.items())),
    }


def _context_payload(context: SemanticContext) -> dict:
    return {
        "active_zones": sorted(z.value for z in context.active_zones),
        "viewport": context.viewport.value,
        "interaction_state": context.interaction_state,
        "reading_heavy_zones": sorted(z.value for z in context.reading_heavy_zones),
        "reduced_motion": context.reduced_motion,
        "accessibility_required": context.accessibility_required,
        "language": context.language,
        "script": context.script,
        "host_capabilities": sorted(context.host_capabilities),
    }


def _constraints_payload(constraints: RuntimeConstraints) -> dict:
    return {
        "contradiction_budget": constraints.contradiction_budget,
        "dominance_cap": constraints.dominance_cap,
        "blocked_axes": sorted(a.value for a in constraints.blocked_axes),
        "blocked_mechanism_ids": sorted(constraints.blocked_mechanism_ids),
        "reading_sanctuary": constraints.reading_sanctuary,
        "safe_baseline_directive": constraints.safe_baseline_directive,
    }


def _fingerprint(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _issue_payload(issue: ResolutionIssue) -> dict:
    return {
        "code": issue.code.value,
        "message": issue.message,
        "source_unit_id": issue.source_unit_id,
        "mechanism_id": issue.mechanism_id,
        "axis": issue.axis.value if issue.axis else None,
        "zone": issue.zone.value if issue.zone else None,
    }


def _asset_decision_payload(decision: AssetDecision) -> dict:
    return {
        "slot": decision.slot,
        "asset_id": decision.asset_id,
        "source_unit_id": decision.source_unit_id,
        "action": decision.action,
        "directive": decision.directive,
        "degradation": decision.degradation.value,
        "reason": decision.reason,
    }


def _mechanism_payload(mechanism: ResolvedMechanism) -> dict:
    return {
        "axis": mechanism.axis.value,
        "zone": mechanism.zone.value,
        "directive": mechanism.directive,
        "source_unit_id": mechanism.source_unit_id,
        "mechanism_id": mechanism.mechanism_id,
        "ownership_rank": mechanism.ownership_rank,
        "degradation": mechanism.degradation.value,
    }


def _make_projection(
    *,
    request: CompositionRequest,
    context: SemanticContext,
    constraints: RuntimeConstraints,
    units: Sequence[DNAUnit],
    mechanisms: Sequence[ResolvedMechanism],
    assets: Sequence[AssetDecision],
    provenance: Sequence[ProvenanceRecord],
    warnings: Sequence[ResolutionIssue],
    rejections: Sequence[ResolutionIssue],
    accessibility_applied: bool,
    reading_sanctuary_applied: bool,
    reduced_motion_applied: bool,
) -> ThemeProjection:
    canonical_mechanisms = tuple(sorted(
        mechanisms,
        key=lambda item: (item.axis.value, item.zone.value, -item.ownership_rank, item.source_unit_id, item.mechanism_id),
    ))
    canonical_assets = tuple(sorted(assets, key=lambda item: (item.slot, item.source_unit_id, item.asset_id)))
    canonical_warnings = tuple(sorted(warnings, key=lambda item: (item.code.value, item.source_unit_id, item.mechanism_id, item.message)))
    canonical_rejections = tuple(sorted(rejections, key=lambda item: (item.code.value, item.source_unit_id, item.mechanism_id, item.message)))
    canonical_provenance = tuple(sorted(
        provenance,
        key=lambda item: (
            item.source_unit_id,
            item.mechanism_id,
            item.axis.value if item.axis else "",
            item.zone.value if item.zone else "",
            item.action,
            item.reason,
        ),
    ))

    payload = {
        "request": _request_payload(request),
        "context": _context_payload(context),
        "constraints": _constraints_payload(constraints),
        "units": [_unit_payload(unit) for unit in sorted(units, key=lambda item: item.id)],
        "mechanisms": [_mechanism_payload(item) for item in canonical_mechanisms],
        "assets": [_asset_decision_payload(item) for item in canonical_assets],
        "warnings": [_issue_payload(item) for item in canonical_warnings],
        "rejections": [_issue_payload(item) for item in canonical_rejections],
    }
    return ThemeProjection(
        composition_id=_composition_id(request),
        fingerprint=_fingerprint(payload),
        viewport=context.viewport,
        mechanisms=canonical_mechanisms,
        asset_decisions=canonical_assets,
        provenance=canonical_provenance,
        warnings=canonical_warnings,
        rejections=canonical_rejections,
        accessibility_applied=accessibility_applied,
        reading_sanctuary_applied=reading_sanctuary_applied,
        reduced_motion_applied=reduced_motion_applied,
    )


def _resolve_assets(
    units: Sequence[DNAUnit],
    asset_state: AssetState,
) -> Tuple[Tuple[AssetDecision, ...], Tuple[ResolutionIssue, ...], Dict[str, AssetDecision]]:
    by_slot: Dict[str, List[Tuple[DNAUnit, AssetIntent]]] = {}
    for unit in units:
        for asset in unit.assets:
            by_slot.setdefault(asset.slot, []).append((unit, asset))

    decisions: List[AssetDecision] = []
    warnings: List[ResolutionIssue] = []
    lookup: Dict[str, AssetDecision] = {}

    for slot in sorted(by_slot):
        candidates = sorted(
            by_slot[slot],
            key=lambda pair: (-pair[1].ownership_rank, pair[0].id, pair[1].asset_id),
        )
        unit, asset = candidates[0]
        if len(candidates) > 1:
            warnings.append(ResolutionIssue(
                code=FailureCode.OWNERSHIP_COLLISION,
                message=f"Asset slot '{slot}' had {len(candidates)} owners; deterministic owner '{unit.id}' selected",
                source_unit_id=unit.id,
            ))

        if not asset.production_eligible:
            decision = AssetDecision(
                slot=slot,
                asset_id=asset.asset_id,
                source_unit_id=unit.id,
                action="structural_fallback",
                directive=asset.fallback_directive,
                degradation=DegradationState.ASSET_OFF_STRUCTURAL,
                reason="asset is not production-eligible",
            )
            warnings.append(ResolutionIssue(
                code=FailureCode.LICENSE_SCOPE_VIOLATION,
                message=f"Asset '{asset.asset_id}' is not production-eligible; structural fallback applied",
                source_unit_id=unit.id,
            ))
        elif asset_state is AssetState.AVAILABLE:
            decision = AssetDecision(
                slot=slot,
                asset_id=asset.asset_id,
                source_unit_id=unit.id,
                action="use_asset",
                directive=asset.asset_id,
                degradation=DegradationState.FULL,
            )
        elif asset_state is AssetState.LOADING:
            decision = AssetDecision(
                slot=slot,
                asset_id=asset.asset_id,
                source_unit_id=unit.id,
                action="safe_substitute",
                directive=asset.fallback_directive,
                degradation=DegradationState.SAFE_SUBSTITUTE,
                reason="asset still loading",
            )
        elif asset_state is AssetState.PARTIAL:
            decision = AssetDecision(
                slot=slot,
                asset_id=asset.asset_id,
                source_unit_id=unit.id,
                action="safe_substitute",
                directive=asset.fallback_directive,
                degradation=DegradationState.SAFE_SUBSTITUTE,
                reason="partial asset failure",
            )
        else:
            decision = AssetDecision(
                slot=slot,
                asset_id=asset.asset_id,
                source_unit_id=unit.id,
                action="structural_fallback",
                directive=asset.fallback_directive,
                degradation=DegradationState.ASSET_OFF_STRUCTURAL,
                reason="asset-off mode",
            )
        decisions.append(decision)
        lookup[slot] = decision

    return tuple(decisions), tuple(warnings), lookup


def _is_relevant(mechanism: MechanismContract, zone: SemanticZone, context: SemanticContext) -> bool:
    viewport_ok = "all" in mechanism.viewports or context.viewport.value in mechanism.viewports
    state_ok = "all" in mechanism.states or context.interaction_state in mechanism.states
    return viewport_ok and state_ok and zone in context.active_zones


def _candidate_from_mechanism(
    *,
    unit: DNAUnit,
    mechanism: MechanismContract,
    zone: SemanticZone,
    context: SemanticContext,
    constraints: RuntimeConstraints,
    asset_lookup: Dict[str, AssetDecision],
    warnings: List[ResolutionIssue],
    rejections: List[ResolutionIssue],
    provenance: List[ProvenanceRecord],
) -> _Candidate | None:
    directive = mechanism.directive
    degradation = DegradationState.FULL

    def demote_or_drop(reason: str, state: DegradationState, code: FailureCode) -> _Candidate | None:
        nonlocal directive, degradation
        warnings.append(ResolutionIssue(
            code=code,
            message=reason,
            source_unit_id=unit.id,
            mechanism_id=mechanism.id,
            axis=mechanism.axis,
            zone=zone,
        ))
        if mechanism.fallback_directive:
            directive = mechanism.fallback_directive
            degradation = state
            provenance.append(ProvenanceRecord(
                action="fallback",
                source_unit_id=unit.id,
                mechanism_id=mechanism.id,
                axis=mechanism.axis,
                zone=zone,
                reason=reason,
            ))
            return _Candidate(unit, mechanism, zone, directive, degradation)
        provenance.append(ProvenanceRecord(
            action="demoted",
            source_unit_id=unit.id,
            mechanism_id=mechanism.id,
            axis=mechanism.axis,
            zone=zone,
            reason=reason,
        ))
        return None

    if mechanism.axis in constraints.blocked_axes or mechanism.id in constraints.blocked_mechanism_ids:
        return demote_or_drop(
            "runtime hard-veto blocked mechanism projection",
            DegradationState.SAFE_BASELINE,
            FailureCode.FORBIDDEN_PROJECTION,
        )

    if mechanism.host_capability and mechanism.host_capability not in context.host_capabilities:
        return demote_or_drop(
            f"host capability '{mechanism.host_capability}' unavailable",
            DegradationState.SAFE_BASELINE,
            FailureCode.FORBIDDEN_PROJECTION,
        )

    if context.accessibility_required and not mechanism.accessibility_safe:
        return demote_or_drop(
            "accessibility super-veto demoted unsafe mechanism",
            DegradationState.ACCESSIBILITY_DEMOTED,
            FailureCode.FORBIDDEN_PROJECTION,
        )

    if context.reduced_motion and mechanism.axis is Axis.MOTION_TEMPORAL:
        return demote_or_drop(
            "reduced-motion preference demoted temporal mechanism",
            DegradationState.ACCESSIBILITY_DEMOTED,
            FailureCode.FORBIDDEN_PROJECTION,
        )

    is_reading_zone = zone is SemanticZone.U7 or zone in context.reading_heavy_zones
    if constraints.reading_sanctuary and is_reading_zone and not mechanism.reading_safe:
        return demote_or_drop(
            "Reading Sanctuary demoted high-intensity mechanism",
            DegradationState.READING_SANCTUARY_DEMOTED,
            FailureCode.FORBIDDEN_PROJECTION,
        )

    if mechanism.requires_asset_slot:
        asset_decision = asset_lookup.get(mechanism.requires_asset_slot)
        if asset_decision is None:
            issue = ResolutionIssue(
                code=FailureCode.ASSET_DEPENDENCY_FAILURE,
                message=f"Required asset slot '{mechanism.requires_asset_slot}' is not declared",
                source_unit_id=unit.id,
                mechanism_id=mechanism.id,
                axis=mechanism.axis,
                zone=zone,
            )
            if mechanism.fallback_directive:
                warnings.append(issue)
                directive = mechanism.fallback_directive
                degradation = DegradationState.ASSET_OFF_STRUCTURAL
                provenance.append(ProvenanceRecord(
                    action="fallback",
                    source_unit_id=unit.id,
                    mechanism_id=mechanism.id,
                    axis=mechanism.axis,
                    zone=zone,
                    reason=issue.message,
                ))
            else:
                rejections.append(issue)
                provenance.append(ProvenanceRecord(
                    action="rejected",
                    source_unit_id=unit.id,
                    mechanism_id=mechanism.id,
                    axis=mechanism.axis,
                    zone=zone,
                    reason=issue.message,
                ))
                return None
        elif asset_decision.action != "use_asset":
            directive = mechanism.fallback_directive or asset_decision.directive
            if not directive:
                issue = ResolutionIssue(
                    code=FailureCode.ASSET_DEPENDENCY_FAILURE,
                    message=f"Asset slot '{mechanism.requires_asset_slot}' degraded without structural fallback",
                    source_unit_id=unit.id,
                    mechanism_id=mechanism.id,
                    axis=mechanism.axis,
                    zone=zone,
                )
                rejections.append(issue)
                return None
            degradation = asset_decision.degradation
            provenance.append(ProvenanceRecord(
                action="fallback",
                source_unit_id=unit.id,
                mechanism_id=mechanism.id,
                axis=mechanism.axis,
                zone=zone,
                reason=asset_decision.reason,
            ))

    return _Candidate(unit, mechanism, zone, directive, degradation)


def _mechanisms_conflict(left: _Candidate, right: _Candidate) -> bool:
    if right.mechanism.id in left.mechanism.conflicts_with:
        return True
    if left.mechanism.id in right.mechanism.conflicts_with:
        return True
    if right.unit.id in left.unit.conflicting_unit_ids:
        return True
    if left.unit.id in right.unit.conflicting_unit_ids:
        return True
    if left.mechanism.compatible_with and right.mechanism.id not in left.mechanism.compatible_with:
        return True
    if right.mechanism.compatible_with and left.mechanism.id not in right.mechanism.compatible_with:
        return True
    return False


def resolve(
    registry: DNARegistry,
    request: CompositionRequest,
    context: SemanticContext,
    constraints: RuntimeConstraints | None = None,
) -> ThemeProjection:
    """Resolve canonical DNA into a host-neutral deterministic ThemeProjection."""
    constraints = constraints or RuntimeConstraints()
    warnings: List[ResolutionIssue] = []
    rejections: List[ResolutionIssue] = []
    provenance: List[ProvenanceRecord] = []
    units: Tuple[DNAUnit, ...] = ()

    try:
        request.validate()
        context.validate()
        constraints.validate()
        units = registry.select(request)
    except (RegistryError, TypeError, ValueError) as exc:
        rejections.append(ResolutionIssue(
            code=FailureCode.UNEXPLAINABLE_COMPOSITION,
            message=str(exc),
        ))
        return _make_projection(
            request=request,
            context=context,
            constraints=constraints,
            units=units,
            mechanisms=(),
            assets=(),
            provenance=(),
            warnings=(),
            rejections=rejections,
            accessibility_applied=False,
            reading_sanctuary_applied=False,
            reduced_motion_applied=False,
        )

    asset_decisions, asset_warnings, asset_lookup = _resolve_assets(units, request.asset_state)
    warnings.extend(asset_warnings)

    grouped: Dict[Tuple[Axis, SemanticZone], List[_Candidate]] = {}
    relevant_count = 0
    accessibility_applied = False
    reading_sanctuary_applied = False
    reduced_motion_applied = False

    for unit in units:
        for mechanism in sorted(unit.mechanisms, key=lambda item: item.id):
            for zone in sorted(mechanism.zones, key=lambda item: item.value):
                if not _is_relevant(mechanism, zone, context):
                    continue
                relevant_count += 1
                if context.accessibility_required and not mechanism.accessibility_safe:
                    accessibility_applied = True
                if context.reduced_motion and mechanism.axis is Axis.MOTION_TEMPORAL:
                    reduced_motion_applied = True
                if constraints.reading_sanctuary and (zone is SemanticZone.U7 or zone in context.reading_heavy_zones) and not mechanism.reading_safe:
                    reading_sanctuary_applied = True

                candidate = _candidate_from_mechanism(
                    unit=unit,
                    mechanism=mechanism,
                    zone=zone,
                    context=context,
                    constraints=constraints,
                    asset_lookup=asset_lookup,
                    warnings=warnings,
                    rejections=rejections,
                    provenance=provenance,
                )
                if candidate is not None:
                    grouped.setdefault((mechanism.axis, zone), []).append(candidate)

    resolved: List[ResolvedMechanism] = []
    contradiction_count = 0

    for key in sorted(grouped, key=lambda item: (item[0].value, item[1].value)):
        candidates = sorted(
            grouped[key],
            key=lambda item: (-item.mechanism.ownership_rank, item.unit.id, item.mechanism.id),
        )
        winners: List[_Candidate] = []
        for candidate in candidates:
            conflicting = next((winner for winner in winners if _mechanisms_conflict(candidate, winner)), None)
            if conflicting is not None:
                contradiction_count += 1
                reason = (
                    f"Mechanism '{candidate.mechanism.id}' conflicts with winning mechanism "
                    f"'{conflicting.mechanism.id}' on {key[0].value}/{key[1].value}"
                )
                warnings.append(ResolutionIssue(
                    code=FailureCode.OWNERSHIP_COLLISION,
                    message=reason,
                    source_unit_id=candidate.unit.id,
                    mechanism_id=candidate.mechanism.id,
                    axis=key[0],
                    zone=key[1],
                ))
                provenance.append(ProvenanceRecord(
                    action="demoted",
                    source_unit_id=candidate.unit.id,
                    mechanism_id=candidate.mechanism.id,
                    axis=key[0],
                    zone=key[1],
                    reason=reason,
                ))
                continue
            if len(winners) >= constraints.dominance_cap:
                reason = f"Dominance cap {constraints.dominance_cap} reached on {key[0].value}/{key[1].value}"
                warnings.append(ResolutionIssue(
                    code=FailureCode.OWNERSHIP_COLLISION,
                    message=reason,
                    source_unit_id=candidate.unit.id,
                    mechanism_id=candidate.mechanism.id,
                    axis=key[0],
                    zone=key[1],
                ))
                provenance.append(ProvenanceRecord(
                    action="demoted",
                    source_unit_id=candidate.unit.id,
                    mechanism_id=candidate.mechanism.id,
                    axis=key[0],
                    zone=key[1],
                    reason=reason,
                ))
                continue
            winners.append(candidate)

        for winner in winners:
            resolved.append(ResolvedMechanism(
                axis=winner.mechanism.axis,
                zone=winner.zone,
                directive=winner.directive,
                source_unit_id=winner.unit.id,
                mechanism_id=winner.mechanism.id,
                ownership_rank=winner.mechanism.ownership_rank,
                degradation=winner.degradation,
            ))
            provenance.append(ProvenanceRecord(
                action="applied",
                source_unit_id=winner.unit.id,
                mechanism_id=winner.mechanism.id,
                axis=winner.mechanism.axis,
                zone=winner.zone,
                reason="deterministic ownership winner",
            ))

    if contradiction_count > constraints.contradiction_budget:
        rejections.append(ResolutionIssue(
            code=FailureCode.CONTRADICTION_OVERFLOW,
            message=(
                f"Contradiction count {contradiction_count} exceeds budget "
                f"{constraints.contradiction_budget}"
            ),
        ))

    if relevant_count > 0 and not resolved:
        rejections.append(ResolutionIssue(
            code=FailureCode.FALLBACK_IDENTITY_COLLAPSE,
            message="All relevant mechanisms were removed; structural identity did not survive",
        ))

    return _make_projection(
        request=request,
        context=context,
        constraints=constraints,
        units=units,
        mechanisms=resolved,
        assets=asset_decisions,
        provenance=provenance,
        warnings=warnings,
        rejections=rejections,
        accessibility_applied=accessibility_applied,
        reading_sanctuary_applied=reading_sanctuary_applied,
        reduced_motion_applied=reduced_motion_applied,
    )
