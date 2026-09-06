from pathlib import Path
import sqlite3
import subprocess
import sys

from database.manager import DatabaseManager, validate_restore_candidate


ROOT = Path(__file__).resolve().parents[1]


def test_export_bytes_is_valid_consistent_sqlite_snapshot(tmp_path):
    db_path = tmp_path / "live.db"
    db = DatabaseManager(str(db_path))
    db.create_session("s1", "snapshot", "coding")
    snapshot = db.export_bytes()

    restored = tmp_path / "snapshot.db"
    restored.write_bytes(snapshot)
    validate_restore_candidate(restored)
    conn = sqlite3.connect(restored)
    try:
        assert conn.execute("SELECT name FROM sessions WHERE id='s1'").fetchone()[0] == "snapshot"
    finally:
        conn.close()


def test_two_process_recreation_keeps_same_sqlite_state(tmp_path):
    db_path = tmp_path / "volume" / "users" / "probe.db"
    probe = ROOT / "scripts" / "rj4_persistence_probe.py"
    subprocess.run([sys.executable, str(probe), "seed", str(db_path)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(probe), "verify", str(db_path)], cwd=ROOT, check=True)


def test_deployment_files_preserve_single_service_and_host_managed_durability():
    compose = (ROOT / "compose.yml").read_text(encoding="utf-8")
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "multimind-data:/app/data" in compose
    assert "restart: unless-stopped" in compose
    assert compose.count("  multimind:") == 1
    assert 'VOLUME ["/app/data"]' not in dockerfile
    assert "mkdir -p /app/data/users /app/data/shared" in dockerfile
    assert 'CMD ["reflex", "run", "--env", "prod"]' in dockerfile


def test_neutral_base_compose_has_no_private_secret_requirement():
    compose = (ROOT / "compose.yml").read_text(encoding="utf-8")
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "github_token" not in compose
    assert "INSTALL_PRIVATE_DNA" not in compose
    assert "github_token" not in dockerfile
    assert "GITHUB_TOKEN" not in dockerfile

    override = (ROOT / "compose.private-dna.yml").read_text(encoding="utf-8")
    assert "dockerfile: Dockerfile.private-dna" in override
    assert "github_token" in override
    assert "INSTALL_PRIVATE_DNA" not in override


def test_private_dna_build_secret_is_not_persisted_as_build_arg():
    dockerfile = (ROOT / "Dockerfile.private-dna").read_text(encoding="utf-8")
    assert "--mount=type=secret,id=github_token" in dockerfile
    assert "required=true" in dockerfile
    assert "ARG GITHUB_TOKEN" not in dockerfile
    assert "ENV GITHUB_TOKEN" not in dockerfile
    assert "rm -rf /tmp/private-dna" in dockerfile
    assert 'VOLUME ["/app/data"]' not in dockerfile


def test_cors_defaults_are_restricted_not_wildcard():
    rxconfig = (ROOT / "rxconfig.py").read_text(encoding="utf-8")
    assert "cors_allowed_origins" in rxconfig
    assert '"http://localhost:3000"' in rxconfig
    assert '"*"' not in rxconfig


def test_no_database_schema_migration_is_added():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    private_dockerfile = (ROOT / "Dockerfile.private-dna").read_text(encoding="utf-8")
    compose = (ROOT / "compose.yml").read_text(encoding="utf-8")
    assert "alembic upgrade" not in dockerfile + private_dockerfile + compose
    assert "postgres" not in (dockerfile + private_dockerfile + compose).lower()
