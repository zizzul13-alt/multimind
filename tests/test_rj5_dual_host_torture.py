from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "app.py").read_text(encoding="utf-8")
REFLEX_STATE = (ROOT / "multimind_reflex" / "state.py").read_text(encoding="utf-8")
REFLEX_SURFACE = (ROOT / "multimind_reflex" / "multimind_reflex.py").read_text(encoding="utf-8")
BRIDGE = (ROOT / "ui" / "dna_bridge.py").read_text(encoding="utf-8")


def test_a_b_a_application_truth_torture(tmp_path):
    probe = ROOT / "scripts" / "rj5_dual_host_torture.py"
    subprocess.run(
        [sys.executable, str(probe), str(tmp_path / "users" / "shared.db")],
        cwd=ROOT,
        check=True,
    )


def test_both_hosts_use_shared_application_composition():
    assert "build_application_for_user(" in APP
    assert "build_host_application" in REFLEX_STATE
    assert "application.execute_chat" in REFLEX_STATE
    assert "application.list_sessions" in APP or ".list_sessions()" in APP
    assert "sqlite3" not in REFLEX_STATE


def test_both_hosts_keep_session_history_and_restore_through_application():
    assert ".get_session_chats(" in APP
    assert ".restore_database(" in APP
    assert "self._application().restore_database" in REFLEX_STATE
    assert "self._application().export_database()" in REFLEX_STATE


def test_private_dna_is_optional_at_both_host_edges():
    assert "from ui.dna_bridge import" in APP
    assert "from ui.dna_bridge import" in REFLEX_STATE
    assert "design_dna" not in REFLEX_STATE
    assert "dna_quarantine" not in REFLEX_STATE
    assert "Optional Design-DNA" in BRIDGE


def test_streamlit_remains_reference_and_reflex_keeps_theme_studio_contract():
    assert "render_theme_studio_surface" in APP
    assert "Theme Studio" in REFLEX_SURFACE
    assert "Apply Composition" in REFLEX_SURFACE
    assert "Back to workspace" in REFLEX_SURFACE


def test_reflex_surface_has_responsive_breakpoints_without_pixel_parity_claim():
    assert "rx.breakpoints" in REFLEX_SURFACE
    assert 'initial="1"' in REFLEX_SURFACE
    assert 'lg="3fr 7fr"' in REFLEX_SURFACE


def test_no_transport_layer_or_second_persistence_owner_was_added_to_hosts():
    combined = APP + REFLEX_STATE + REFLEX_SURFACE
    for forbidden in ("FastAPI", "requests.post(", "httpx.post(", "sqlite3.connect("):
        assert forbidden not in combined
