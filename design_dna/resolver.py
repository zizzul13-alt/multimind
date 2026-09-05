"""Deterministic Design-DNA M0 marriage resolver.

The resolver is host-neutral and application-state neutral. It consumes validated
contracts and produces a deterministic ThemeProjection plus explainability data.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Dict, List, Sequence, Tuple

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
    Viewport,
)
from design_dna.registry import DNARegistry, RegistryError


@dataclass(frozen=True)
class _Candidate:
    unit: DNAUnit
    mechanism: MechanismContract
    zone: SemanticZone
    directive: str
    degradation: DegradationState


def _enum_value(value) -> str:
    return value.value if isinstance(value, Enum) else str(value)


def _safe_text(value, fallback: str = "") -> str:
    return value if isinstance(value, str) and value.strip() else fallback


def _safe_viewport(context: SemanticContext) -> Viewport:
    return context.viewport if isinstance(context.viewport, Viewport) else Viewport.DESKTOP


def _safe_strings(values) -> list[str]:
    try:
        return sorted(str(value) for value in values)
    except TypeError:
        return [str(values)]


def _composition_id(request: CompositionRequest) -> str:
    return (
        f"{_safe_text(request.selected_reference_id, '<invalid>')}"
        f"|E:{','.join(_safe_strings(request.engine_ids))}"
        f"|P:{','.join(_safe_strings(request.primitive_ids))}"
        f"|A:{_safe_text(request.archetype_id, '<invalid>')}"
    )


def _unit_payload(unit: DNAUnit) -> dict:
    return {
        "id": unit.id,
        "kind": _enum_value(unit.kind),
        "family": unit.family,
        "lineage": unit.lineage,
        "provenance_pointer": unit.provenance_pointer,
        "identity_survival": unit.identity_survival,
        "compatible_unit_ids": _safe_strings(unit.compatible_unit_ids),
        "conflicting_unit_ids": _safe_strings(unit.conflicting_unit_ids),
        "mechanisms": [
            {
                "id": m.id,
                "axis": _enum_value(m.axis),
                "zones": sorted(_enum_value(z) for z in m.zones),
                "directive": m.directive,
                "fallback_directive": m.fallback_directive,
                "ownership_rank": m.ownership_rank,
                "viewports": _safe_strings(m.viewports),
                "states": _safe_strings(m.states),
                "compatible_with": _safe_strings(m.compatible_with),
                "conflicts_with": _safe_strings(m.conflicts_with),
                "accessibility_safe": m.accessibility_safe,
                "reading_safe": m.reading_safe,
                "requires_asset_slot": m.requires_asset_slot,
                "host_capability": m.host_capability,
            }
            for m in sorted(unit.mechanisms, key=lambda item: item.id)
        ],
        "axis_absences": [
            {"axis": _enum_value(a.axis), "state": _enum_value(a.state)}
            for a in sorted(unit.axis_absences, key=lambda item: _enum_value(item.axis))
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
        "selected_reference_id": str(request.selected_reference_id),
        "engine_ids": _safe_strings(request.engine_ids),
        "primitive_ids": _safe_strings(request.primitive_ids),
        "archetype_id": str(request.archetype_id),
        "asset_state": _enum_value(request.asset_state),
        "modifiers": dict(sorted((str(k), str(v)) for k, v in dict(request.modifiers).items())),
    }


def _context_payload(context: SemanticContext) -> dict:
    return {
        "active_zones": sorted(_enum_value(z) for z in context.active_zones),
        "viewport": _enum_value(context.viewport),
        "interaction_state": str(context.interaction_state),
        "reading_heavy_zones": sorted(_enum_value(z) for z in context.reading_heavy_zones),
        "reduced_motion": context.reduced_motion,
        "accessibility_required": context.accessibility_required,
        "language": str(context.language),
        "script": str(context.script),
        "host_capabilities": _safe_strings(context.host_capabilities),
    }


def _constraints_payload(constraints: RuntimeConstraints) -> dict:
    return {
        "contradiction_budget": constraints.contradiction_budget,
        "dominance_cap": constraints.dominance_cap,
        "blocked_axes": sorted(_enum_value(a) for a in constraints.blocked_axes),
        "blocked_mechanism_ids": _safe_strings(constraints.blocked_mechanism_ids),
        "reading_sanctuary": constraints.reading_sanctuary,
        "safe_baseline_directive": str(constraints.safe_baseline_directive),
    }


def _fingerprint(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _issue_payload(issue: ResolutionIssue) -> dict:
    return {
        "code": _enum_value(issue.code),
        "message": issue.message,
        "source_unit_id": issue.source_unit_id,
        "mechanism_id": issue.mechanism_id,
        "axis": _enum_value(issue.axis) if issue.axis else None,
        "zone": _enum_value(issue.zone) if issue.zone else None,
    }


def _asset_decision_payload(decision: AssetDecision) -> dict:
    return {
        "slot": decision.slot,
        "asset_id": decision.asset_id,
        "source_unit_id": decision.source_unit_id,
        "action": decision.action,
        "directive": decision.directive,
        "degradation": _enum_value(decision.degradation),
        "reason": decision.reason,
    }


def _mechanism_payload(mechanism: ResolvedMechanism) -> dict:
    return {
        "axis": _enum_value(mechanism.axis),
        "zone": _enum_value(mechanism.zone),
        "viewport": _enum_value(mechanism.viewport),
        "interaction_state": mechanism.interaction_state,
        "directive": mechanism.directive,
        "source_unit_id": mechanism.source_unit_id,
        "mechanism_id": mechanism.mechanism_id,
        "ownership_rank": mechanism.ownership_rank,
        "degradation": _enum_value(mechanism.degradation),
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
        key=lambda item: (
            _enum_value(item.axis), _enum_value(item.zone), _enum_value(item.viewport),
            item.interaction_state, -item.ownership_rank, item.source_unit_id, item.mechanism_id,
        ),
    ))
    canonical_assets = tuple(sorted(assets, key=lambda item: (item.slot, item.source_unit_id, item.asset_id)))
    canonical_warnings = tuple(sorted(
        warnings,
        key=lambda item: (_enum_value(item.code), item.source_unit_id, item.mechanism_id, item.message),
    ))
    canonical_rejections = tuple(sorted(
        rejections,
        key=lambda item: (_enum_value(item.code), item.source_unit_id, item.mechanism_id, item.message),
    ))
    canonical_provenance = tuple(sorted(
        provenance,
        key=lambda item: (
            item.source_unit_id,
            item.mechanism_id,
            _enum_value(item.axis) if item.axis else "",
            _enum_value(item.zone) if item.zone else "",
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
        archetype_id=_safe_text(request.archetype_id, "invalid"),
        viewport=_safe_viewport(context),
        interaction_state=_safe_text(context.interaction_state, "invalid"),
        safe_baseline_directive=_safe_text(constraints.safe_baseline_directive, "semantic-default"),
        mechanisms=canonical_mechanisms,
        asset_decisions=canonical_assets,
        provenance=canonical_provenance,
        warnings=canonical_warnings,
        rejections=canonical_rejections,
        accessibility_applied=accessibility_applied,
        reading_sanctuary_applied=reading_sanctuary_applied,
        reduced_motion_applied=reduced_motion_applied,
    )


def _resolve_assets(units: Sequence[DNAUnit], asset_state: AssetState):
    by_slot: Dict[str, List[Tuple[DNAUnit, AssetIntent]]] = {}
    for unit in units:
        for asset in unit.assets:
            by_slot.setdefault(asset.slot, []).append((unit, asset))
    decisions: List[AssetDecision] = []
    warnings: List[ResolutionIssue] = []
    lookup: Dict[str, AssetDecision] = {}
    for slot in sorted(by_slot):
        candidates = sorted(by_slot[slot], key=lambda pair: (-pair[1].ownership_rank, pair[0].id, pair[1].asset_id))
        unit, asset = candidates[0]
        if len(candidates) > 1:
            warnings.append(ResolutionIssue(
                FailureCode.OWNERSHIP_COLLISION,
                f"Asset slot '{slot}' had {len(candidates)} owners; deterministic owner '{unit.id}' selected",
                unit.id,
            ))
        if not asset.production_eligible:
            decision = AssetDecision(slot, asset.asset_id, unit.id, "structural_fallback", asset.fallback_directive,
                                     DegradationState.ASSET_OFF_STRUCTURAL, "asset is not production-eligible")
            warnings.append(ResolutionIssue(
                FailureCode.LICENSE_SCOPE_VIOLATION,
                f"Asset '{asset.asset_id}' is not production-eligible; structural fallback applied",
                unit.id,
            ))
        elif asset_state is AssetState.AVAILABLE:
            decision = AssetDecision(slot, asset.asset_id, unit.id, "use_asset", asset.asset_id, DegradationState.FULL)
        elif asset_state is AssetState.LOADING:
            decision = AssetDecision(slot, asset.asset_id, unit.id, "safe_substitute", asset.fallback_directive,
                                     DegradationState.SAFE_SUBSTITUTE, "asset still loading")
        elif asset_state is AssetState.PARTIAL:
            decision = AssetDecision(slot, asset.asset_id, unit.id, "safe_substitute", asset.fallback_directive,
                                     DegradationState.SAFE_SUBSTITUTE, "partial asset failure")
        else:
            decision = AssetDecision(slot, asset.asset_id, unit.id, "structural_fallback", asset.fallback_directive,
                                     DegradationState.ASSET_OFF_STRUCTURAL, "asset-off mode")
        decisions.append(decision)
        lookup[slot] = decision
    return tuple(decisions), tuple(warnings), lookup


def _is_relevant(mechanism: MechanismContract, zone: SemanticZone, context: SemanticContext) -> bool:
    viewport_ok = "all" in mechanism.viewports or context.viewport.value in mechanism.viewports
    state_ok = "all" in mechanism.states or context.interaction_state in mechanism.states
    return viewport_ok and state_ok and zone in context.active_zones


def _hard_drop(*, unit, mechanism, zone, reason, warnings, provenance) -> None:
    warnings.append(ResolutionIssue(
        FailureCode.FORBIDDEN_PROJECTION, reason, unit.id, mechanism.id, mechanism.axis, zone,
    ))
    provenance.append(ProvenanceRecord(
        "demoted", unit.id, mechanism.id, mechanism.axis, zone, reason,
    ))


def _candidate_from_mechanism(
    *, unit, mechanism, zone, context, constraints, asset_lookup, warnings, rejections, provenance,
) -> _Candidate | None:
    directive = mechanism.directive
    degradation = DegradationState.FULL

    def demote_or_drop(reason: str, state: DegradationState, code: FailureCode):
        nonlocal directive, degradation
        warnings.append(ResolutionIssue(code, reason, unit.id, mechanism.id, mechanism.axis, zone))
        if mechanism.fallback_directive:
            directive = mechanism.fallback_directive
            degradation = state
            provenance.append(ProvenanceRecord("fallback", unit.id, mechanism.id, mechanism.axis, zone, reason))
            return _Candidate(unit, mechanism, zone, directive, degradation)
        provenance.append(ProvenanceRecord("demoted", unit.id, mechanism.id, mechanism.axis, zone, reason))
        return None

    if mechanism.axis in constraints.blocked_axes or mechanism.id in constraints.blocked_mechanism_ids:
        _hard_drop(unit=unit, mechanism=mechanism, zone=zone,
                   reason="runtime hard-veto blocked mechanism projection",
                   warnings=warnings, provenance=provenance)
        return None
    if mechanism.host_capability and mechanism.host_capability not in context.host_capabilities:
        return demote_or_drop(f"host capability '{mechanism.host_capability}' unavailable",
                              DegradationState.SAFE_BASELINE, FailureCode.FORBIDDEN_PROJECTION)
    if context.accessibility_required and not mechanism.accessibility_safe:
        return demote_or_drop("accessibility super-veto demoted unsafe mechanism",
                              DegradationState.ACCESSIBILITY_DEMOTED, FailureCode.FORBIDDEN_PROJECTION)
    if context.reduced_motion and mechanism.axis is Axis.MOTION_TEMPORAL:
        return demote_or_drop("reduced-motion preference demoted temporal mechanism",
                              DegradationState.ACCESSIBILITY_DEMOTED, FailureCode.FORBIDDEN_PROJECTION)
    is_reading_zone = zone is SemanticZone.U7 or zone in context.reading_heavy_zones
    if constraints.reading_sanctuary and is_reading_zone and not mechanism.reading_safe:
        return demote_or_drop("Reading Sanctuary demoted high-intensity mechanism",
                              DegradationState.READING_SANCTUARY_DEMOTED, FailureCode.FORBIDDEN_PROJECTION)
    if mechanism.requires_asset_slot:
        decision = asset_lookup.get(mechanism.requires_asset_slot)
        if decision is None:
            issue = ResolutionIssue(FailureCode.ASSET_DEPENDENCY_FAILURE,
                                    f"Required asset slot '{mechanism.requires_asset_slot}' is not declared",
                                    unit.id, mechanism.id, mechanism.axis, zone)
            if mechanism.fallback_directive:
                warnings.append(issue)
                directive = mechanism.fallback_directive
                degradation = DegradationState.ASSET_OFF_STRUCTURAL
                provenance.append(ProvenanceRecord("fallback", unit.id, mechanism.id, mechanism.axis, zone, issue.message))
            else:
                rejections.append(issue)
                provenance.append(ProvenanceRecord("rejected", unit.id, mechanism.id, mechanism.axis, zone, issue.message))
                return None
        elif decision.action != "use_asset":
            directive = mechanism.fallback_directive or decision.directive
            if not directive:
                issue = ResolutionIssue(FailureCode.ASSET_DEPENDENCY_FAILURE,
                                        f"Asset slot '{mechanism.requires_asset_slot}' degraded without structural fallback",
                                        unit.id, mechanism.id, mechanism.axis, zone)
                rejections.append(issue)
                provenance.append(ProvenanceRecord("rejected", unit.id, mechanism.id, mechanism.axis, zone, issue.message))
                return None
            degradation = decision.degradation
            provenance.append(ProvenanceRecord("fallback", unit.id, mechanism.id, mechanism.axis, zone,
                                               decision.reason or "asset degraded"))
    return _Candidate(unit, mechanism, zone, directive, degradation)


def _mechanisms_conflict(left: _Candidate, right: _Candidate) -> bool:
    if right.mechanism.id in left.mechanism.conflicts_with or left.mechanism.id in right.mechanism.conflicts_with:
        return True
    if right.unit.id in left.unit.conflicting_unit_ids or left.unit.id in right.unit.conflicting_unit_ids:
        return True
    if left.mechanism.compatible_with and right.mechanism.id not in left.mechanism.compatible_with:
        return True
    if right.mechanism.compatible_with and left.mechanism.id not in right.mechanism.compatible_with:
        return True
    if left.unit.compatible_unit_ids and right.unit.id not in left.unit.compatible_unit_ids:
        return True
    if right.unit.compatible_unit_ids and left.unit.id not in right.unit.compatible_unit_ids:
        return True
    return False


def resolve(registry: DNARegistry, request: CompositionRequest, context: SemanticContext,
            constraints: RuntimeConstraints | None = None) -> ThemeProjection:
    """Resolve canonical DNA into a deterministic host-neutral projection."""
    constraints = constraints or RuntimeConstraints()
    warnings: List[ResolutionIssue] = []
    rejections: List[ResolutionIssue] = []
    provenance: List[ProvenanceRecord] = []
    units: Tuple[DNAUnit, ...] = ()
    try:
        if not isinstance(registry, DNARegistry):
            raise TypeError("registry must be DNARegistry")
        if not isinstance(request, CompositionRequest):
            raise TypeError("request must be CompositionRequest")
        if not isinstance(context, SemanticContext):
            raise TypeError("context must be SemanticContext")
        if not isinstance(constraints, RuntimeConstraints):
            raise TypeError("constraints must be RuntimeConstraints")
        request.validate()
        context.validate()
        constraints.validate()
        units = registry.select(request)
    except (RegistryError, TypeError, ValueError) as exc:
        rejections.append(ResolutionIssue(FailureCode.UNEXPLAINABLE_COMPOSITION, str(exc)))
        return _make_projection(
            request=request if isinstance(request, CompositionRequest) else CompositionRequest("invalid"),
            context=context if isinstance(context, SemanticContext) else SemanticContext(),
            constraints=constraints if isinstance(constraints, RuntimeConstraints) else RuntimeConstraints(),
            units=(), mechanisms=(), assets=(), provenance=(), warnings=(), rejections=rejections,
            accessibility_applied=False, reading_sanctuary_applied=False, reduced_motion_applied=False,
        )

    asset_decisions, asset_warnings, asset_lookup = _resolve_assets(units, request.asset_state)
    warnings.extend(asset_warnings)
    for decision in asset_decisions:
        provenance.append(ProvenanceRecord(
            decision.action, decision.source_unit_id, f"asset:{decision.slot}", None, None,
            decision.reason or "asset resolution",
        ))

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
                accessibility_applied |= bool(context.accessibility_required and not mechanism.accessibility_safe)
                reduced_motion_applied |= bool(context.reduced_motion and mechanism.axis is Axis.MOTION_TEMPORAL)
                reading_sanctuary_applied |= bool(
                    constraints.reading_sanctuary
                    and (zone is SemanticZone.U7 or zone in context.reading_heavy_zones)
                    and not mechanism.reading_safe
                )
                candidate = _candidate_from_mechanism(
                    unit=unit, mechanism=mechanism, zone=zone, context=context, constraints=constraints,
                    asset_lookup=asset_lookup, warnings=warnings, rejections=rejections, provenance=provenance,
                )
                if candidate is not None:
                    grouped.setdefault((mechanism.axis, zone), []).append(candidate)

    resolved: List[ResolvedMechanism] = []
    contradiction_count = 0
    for key in sorted(grouped, key=lambda item: (item[0].value, item[1].value)):
        candidates = sorted(grouped[key], key=lambda item: (-item.mechanism.ownership_rank, item.unit.id, item.mechanism.id))
        winners: List[_Candidate] = []
        for candidate in candidates:
            conflicting = next((winner for winner in winners if _mechanisms_conflict(candidate, winner)), None)
            if conflicting is not None:
                contradiction_count += 1
                reason = (f"Mechanism '{candidate.mechanism.id}' conflicts with winning mechanism "
                          f"'{conflicting.mechanism.id}' on {key[0].value}/{key[1].value}")
                warnings.append(ResolutionIssue(FailureCode.OWNERSHIP_COLLISION, reason, candidate.unit.id,
                                                candidate.mechanism.id, key[0], key[1]))
                provenance.append(ProvenanceRecord("demoted", candidate.unit.id, candidate.mechanism.id,
                                                   key[0], key[1], reason))
                continue
            if len(winners) >= constraints.dominance_cap:
                reason = f"Dominance cap {constraints.dominance_cap} reached on {key[0].value}/{key[1].value}"
                warnings.append(ResolutionIssue(FailureCode.OWNERSHIP_COLLISION, reason, candidate.unit.id,
                                                candidate.mechanism.id, key[0], key[1]))
                provenance.append(ProvenanceRecord("demoted", candidate.unit.id, candidate.mechanism.id,
                                                   key[0], key[1], reason))
                continue
            winners.append(candidate)
        for winner in winners:
            resolved.append(ResolvedMechanism(
                winner.mechanism.axis, winner.zone, context.viewport, context.interaction_state,
                winner.directive, winner.unit.id, winner.mechanism.id, winner.mechanism.ownership_rank,
                winner.degradation,
            ))
            provenance.append(ProvenanceRecord("applied", winner.unit.id, winner.mechanism.id,
                                               winner.mechanism.axis, winner.zone,
                                               "deterministic ownership winner"))

    if contradiction_count > constraints.contradiction_budget:
        rejections.append(ResolutionIssue(FailureCode.CONTRADICTION_OVERFLOW,
                                          f"Contradiction count {contradiction_count} exceeds budget {constraints.contradiction_budget}"))
    if relevant_count > 0 and not resolved:
        rejections.append(ResolutionIssue(FailureCode.FALLBACK_IDENTITY_COLLAPSE,
                                          "All relevant mechanisms were removed; structural identity did not survive"))
    return _make_projection(
        request=request, context=context, constraints=constraints, units=units, mechanisms=resolved,
        assets=asset_decisions, provenance=provenance, warnings=warnings, rejections=rejections,
        accessibility_applied=accessibility_applied,
        reading_sanctuary_applied=reading_sanctuary_applied,
        reduced_motion_applied=reduced_motion_applied,
    )
