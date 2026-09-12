from types import SimpleNamespace

import pytest

import ui.visual_signature_bridge as bridge


@pytest.fixture(autouse=True)
def _clear_signature_bridge_caches():
    bridge._private_module.cache_clear()
    bridge.resolve_approved_visual_signature.cache_clear()
    yield
    bridge._private_module.cache_clear()
    bridge.resolve_approved_visual_signature.cache_clear()


def _mark(*, pack_id="generic-ring", shape="ring", size_px=28, stroke_px=2, opacity=0.42):
    return SimpleNamespace(
        pack_id=pack_id,
        shape=shape,
        size_px=size_px,
        stroke_px=stroke_px,
        opacity=opacity,
    )


def _payload(*, approved=True, placement="bounded_material_frame_outside_text_surface", opacity=0.38, mark=None):
    typography = SimpleNamespace(
        pack_id="demo-pack",
        font_family="Arial, sans-serif",
        font_weight=700,
        heading_letter_spacing="0.04em",
        heading_text_transform="uppercase",
        body_letter_spacing="0em",
        line_height=1.45,
    )
    payload = SimpleNamespace(
        reference_id="CA21",
        material_unit_id="M4",
        material_variant="concrete-frame",
        material_candidate_id="rough_concrete",
        material_mime_type="image/webp",
        material_payload=b"abc",
        material_sha256="deadbeef",
        material_opacity=opacity,
        material_tile_size="28rem 28rem",
        material_placement_mode=placement,
        typography=typography,
        final_approved=approved,
    )
    if mark is not None:
        payload.mark = mark
    return payload


def _resolve(monkeypatch, payload):
    bridge._private_module.cache_clear()
    bridge.resolve_approved_visual_signature.cache_clear()
    module = SimpleNamespace(read_approved_signature=lambda _reference_id: payload)
    monkeypatch.setattr(bridge, "import_module", lambda _name: module)
    return bridge.resolve_approved_visual_signature("CA21")


def test_missing_private_signature_runtime_fails_closed(monkeypatch):
    monkeypatch.setattr(bridge, "import_module", lambda _name: (_ for _ in ()).throw(ModuleNotFoundError()))
    assert bridge.resolve_approved_visual_signature("CA21") is None


def test_draft_signature_never_crosses_normal_runtime_bridge(monkeypatch):
    module = SimpleNamespace(read_approved_signature=lambda _reference_id: _payload(approved=False))
    monkeypatch.setattr(bridge, "import_module", lambda _name: module)
    assert bridge.resolve_approved_visual_signature("CA21") is None


def test_final_signature_is_projected_without_private_paths(monkeypatch):
    result = _resolve(monkeypatch, _payload())
    assert result is not None
    assert result.reference_id == "CA21"
    assert result.material_unit_id == "M4"
    assert result.material_data_uri.startswith("data:image/webp;base64,")
    assert result.material_placement_mode == "bounded_material_frame_outside_text_surface"
    assert result.material_opacity == 0.38
    assert result.typography_pack_id == "demo-pack"
    assert result.font_weight == 700
    assert result.mark_pack_id == ""
    assert result.mark_shape == ""
    assert result.mark_size_px == 0
    assert result.mark_stroke_px == 0
    assert result.mark_opacity == 0.0
    assert "design_dna/" not in result.material_data_uri


def test_valid_generic_mark_crosses_as_bounded_scalars(monkeypatch):
    result = _resolve(monkeypatch, _payload(mark=_mark()))
    assert result is not None
    assert result.mark_pack_id == "generic-ring"
    assert result.mark_shape == "ring"
    assert result.mark_size_px == 28
    assert result.mark_stroke_px == 2
    assert result.mark_opacity == 0.42


@pytest.mark.parametrize(
    "mark",
    (
        _mark(shape="glyph"),
        _mark(size_px=7),
        _mark(size_px=65),
        _mark(stroke_px=0),
        _mark(stroke_px=7),
        _mark(opacity=0.01),
        _mark(opacity=0.71),
        _mark(pack_id=""),
    ),
)
def test_unsafe_optional_mark_degrades_to_no_mark_without_killing_signature(monkeypatch, mark):
    result = _resolve(monkeypatch, _payload(mark=mark))
    assert result is not None
    assert result.material_unit_id == "M4"
    assert result.typography_pack_id == "demo-pack"
    assert result.mark_pack_id == ""
    assert result.mark_shape == ""
    assert result.mark_size_px == 0
    assert result.mark_stroke_px == 0
    assert result.mark_opacity == 0.0


def test_unsafe_placement_or_opacity_fails_closed(monkeypatch):
    for payload in (
        _payload(placement="unknown"),
        _payload(placement="surface_overlay", opacity=0.30),
        _payload(placement="bounded_material_frame_outside_text_surface", opacity=0.51),
    ):
        assert _resolve(monkeypatch, payload) is None
