from pathlib import Path

import yaml


def test_step7_acceptance_waits_only_for_step5_economics():
    data = yaml.safe_load(
        Path("docs/governance/STEP7_ACCEPTANCE.yaml").read_text(encoding="utf-8")
    )

    assert data["step"] == 7
    assert data["acceptance"] == {
        "topology_freeze": "PASS",
        "repository_contract": "PASS",
        "runtime_evidence_reconciled": "PASS",
        "final_environment_acceptance": "WAITING_ONLY_STEP5_ECONOMICS",
    }
    assert data["remaining_dependency"]["step"] == 5
    assert data["remaining_dependency"]["steady_state_economics"] == "PENDING"
    assert data["cutover"]["authorized"] is False
