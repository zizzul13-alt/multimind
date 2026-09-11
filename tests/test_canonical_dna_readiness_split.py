import inspect

import multimind_reflex.canonical_dna_state as state
import ui.canonical_dna_bridge as bridge


def test_public_bridge_exposes_host_readiness_and_browser_proving_separately():
    source = inspect.getsource(bridge)
    assert "def list_host_realizable_reference_ids" in source
    assert "def list_browser_proving_reference_ids" in source
    assert "list_browser_proving_reference_ids" in bridge.__all__


def test_catalog_status_never_equates_generic_host_readiness_with_eq4_credit():
    source = inspect.getsource(state)
    assert '"EQ4 browser-proving slice"' in source
    assert '"Host-realizable · browser evidence pending"' in source
    assert '"Canonical · host realization pending"' in source
    assert '"host_ready"' in source
    assert '"proving"' in source
    assert "browser evidence and EQ4 credit remain pending" in source


def test_only_host_realizable_entries_can_render_but_non_proving_entries_are_allowed():
    source = inspect.getsource(state.CanonicalDnaState)
    assert 'selected.get("host_ready") != "true"' in source
    assert 'selected.get("proving") == "true"' in source
    assert "Only a host-realizable canonical plan" in source


def test_public_bridge_remains_safe_when_old_private_package_has_no_proving_api(monkeypatch):
    class OldRealizer:
        @staticmethod
        def list_host_realizable_reference_ids():
            return ("CW01",)

    monkeypatch.setattr(bridge, "_optional_import", lambda name: OldRealizer if name == "design_dna.host_realization" else None)
    assert bridge.list_host_realizable_reference_ids() == ("CW01",)
    assert bridge.list_browser_proving_reference_ids() == ()
