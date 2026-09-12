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


def _payload(*, approved=True, placement="bounded_material_frame_outside_text_surface", opacity=0.38):
    typography = SimpleNamespace(
        pack_id="demo-pack",
        font_family="Arial, sans-serif",
        font_weight=700,
        heading_letter_spacing="0.04em",
        heading_text_transform="uppercase",
        body_letter_spacing="0em",
        line_height=1.45,
    )
    return SimpleNamespace(
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


def test_missing_private_signature_runtime_fails_closed(monkeypatch):
    monkeypatch.setattr(bridge, "import_module", lambda _name: (_ for _ in ()).throw(ModuleNotFoundError()))
    assert bridge.resolve_approved_visual_signature("CA21") is None


def test_draft_signature_never_crosses_normal_runtime_bridge(monkeypatch):
    module = SimpleNamespace(read_approved_signature=lambda _reference_id: _payload(approved=False))
    monkeypatch.setattr(bridge, "import_module", lambda _name: module)
    assert bridge.resolve_approved_visual_signature("CA21") is None


def test_final_signature_is_projected_without_private_paths(monkeypatch):
    module = SimpleNamespace(read_approved_signature=lambda _reference_id: _payload())
    monkeypatch.setattr(bridge, "import_module", lambda _name: module)
    result = bridge.resolve_approved_visual_signature("CA21")
    assert result is not None
    assert result.reference_id == "CA21"
    assert result.material_unit_id == "M4"
    assert result.material_data_uri.startswith("data:image/webp;base64,")
    assert result.material_placement_mode == "bounded_material_frame_outside_text_surface"
    assert result.material_opacity == 0.38
    assert result.typography_pack_id == "demo-pack"
    assert result.font_weight == 700
    assert "design_dna/" not in result.material_data_uri


def test_unsafe_placement_or_opacity_fails_closed(monkeypatch):
    for payload in (
        _payload(placement="unknown"),
        _payload(placement="surface_overlay", opacity=0.30),
        _payload(placement="bounded_material_frame_outside_text_surface", opacity=0.51),
    ):
        bridge._private_module.cache_clear()
        bridge.resolve_approved_visual_signature.cache_clear()
        module = SimpleNamespace(read_approved_signature=lambda _reference_id, payload=payload: payload)
        monkeypatch.setattr(bridge, "import_module", lambda _name, module=module: module)
        assert bridge.resolve_approved_visual_signature("CA21") is None
