from pathlib import Path

import yaml


FREEZE = Path("docs/governance/STEP7_ENVIRONMENT_FREEZE.yaml")


def test_step7_freeze_is_machine_readable_and_cutover_stays_closed():
    data = yaml.safe_load(FREEZE.read_text(encoding="utf-8"))

    assert data["step"] == 7
    assert data["production_cutover_authorized"] is False
    assert data["candidate"]["host"] == "railway"
    assert data["candidate"]["presentation"] == "reflex"
    assert data["candidate"]["application_boundary"] == "MultiMindApplication"
    assert data["candidate"]["authoritative_persistence"] == "turso"
    assert data["step7"]["topology_freeze"] == "PASS"
    assert data["step7"]["runtime_evidence_reconciled"] == "PASS"
    assert data["step7"]["final_environment_acceptance"] == "WAITING_ONLY_STEP5_ECONOMICS"
    assert data["step5"]["steady_state_economics"] == "PENDING"
    assert data["locks"]["production_cutover_authorized"] is False
