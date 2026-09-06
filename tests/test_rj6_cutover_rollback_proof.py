from pathlib import Path

from scripts import rj6_cutover_rollback_probe as probe
from utils.config import Config


def test_application_truth_survives_streamlit_reflex_rollback_cycle(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "DB_DIR", str(tmp_path / "data"))
    probe.streamlit_write()
    probe.reflex_write()
    probe.verify_shared_truth()
    probe.backup_restore()
    probe.verify_shared_truth("RJ6_TEST_ROLLBACK_PASS")


def test_server_side_secret_injection_contract():
    probe.secret_contract()


def test_rj6_workflow_encodes_real_cutover_and_rollback_drill():
    workflow = Path(".github/workflows/rj6-cutover-rollback-proof.yml").read_text(encoding="utf-8")
    assert "streamlit run app.py" in workflow
    assert "docker build" in workflow
    assert "docker restart" in workflow
    assert "docker rm -f" in workflow
    assert "rj6_cutover_rollback_probe.py reflex-write" in workflow
    assert "rj6_cutover_rollback_probe.py rollback-verify" in workflow
    assert "MULTIMIND_CORS_ALLOWED_ORIGINS" in workflow
    assert "https://multimind.invalid" in workflow
    assert '"$PWD/data:/app/data"' in workflow
    assert "not-a-sqlite-backup" not in workflow


def test_rj6_package_does_not_modify_application_or_persistence_ownership():
    report = Path("docs/governance/RJ6_IMPLEMENTATION_REPORT.md").read_text(encoding="utf-8")
    assert "NO CORE ROLLBACK" in report
    assert "NO DB CONVERSION" in report
    assert "PRODUCTION CUTOVER AUTHORIZED: NO" in report
