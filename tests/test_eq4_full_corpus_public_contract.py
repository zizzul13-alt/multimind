from types import SimpleNamespace

import multimind_reflex.canonical_dna_state as state_module
import ui.canonical_dna_bridge as bridge


def _option(reference_id: str):
    return bridge.CanonicalReferenceOption(
        id=reference_id,
        display_name=f"Reference {reference_id}",
        family="fixture-family",
        category="fixture-category",
        lineage="fixture-lineage",
    )


def test_public_bridge_separates_host_realizable_from_browser_proving(monkeypatch):
    fake = SimpleNamespace(
        list_host_realizable_reference_ids=lambda: ("A", "B", "C"),
        list_browser_proving_reference_ids=lambda: ("A",),
    )
    monkeypatch.setattr(bridge, "_optional_import", lambda name: fake if name == "design_dna.host_realization" else None)

    assert bridge.list_host_realizable_reference_ids() == ("A", "B", "C")
    assert bridge.list_browser_proving_reference_ids() == ("A",)


def test_public_bridge_older_private_package_fallback_preserves_old_nine_style_semantics(monkeypatch):
    fake = SimpleNamespace(list_host_realizable_reference_ids=lambda: ("A", "B"))
    monkeypatch.setattr(bridge, "_optional_import", lambda name: fake if name == "design_dna.host_realization" else None)

    assert bridge.list_browser_proving_reference_ids() == ("A", "B")


def test_catalog_status_does_not_convert_host_readiness_into_eq4_credit(monkeypatch):
    monkeypatch.setattr(state_module, "list_canonical_reference_options", lambda: (_option("A"), _option("B"), _option("C")))
    monkeypatch.setattr(state_module, "list_host_realizable_reference_ids", lambda: ("A", "B"))
    monkeypatch.setattr(state_module, "list_browser_proving_reference_ids", lambda: ("A",))

    rows = {row["id"]: row for row in state_module._catalog_snapshots()}

    assert rows["A"]["host_ready"] == "true"
    assert rows["A"]["browser_proving"] == "true"
    assert rows["A"]["status"] == "Browser proving slice · EQ4 evidence pending"

    assert rows["B"]["host_ready"] == "true"
    assert rows["B"]["browser_proving"] == "false"
    assert rows["B"]["status"] == "Host-realization ready · EQ4 evidence pending"

    assert rows["C"]["host_ready"] == "false"
    assert rows["C"]["browser_proving"] == "false"
    assert rows["C"]["status"] == "Canonical · host realization pending"

    assert all("PASS" not in row["status"] for row in rows.values())
    assert all("credited" not in row["status"].lower() for row in rows.values())
