"""Optional public bridge for the canonical private Design-DNA runtime.

This module is intentionally presentation-safe and import-safe when the private
package is absent or incompatible. No private Design-DNA type crosses this
boundary; Reflex and other public hosts receive frozen scalar projections only.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
import logging
from typing import Optional


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CanonicalReferenceOption:
    id: str
    display_name: str
    family: str
    category: str
    lineage: str


@dataclass(frozen=True)
class CanonicalMechanismProjection:
    axis: str
    zone: str
    directive: str
    source_unit_id: str
    mechanism_id: str
    ownership_rank: int
    degradation: str


@dataclass(frozen=True)
class CanonicalPresentationProjection:
    reference: CanonicalReferenceOption
    composition_id: str
    fingerprint: str
    archetype_id: str
    viewport: str
    interaction_state: str
    primitive_ids: tuple[str, ...]
    mechanisms: tuple[CanonicalMechanismProjection, ...]
    asset_decisions: tuple[dict[str, str], ...]
    provenance: tuple[dict[str, str], ...]
    warnings: tuple[dict[str, str], ...]
    rejections: tuple[dict[str, str], ...]
    accessibility_applied: bool
    reading_sanctuary_applied: bool
    reduced_motion_applied: bool

    @property
    def is_valid(self) -> bool:
        return not self.rejections


@dataclass(frozen=True)
class CanonicalHostRealizationPlan:
    """Renderer-neutral typed plan safe to expose to public presentation hosts."""

    reference_id: str
    display_name: str
    source_fingerprint: str
    viewport: str
    archetype_id: str
    layout_flow: str
    balance: str
    density: str
    hierarchy: str
    continuity: str
    motion: str
    typography: str
    mobile_strategy: str
    active_axes: tuple[str, ...]
    active_zones: tuple[str, ...]
    degraded_mechanism_count: int
    accessibility_applied: bool
    reading_sanctuary_applied: bool
    reduced_motion_applied: bool


def _warn(operation: str, exc: Exception) -> None:
    logger.warning("Optional canonical Design-DNA %s failed; keeping safe presentation: %s", operation, exc)


def _optional_import(module_name: str):
    try:
        return import_module(module_name)
    except Exception as exc:
        _warn(f"import {module_name}", exc)
        return None


def _enum_value(value) -> str:
    return str(getattr(value, "value", value))


def canonical_dna_available() -> bool:
    """Return whether the canonical private host facade can be loaded."""
    return _optional_import("design_dna.host_runtime") is not None


def list_canonical_reference_options() -> tuple[CanonicalReferenceOption, ...]:
    """Return the canonical user-facing REFERENCE catalog, or empty on failure."""
    module = _optional_import("design_dna.host_runtime")
    if module is None:
        return ()
    try:
        result = []
        for option in module.list_reference_options():
            result.append(
                CanonicalReferenceOption(
                    id=str(option.id),
                    display_name=str(option.display_name),
                    family=str(option.family),
                    category=str(option.category),
                    lineage=str(option.lineage),
                )
            )
        return tuple(result)
    except Exception as exc:
        _warn("reference catalog", exc)
        return ()


def list_host_realizable_reference_ids() -> tuple[str, ...]:
    """Return references implemented by the current typed EQ4 host realizer."""
    module = _optional_import("design_dna.host_realization")
    if module is None:
        return ()
    try:
        return tuple(str(item) for item in module.list_host_realizable_reference_ids())
    except Exception as exc:
        _warn("host-realizable catalog", exc)
        return ()


def _issue_snapshot(issue) -> dict[str, str]:
    return {
        "code": _enum_value(getattr(issue, "code", "")),
        "message": str(getattr(issue, "message", "")),
        "source_unit_id": str(getattr(issue, "source_unit_id", "")),
        "mechanism_id": str(getattr(issue, "mechanism_id", "")),
        "axis": _enum_value(getattr(issue, "axis", "")) if getattr(issue, "axis", None) else "",
        "zone": _enum_value(getattr(issue, "zone", "")) if getattr(issue, "zone", None) else "",
    }


def _provenance_snapshot(record) -> dict[str, str]:
    return {
        "action": str(getattr(record, "action", "")),
        "source_unit_id": str(getattr(record, "source_unit_id", "")),
        "mechanism_id": str(getattr(record, "mechanism_id", "")),
        "axis": _enum_value(getattr(record, "axis", "")) if getattr(record, "axis", None) else "",
        "zone": _enum_value(getattr(record, "zone", "")) if getattr(record, "zone", None) else "",
        "reason": str(getattr(record, "reason", "")),
    }


def _asset_snapshot(decision) -> dict[str, str]:
    return {
        "slot": str(getattr(decision, "slot", "")),
        "asset_id": str(getattr(decision, "asset_id", "")),
        "source_unit_id": str(getattr(decision, "source_unit_id", "")),
        "action": str(getattr(decision, "action", "")),
        "directive": str(getattr(decision, "directive", "")),
        "degradation": _enum_value(getattr(decision, "degradation", "")),
        "reason": str(getattr(decision, "reason", "")),
    }


def _private_resolve(
    reference_id: str,
    *,
    viewport: str,
    asset_state: str,
    archetype_id: str,
    interaction_state: str,
    reduced_motion: bool,
    accessibility_required: bool,
    language: str,
    script: str,
    host_capabilities: tuple[str, ...],
):
    runtime = _optional_import("design_dna.host_runtime")
    models = _optional_import("design_dna.models")
    if runtime is None or models is None:
        return None
    return runtime.resolve_reference(
        str(reference_id),
        viewport=models.Viewport(str(viewport)),
        asset_state=models.AssetState(str(asset_state)),
        archetype_id=str(archetype_id),
        interaction_state=str(interaction_state),
        reduced_motion=bool(reduced_motion),
        accessibility_required=bool(accessibility_required),
        language=str(language),
        script=str(script),
        host_capabilities=tuple(str(item) for item in host_capabilities),
    )


def resolve_canonical_reference(
    reference_id: str,
    *,
    viewport: str = "desktop",
    asset_state: str = "off",
    archetype_id: str = "chat_first",
    interaction_state: str = "default",
    reduced_motion: bool = False,
    accessibility_required: bool = True,
    language: str = "",
    script: str = "",
    host_capabilities: tuple[str, ...] = (),
) -> Optional[CanonicalPresentationProjection]:
    """Resolve one canonical reference and strip all private implementation types."""
    try:
        resolved = _private_resolve(
            reference_id,
            viewport=viewport,
            asset_state=asset_state,
            archetype_id=archetype_id,
            interaction_state=interaction_state,
            reduced_motion=reduced_motion,
            accessibility_required=accessibility_required,
            language=language,
            script=script,
            host_capabilities=host_capabilities,
        )
        if resolved is None:
            return None
        projection = resolved.projection
        reference = CanonicalReferenceOption(
            id=str(resolved.reference.id),
            display_name=str(resolved.reference.display_name),
            family=str(resolved.reference.family),
            category=str(resolved.reference.category),
            lineage=str(resolved.reference.lineage),
        )
        mechanisms = tuple(
            CanonicalMechanismProjection(
                axis=_enum_value(item.axis),
                zone=_enum_value(item.zone),
                directive=str(item.directive),
                source_unit_id=str(item.source_unit_id),
                mechanism_id=str(item.mechanism_id),
                ownership_rank=int(item.ownership_rank),
                degradation=_enum_value(item.degradation),
            )
            for item in projection.mechanisms
        )
        return CanonicalPresentationProjection(
            reference=reference,
            composition_id=str(projection.composition_id),
            fingerprint=str(projection.fingerprint),
            archetype_id=str(projection.archetype_id),
            viewport=_enum_value(projection.viewport),
            interaction_state=str(projection.interaction_state),
            primitive_ids=tuple(str(item) for item in resolved.primitive_ids),
            mechanisms=mechanisms,
            asset_decisions=tuple(_asset_snapshot(item) for item in projection.asset_decisions),
            provenance=tuple(_provenance_snapshot(item) for item in projection.provenance),
            warnings=tuple(_issue_snapshot(item) for item in projection.warnings),
            rejections=tuple(_issue_snapshot(item) for item in projection.rejections),
            accessibility_applied=bool(projection.accessibility_applied),
            reading_sanctuary_applied=bool(projection.reading_sanctuary_applied),
            reduced_motion_applied=bool(projection.reduced_motion_applied),
        )
    except Exception as exc:
        _warn("reference resolution", exc)
        return None


def realize_canonical_reference(
    reference_id: str,
    *,
    viewport: str = "desktop",
    asset_state: str = "off",
    archetype_id: str = "chat_first",
    interaction_state: str = "default",
    reduced_motion: bool = False,
    accessibility_required: bool = True,
    language: str = "",
    script: str = "",
    host_capabilities: tuple[str, ...] = (),
) -> Optional[CanonicalHostRealizationPlan]:
    """Resolve and translate an EQ4-proving reference into typed host vocabulary."""
    realizer = _optional_import("design_dna.host_realization")
    if realizer is None:
        return None
    try:
        resolved = _private_resolve(
            reference_id,
            viewport=viewport,
            asset_state=asset_state,
            archetype_id=archetype_id,
            interaction_state=interaction_state,
            reduced_motion=reduced_motion,
            accessibility_required=accessibility_required,
            language=language,
            script=script,
            host_capabilities=host_capabilities,
        )
        if resolved is None:
            return None
        plan = realizer.realize_for_host(resolved)
        profile = plan.profile
        return CanonicalHostRealizationPlan(
            reference_id=str(plan.reference_id),
            display_name=str(plan.display_name),
            source_fingerprint=str(plan.source_fingerprint),
            viewport=str(plan.viewport),
            archetype_id=str(plan.archetype_id),
            layout_flow=_enum_value(profile.layout_flow),
            balance=_enum_value(profile.balance),
            density=_enum_value(profile.density),
            hierarchy=_enum_value(profile.hierarchy),
            continuity=_enum_value(profile.continuity),
            motion=_enum_value(profile.motion),
            typography=_enum_value(profile.typography),
            mobile_strategy=_enum_value(profile.mobile_strategy),
            active_axes=tuple(str(item) for item in plan.active_axes),
            active_zones=tuple(str(item) for item in plan.active_zones),
            degraded_mechanism_count=int(plan.degraded_mechanism_count),
            accessibility_applied=bool(plan.accessibility_applied),
            reading_sanctuary_applied=bool(plan.reading_sanctuary_applied),
            reduced_motion_applied=bool(plan.reduced_motion_applied),
        )
    except Exception as exc:
        _warn("host realization", exc)
        return None


__all__ = [
    "CanonicalHostRealizationPlan",
    "CanonicalMechanismProjection",
    "CanonicalPresentationProjection",
    "CanonicalReferenceOption",
    "canonical_dna_available",
    "list_canonical_reference_options",
    "list_host_realizable_reference_ids",
    "realize_canonical_reference",
    "resolve_canonical_reference",
]
