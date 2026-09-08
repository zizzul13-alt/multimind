#!/usr/bin/env python3
from pathlib import Path

import yaml


path = Path("docs/governance/STEP7_ENVIRONMENT_FREEZE.yaml")
data = yaml.safe_load(path.read_text(encoding="utf-8"))

assert data["step"] == 7
assert data["production_cutover_authorized"] is False
assert data["step7"]["topology_freeze"] == "PASS"
assert data["step7"]["runtime_evidence_reconciled"] == "PASS"
assert data["step7"]["final_environment_acceptance"] == "WAITING_ONLY_STEP5_ECONOMICS"
assert data["step5"]["steady_state_economics"] == "PENDING"
assert data["locks"]["production_cutover_authorized"] is False

print("STEP7_ENVIRONMENT_FREEZE_CHECK=PASS")
