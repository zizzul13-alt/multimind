from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path

import pytest

from design_dna.asset_policy import (
    ASSET_POLICY_BY_ID,
    M12_DIRECT_IP_GATED_IDS,
    M12_ENGINE_ASSET_ON_NOT_APPLICABLE,
    M12_MK_ASSET_ON_APPLICABLE,
    M12_REFERENCE_ASSET_ON_NOT_APPLICABLE,
    M4_HISTORICAL_ASSET_SEMANTICS_REWRITTEN,
    asset_policy_ledger_payload,
    project_asset_policy,
    require_asset_policy,
)
from design_dna.fixtures import FIXTURE_ASSET_ON_APPLICABLE, FIXTURE_ASSET_ON_NOT_APPLICABLE
from design_dna.izzul import IZZUL_REFERENCE_IDS
from design_dna.miko import MIKO_REFERENCE_IDS
from design_dna.models import AssetState, UnitKind
from design_dna.primitives import M4_PRIMITIVE_IDS, primitive_asset_on_applicable
from design_dna.registry import UnknownUnitError
from design_dna.track_t import TRACK_T_I_REFERENCE_IDS

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/design-dna/migration/status/ASSET_POLICY_271.json"
M12_MODULE = ROOT / "design_dna/asset_policy.py"

EXPECTED_MK_CORRECTION = {
    "MK01", "MK04", "MK05", "MK06", "MK12", "MK13",
    "MK14", "MK16", "MK18", "MK22", "MK23", "MK25",
}


def test_canonical_policy_has_exact_271_additive_units_and_kind_census():
    assert len(ASSET_POLICY_BY_ID) == 271
    kinds = Counter(row.unit_kind for row in ASSET_POLICY_BY_ID.values())
    assert kinds == {
        UnitKind.REFERENCE: 160,
        UnitKind.ENGINE: 29,
        UnitKind.PRIMITIVE: 68,
        UnitKind.FIXTURE: 14,
    }


def test_exact_207_applicable_64_not_applicable_arithmetic():
    applicable = {unit_id for unit_id, row in ASSET_POLICY_BY_ID.items() if row.asset_applicable}
    not_applicable = set(ASSET_POLICY_BY_ID) - applicable
    assert len(applicable) == 207
    assert len(not_applicable) == 64
    assert applicable.isdisjoint(not_applicable)
    assert applicable | not_applicable == set(ASSET_POLICY_BY_ID)


def test_direct_ip_gate_is_exact_75_with_locked_owner_accounting():
    assert len(IZZUL_REFERENCE_IDS) == 36
    assert len(MIKO_REFERENCE_IDS) == 23
    assert len(TRACK_T_I_REFERENCE_IDS) == 16
    assert set(IZZUL_REFERENCE_IDS).isdisjoint(MIKO_REFERENCE_IDS)
    assert set(IZZUL_REFERENCE_IDS).isdisjoint(TRACK_T_I_REFERENCE_IDS)
    assert set(MIKO_REFERENCE_IDS).isdisjoint(TRACK_T_I_REFERENCE_IDS)
    assert M12_DIRECT_IP_GATED_IDS == {
        *IZZUL_REFERENCE_IDS,
        *MIKO_REFERENCE_IDS,
        *TRACK_T_I_REFERENCE_IDS,
    }
    assert len(M12_DIRECT_IP_GATED_IDS) == 75
    assert {unit_id for unit_id, row in ASSET_POLICY_BY_ID.items() if row.direct_ip_gated} == set(M12_DIRECT_IP_GATED_IDS)
    assert all(ASSET_POLICY_BY_ID[unit_id].asset_applicable for unit_id in M12_DIRECT_IP_GATED_IDS)


def test_exact_12_mk_final_correction_does_not_rewrite_m4_historical_semantics():
    assert M12_MK_ASSET_ON_APPLICABLE == EXPECTED_MK_CORRECTION
    assert M4_HISTORICAL_ASSET_SEMANTICS_REWRITTEN is False

    # Historical M4 behavior remains untouched for every primitive.
    assert all(primitive_asset_on_applicable(primitive_id) is False for primitive_id in M4_PRIMITIVE_IDS)

    # M12 is the only final layer that marks the twelve corrected primitives applicable.
    m12_applicable_primitives = {
        unit_id
        for unit_id, row in ASSET_POLICY_BY_ID.items()
        if row.unit_kind is UnitKind.PRIMITIVE and row.asset_applicable
    }
    assert m12_applicable_primitives == EXPECTED_MK_CORRECTION
    for primitive_id in EXPECTED_MK_CORRECTION:
        row = ASSET_POLICY_BY_ID[primitive_id]
        assert row.policy_basis == "M12_FINAL_PRIMITIVE_CORRECTION__M4_HISTORY_UNCHANGED"


def test_reference_engine_and_fixture_asset_applicability_is_exact():
    reference_na = {
        unit_id for unit_id, row in ASSET_POLICY_BY_ID.items()
        if row.unit_kind is UnitKind.REFERENCE and not row.asset_applicable
    }
    engine_na = {
        unit_id for unit_id, row in ASSET_POLICY_BY_ID.items()
        if row.unit_kind is UnitKind.ENGINE and not row.asset_applicable
    }
    fixture_applicable = {
        unit_id for unit_id, row in ASSET_POLICY_BY_ID.items()
        if row.unit_kind is UnitKind.FIXTURE and row.asset_applicable
    }
    fixture_na = {
        unit_id for unit_id, row in ASSET_POLICY_BY_ID.items()
        if row.unit_kind is UnitKind.FIXTURE and not row.asset_applicable
    }

    assert M12_REFERENCE_ASSET_ON_NOT_APPLICABLE == {"CW02"}
    assert reference_na == {"CW02"}
    assert M12_ENGINE_ASSET_ON_NOT_APPLICABLE == {"E1", "E5"}
    assert engine_na == {"E1", "E5"}
    assert fixture_applicable == set(FIXTURE_ASSET_ON_APPLICABLE)
    assert fixture_na == set(FIXTURE_ASSET_ON_NOT_APPLICABLE)
    assert len(fixture_applicable) == 9
    assert len(fixture_na) == 5


def test_all_271_rows_are_optional_structural_fallbacks_with_zero_approval():
    for row in ASSET_POLICY_BY_ID.values():
        assert row.asset_required is False
        assert row.fallback_required is True
        assert row.selected_asset is None
        assert row.final_approved is False
        assert row.rights_evidence_pointer is None
        assert row.provenance_pointer.strip()

    assert sum(row.final_approved for row in ASSET_POLICY_BY_ID.values()) == 0
    assert sum(row.selected_asset is not None for row in ASSET_POLICY_BY_ID.values()) == 0


def test_license_state_fails_closed_for_direct_ip_and_unverified_applicable_rows():
    for row in ASSET_POLICY_BY_ID.values():
        if not row.asset_applicable:
            assert row.license_status == "NOT_APPLICABLE"
        elif row.direct_ip_gated:
            assert row.license_status == "DIRECT_IP_RIGHTS_EVIDENCE_REQUIRED"
        else:
            assert row.license_status == "UNVERIFIED_NO_SELECTED_ASSET"


@pytest.mark.parametrize("asset_state", tuple(AssetState))
def test_all_271_units_survive_available_loading_partial_off_without_asset_identity_dependency(asset_state):
    for unit_id in ASSET_POLICY_BY_ID:
        projection = project_asset_policy(unit_id, asset_state)
        assert projection.unit_id == unit_id
        assert projection.asset_state is asset_state
        assert projection.structural_identity_preserved is True
        assert projection.asset_enrichment_active is False
        assert projection.fallback_active is True
        assert projection.accessibility_super_veto is True
        assert projection.reading_sanctuary_super_veto is True
        assert projection.theatricality_allowed is False
        assert projection.directive


def test_available_never_bypasses_missing_rights_evidence():
    for unit_id, row in ASSET_POLICY_BY_ID.items():
        projection = project_asset_policy(unit_id, AssetState.AVAILABLE)
        if row.asset_applicable:
            assert projection.directive == "available-without-approved-rights-evidence-use-structural-fallback"
        else:
            assert projection.directive == "asset-not-applicable-use-structural-identity"
        assert projection.asset_enrichment_active is False
        assert projection.fallback_active is True


@pytest.mark.parametrize(
    ("accessibility_required", "reading_sanctuary", "theatricality_allowed"),
    (
        (True, True, False),
        (True, False, False),
        (False, True, False),
        (False, False, True),
    ),
)
def test_accessibility_and_reading_sanctuary_are_independent_super_vetoes(
    accessibility_required, reading_sanctuary, theatricality_allowed
):
    projection = project_asset_policy(
        "MK01",
        AssetState.AVAILABLE,
        accessibility_required=accessibility_required,
        reading_sanctuary=reading_sanctuary,
    )
    assert projection.accessibility_super_veto is accessibility_required
    assert projection.reading_sanctuary_super_veto is reading_sanctuary
    assert projection.theatricality_allowed is theatricality_allowed
    assert projection.structural_identity_preserved is True
    assert projection.asset_enrichment_active is False


def test_checked_in_271_entry_ledger_is_exact_runtime_projection():
    payload = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert payload == asset_policy_ledger_payload()
    assert payload["unit_count"] == 271
    assert len(payload["records"]) == 271
    assert payload["asset_applicable_count"] == 207
    assert payload["asset_not_applicable_count"] == 64
    assert payload["direct_ip_gated_count"] == 75
    assert payload["final_approved_count"] == 0
    assert payload["m4_historical_asset_semantics_rewritten"] is False


def test_asset_policy_runtime_stays_private_candidate_host_neutral():
    tree = ast.parse(M12_MODULE.read_text(encoding="utf-8"), filename=str(M12_MODULE))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)

    forbidden_prefixes = ("core", "providers", "database", "ui.dna", "ui.theme_studio")
    assert all(
        not any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden_prefixes)
        for name in imports
    )


def test_unknown_unit_and_invalid_asset_state_fail_explicitly():
    with pytest.raises(UnknownUnitError):
        require_asset_policy("F11")
    with pytest.raises(UnknownUnitError):
        project_asset_policy("NOT_A_UNIT", AssetState.OFF)
    with pytest.raises(TypeError):
        project_asset_policy("MK01", "off")
