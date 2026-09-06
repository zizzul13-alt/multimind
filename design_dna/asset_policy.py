"""M12 final per-unit Design-DNA asset-policy reconciliation.

This module is the canonical final asset-policy layer for the additive 271-unit
runtime census.  It deliberately does not rewrite historical batch semantics:
in particular, M4's primitive_asset_on_applicable() remains unchanged.  The 12
primitive corrections below apply only to the final M12 policy ledger.

Assets are optional enrichment.  Structural identity, accessibility and Reading
Sanctuary remain valid when assets are unavailable, loading, partial, off, or
unapproved.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Optional, Tuple

from design_dna.country_web import register_country_web_references
from design_dna.cultural import register_cultural_tier_s
from design_dna.cultural_tier_a import register_cultural_tier_a
from design_dna.cultural_tier_b import register_cultural_tier_b
from design_dna.engines import register_m1_engines
from design_dna.fixtures import (
    FIXTURE_ASSET_ON_APPLICABLE,
    FIXTURE_ASSET_ON_NOT_APPLICABLE,
    register_m11_fixtures,
)
from design_dna.izzul import IZZUL_REFERENCE_IDS, register_m5_izzul_references
from design_dna.miko import MIKO_REFERENCE_IDS, register_m6_miko_references
from design_dna.models import AssetState, DNAUnit, UnitKind
from design_dna.primitives import register_m4_primitives
from design_dna.registry import DNARegistry, UnknownUnitError
from design_dna.track_m_r import register_track_m_r
from design_dna.track_t import TRACK_T_I_REFERENCE_IDS, register_m7_track_t_i_references


M12_REFERENCE_ASSET_ON_NOT_APPLICABLE = frozenset({"CW02"})
M12_ENGINE_ASSET_ON_NOT_APPLICABLE = frozenset({"E1", "E5"})
M12_MK_ASSET_ON_APPLICABLE = frozenset({
    "MK01", "MK04", "MK05", "MK06", "MK12", "MK13",
    "MK14", "MK16", "MK18", "MK22", "MK23", "MK25",
})
M12_DIRECT_IP_GATED_IDS = frozenset({
    *IZZUL_REFERENCE_IDS,
    *MIKO_REFERENCE_IDS,
    *TRACK_T_I_REFERENCE_IDS,
})
M4_HISTORICAL_ASSET_SEMANTICS_REWRITTEN = False


@dataclass(frozen=True)
class AssetPolicyRecord:
    """One immutable final M12 policy row for one additive DNA unit."""

    unit_id: str
    unit_kind: UnitKind
    family: str
    asset_applicable: bool
    asset_required: bool
    direct_ip_gated: bool
    selected_asset: Optional[str]
    license_status: str
    provenance_pointer: str
    fallback_required: bool
    final_approved: bool
    rights_evidence_pointer: Optional[str]
    policy_basis: str


@dataclass(frozen=True)
class AssetPolicyProjection:
    """Asset-state torture result independent of presentation host."""

    unit_id: str
    asset_state: AssetState
    structural_identity_preserved: bool
    asset_enrichment_active: bool
    fallback_active: bool
    accessibility_super_veto: bool
    reading_sanctuary_super_veto: bool
    theatricality_allowed: bool
    directive: str


def _canonical_registry() -> DNARegistry:
    """Build the same additive 271-unit census proven by M11."""

    registry = DNARegistry()
    register_m1_engines(registry)
    register_country_web_references(registry)
    register_cultural_tier_s(registry)
    register_cultural_tier_a(registry)
    register_m4_primitives(registry)
    register_m5_izzul_references(registry)
    register_m6_miko_references(registry)
    register_m7_track_t_i_references(registry)
    register_cultural_tier_b(registry)
    register_track_m_r(registry)
    register_m11_fixtures(registry)
    return registry


def _asset_applicable(unit: DNAUnit) -> bool:
    if unit.kind is UnitKind.REFERENCE:
        return unit.id not in M12_REFERENCE_ASSET_ON_NOT_APPLICABLE
    if unit.kind is UnitKind.ENGINE:
        return unit.id not in M12_ENGINE_ASSET_ON_NOT_APPLICABLE
    if unit.kind is UnitKind.PRIMITIVE:
        return unit.id in M12_MK_ASSET_ON_APPLICABLE
    if unit.kind is UnitKind.FIXTURE:
        if unit.id in FIXTURE_ASSET_ON_APPLICABLE:
            return True
        if unit.id in FIXTURE_ASSET_ON_NOT_APPLICABLE:
            return False
        raise AssertionError(f"fixture asset policy missing for {unit.id}")
    raise AssertionError(f"unsupported DNA unit kind: {unit.kind!r}")


def _policy_basis(unit: DNAUnit) -> str:
    if unit.kind is UnitKind.PRIMITIVE and unit.id in M12_MK_ASSET_ON_APPLICABLE:
        return "M12_FINAL_PRIMITIVE_CORRECTION__M4_HISTORY_UNCHANGED"
    return "M12_FINAL_RECONCILIATION_FROM_CANONICAL_RUNTIME"


def _license_status(*, applicable: bool, direct_ip_gated: bool) -> str:
    if not applicable:
        return "NOT_APPLICABLE"
    if direct_ip_gated:
        return "DIRECT_IP_RIGHTS_EVIDENCE_REQUIRED"
    return "UNVERIFIED_NO_SELECTED_ASSET"


def _build_asset_policy() -> Mapping[str, AssetPolicyRecord]:
    registry = _canonical_registry()
    units = registry.list_units()
    if len(units) != 271:
        raise AssertionError(f"M12 requires exact 271-unit census, got {len(units)}")

    rows = {}
    for unit in units:
        applicable = _asset_applicable(unit)
        direct_ip_gated = unit.id in M12_DIRECT_IP_GATED_IDS
        rows[unit.id] = AssetPolicyRecord(
            unit_id=unit.id,
            unit_kind=unit.kind,
            family=unit.family,
            asset_applicable=applicable,
            asset_required=False,
            direct_ip_gated=direct_ip_gated,
            selected_asset=None,
            license_status=_license_status(
                applicable=applicable,
                direct_ip_gated=direct_ip_gated,
            ),
            provenance_pointer=unit.provenance_pointer,
            fallback_required=True,
            final_approved=False,
            rights_evidence_pointer=None,
            policy_basis=_policy_basis(unit),
        )

    applicable_count = sum(row.asset_applicable for row in rows.values())
    direct_ip_count = sum(row.direct_ip_gated for row in rows.values())
    if applicable_count != 207:
        raise AssertionError(f"M12 requires exact 207 asset-applicable units, got {applicable_count}")
    if len(rows) - applicable_count != 64:
        raise AssertionError("M12 requires exact 64 asset-N/A units")
    if direct_ip_count != 75:
        raise AssertionError(f"M12 requires exact 75 direct-IP gated units, got {direct_ip_count}")
    return MappingProxyType(rows)


ASSET_POLICY_BY_ID: Mapping[str, AssetPolicyRecord] = _build_asset_policy()


def require_asset_policy(unit_id: str) -> AssetPolicyRecord:
    if not isinstance(unit_id, str) or not unit_id.strip():
        raise UnknownUnitError(f"Unknown DNA unit '{unit_id}'")
    try:
        return ASSET_POLICY_BY_ID[unit_id.strip()]
    except KeyError as exc:
        raise UnknownUnitError(f"Unknown DNA unit '{unit_id}'") from exc


def project_asset_policy(
    unit_id: str,
    asset_state: AssetState,
    *,
    accessibility_required: bool = True,
    reading_sanctuary: bool = True,
) -> AssetPolicyProjection:
    """Project one policy through the four asset states without identity loss.

    No current M12 row has a selected asset or rights evidence, so AVAILABLE is
    intentionally not equivalent to approved-for-use.  The structural fallback
    remains active until a future, separately governed rights-evidence change.
    """

    if not isinstance(asset_state, AssetState):
        raise TypeError("asset_state must be AssetState")
    record = require_asset_policy(unit_id)
    approved_asset_available = bool(
        record.asset_applicable
        and asset_state is AssetState.AVAILABLE
        and record.final_approved
        and record.selected_asset
        and record.rights_evidence_pointer
    )

    if not record.asset_applicable:
        directive = "asset-not-applicable-use-structural-identity"
    elif asset_state is AssetState.AVAILABLE:
        directive = "available-without-approved-rights-evidence-use-structural-fallback"
    elif asset_state is AssetState.LOADING:
        directive = "loading-use-structural-fallback"
    elif asset_state is AssetState.PARTIAL:
        directive = "partial-use-structural-fallback"
    else:
        directive = "asset-off-use-structural-fallback"

    theatricality_allowed = not (accessibility_required or reading_sanctuary)
    return AssetPolicyProjection(
        unit_id=record.unit_id,
        asset_state=asset_state,
        structural_identity_preserved=True,
        asset_enrichment_active=approved_asset_available,
        fallback_active=not approved_asset_available,
        accessibility_super_veto=bool(accessibility_required),
        reading_sanctuary_super_veto=bool(reading_sanctuary),
        theatricality_allowed=theatricality_allowed,
        directive=directive,
    )


def asset_policy_ledger_rows() -> Tuple[dict, ...]:
    """Return deterministic JSON-serializable rows for the checked-in ledger."""

    return tuple(
        {
            "unit_id": row.unit_id,
            "unit_kind": row.unit_kind.value,
            "family": row.family,
            "asset_applicable": row.asset_applicable,
            "asset_required": row.asset_required,
            "direct_ip_gated": row.direct_ip_gated,
            "selected_asset": row.selected_asset,
            "license_status": row.license_status,
            "provenance_pointer": row.provenance_pointer,
            "fallback_required": row.fallback_required,
            "final_approved": row.final_approved,
            "rights_evidence_pointer": row.rights_evidence_pointer,
            "policy_basis": row.policy_basis,
        }
        for row in ASSET_POLICY_BY_ID.values()
    )


def asset_policy_ledger_payload() -> dict:
    rows = asset_policy_ledger_rows()
    return {
        "schema_version": 1,
        "batch": "M12",
        "canonical_runtime": "design_dna.asset_policy.ASSET_POLICY_BY_ID",
        "unit_count": len(rows),
        "asset_applicable_count": sum(row["asset_applicable"] for row in rows),
        "asset_not_applicable_count": sum(not row["asset_applicable"] for row in rows),
        "direct_ip_gated_count": sum(row["direct_ip_gated"] for row in rows),
        "final_approved_count": sum(row["final_approved"] for row in rows),
        "m4_historical_asset_semantics_rewritten": M4_HISTORICAL_ASSET_SEMANTICS_REWRITTEN,
        "records": list(rows),
    }
