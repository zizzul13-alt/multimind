"""Q3 governance-state guards before Governor acceptance."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_q3_manifest_records_implemented_pending_acceptance_without_false_closure():
    text = (ROOT / "docs/design-dna/quarantine/DNA_QUARANTINE_MANIFEST.yaml").read_text(encoding="utf-8")
    assert "Q3_theme_bridge_decoupling:\n    status: IMPLEMENTED_PENDING_ACCEPTANCE" in text
    assert "public_bridge: ui/dna_bridge.py" in text
    assert "ONE_PUBLIC_BRIDGE_OWNS_ALL_PRIVATE_DNA_IMPORTS" in text
    assert "APP_BRAND_AND_THEME_REGISTRY_HAVE_ZERO_DEEP_DNA_IMPORTS" in text
    assert "Q4_REMAINS_OWNER_OF_PHYSICAL_PRIVATE_PACKAGE_ABSENCE_PROOF" in text
    assert "Q4_private_repository_cut:\n    status: NOT_STARTED" in text


def test_q3_report_preserves_gate_boundaries_and_no_eq4_claim():
    text = (ROOT / "docs/design-dna/quarantine/Q3_IMPLEMENTATION_REPORT.md").read_text(encoding="utf-8")
    assert "IMPLEMENTED / PENDING GOVERNOR ACCEPTANCE" in text
    assert "ui/dna_bridge.py" in text
    assert "Q4 physical private-package absence proof" in text
    assert "M11 fixture implementation" in text
    assert "EQ4 credit" in text
    assert "RJ3 start" in text
    assert "production cutover" in text
