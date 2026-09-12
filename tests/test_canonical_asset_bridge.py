from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import ui.canonical_asset_bridge as bridge


ROOT = Path(__file__).resolve().parents[1]
PANEL = (ROOT / "multimind_reflex/canonical_material_proving.py").read_text(encoding="utf-8")
PAGE = (ROOT / "multimind_reflex/canonical_page.py").read_text(encoding="utf-8")


def test_absent_private_asset_package_fails_to_neutral_surface(monkeypatch):
    monkeypatch.setattr(bridge, "_optional_import", lambda name: None)
    assert bridge.resolve_approved_asset_surface("M7") is None


def test_bridge_exposes_only_host_safe_data_uri_and_bounded_hints(monkeypatch):
    calls = []

    def read(unit_id, **kwargs):
        calls.append((unit_id, kwargs))
        return SimpleNamespace(
            unit_id="M7",
            candidate_id="book_pattern_roughness",
            mime_type="image/webp",
            payload=b"approved-bytes",
            payload_sha256="8" * 64,
            surface_opacity=0.01,
            tile_size="12rem 12rem",
        )

    fake = SimpleNamespace(read_approved_host_asset=read)
    monkeypatch.setattr(
        bridge,
        "_optional_import",
        lambda name: fake if name == "design_dna.asset_selection" else None,
    )
    surface = bridge.resolve_approved_asset_surface(
        "M7", accessibility_veto=False, reading_sanctuary_veto=False
    )
    assert surface is not None
    assert surface.unit_id == "M7"
    assert surface.candidate_id == "book_pattern_roughness"
    assert surface.data_uri.startswith("data:image/webp;base64,")
    assert "design_dna/" not in surface.data_uri
    assert surface.surface_opacity == 0.01
    assert surface.tile_size == "12rem 12rem"
    assert calls == [("M7", {"accessibility_veto": False, "reading_sanctuary_veto": False})]


def test_malformed_private_payload_fails_closed(monkeypatch):
    fake = SimpleNamespace(
        read_approved_host_asset=lambda *args, **kwargs: SimpleNamespace(
            unit_id="M7",
            candidate_id="bad",
            mime_type="text/html",
            payload=b"x",
            payload_sha256="0" * 64,
            surface_opacity=1.0,
            tile_size="",
        )
    )
    monkeypatch.setattr(bridge, "_optional_import", lambda name: fake)
    assert bridge.resolve_approved_asset_surface("M7") is None


def test_reflex_material_panel_is_isolated_and_not_global_reference_binding():
    assert 'resolve_approved_asset_surface("M7")' in PANEL
    assert 'data_material_proof="m7-approved"' in PANEL
    assert "M7 APPROVED PAYLOAD · ACTIVE" in PANEL
    assert "no reference/theme binding implied" in PANEL
    assert "canonical_material_proving_panel()" in PAGE
    assert "PROVING · NOT CUTOVER" in PAGE
