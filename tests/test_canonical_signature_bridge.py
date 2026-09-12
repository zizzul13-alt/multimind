from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import ui.canonical_signature_bridge as bridge


ROOT = Path(__file__).resolve().parents[1]
PANEL = (ROOT / "multimind_reflex/canonical_signature_proving.py").read_text(encoding="utf-8")
PAGE = (ROOT / "multimind_reflex/canonical_page.py").read_text(encoding="utf-8")

BATCH_01 = ("CA20", "CA21", "CA22", "CA24", "CA27", "CA28")
BATCH_02 = ("CA16", "CA01", "CA19", "CA14", "CA23", "CA29")


def _fake_payload(*, placement="bounded_material_frame_outside_text_surface", opacity=0.34):
    return SimpleNamespace(
        reference_id="CA20",
        material_unit_id="M2",
        material_variant="wood-frame",
        material_candidate_id="plywood",
        material_mime_type="image/webp",
        material_payload=b"signature-bytes",
        material_sha256="a" * 64,
        material_opacity=opacity,
        material_tile_size="28rem 28rem",
        material_placement_mode=placement,
        typography=SimpleNamespace(
            pack_id="craft-serif",
            font_family='Georgia, "Times New Roman", serif',
            font_weight=600,
            heading_letter_spacing="0.01em",
            heading_text_transform="none",
            body_letter_spacing="0em",
            line_height=1.55,
        ),
        final_approved=False,
    )


def test_absent_private_signature_package_fails_to_neutral_surface(monkeypatch):
    monkeypatch.setattr(bridge, "_optional_import", lambda name: None)
    assert bridge.resolve_signature_for_proving("CA20") is None


def test_bridge_exposes_opaque_material_and_typography_without_private_paths(monkeypatch):
    fake = SimpleNamespace(read_signature_for_proving=lambda reference_id: _fake_payload())
    monkeypatch.setattr(bridge, "_optional_import", lambda name: fake)
    surface = bridge.resolve_signature_for_proving("CA20")
    assert surface is not None
    assert surface.reference_id == "CA20"
    assert surface.material_unit_id == "M2"
    assert surface.data_uri.startswith("data:image/webp;base64,")
    assert "design_dna/" not in surface.data_uri
    assert surface.surface_opacity == 0.34
    assert surface.placement_mode == "bounded_material_frame_outside_text_surface"
    assert surface.typography.pack_id == "craft-serif"
    assert surface.typography.font_weight == 600
    assert surface.final_approved is False


def test_bridge_rejects_unknown_placement_or_unsafe_opacity(monkeypatch):
    for payload in (
        _fake_payload(placement="unknown", opacity=0.1),
        _fake_payload(placement="surface_overlay", opacity=0.30),
        _fake_payload(placement="bounded_material_frame_outside_text_surface", opacity=0.60),
    ):
        fake = SimpleNamespace(read_signature_for_proving=lambda reference_id, payload=payload: payload)
        monkeypatch.setattr(bridge, "_optional_import", lambda name, fake=fake: fake)
        assert bridge.resolve_signature_for_proving("CA20") is None


def test_signature_panel_keeps_both_batches_isolated_and_credit_neutral():
    for reference_id in BATCH_01 + BATCH_02:
        assert reference_id in PANEL
    assert 'data_signature_batch="01"' in PANEL
    assert 'data_signature_batch="02"' in PANEL
    assert 'data_signature_complete_credit="0"' in PANEL
    assert "DRAFT PROVING" in PANEL
    assert "cultural-safe draft proving" in PANEL
    assert "canonical_signature_proving_panel()" in PAGE
    assert "PROVING · NOT CUTOVER" in PAGE
