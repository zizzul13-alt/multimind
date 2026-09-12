from pathlib import Path


MOBILE_ENTRY = Path("multimind_reflex/mobile_entry.py").read_text(encoding="utf-8")
SIGNATURE_ENTRY = Path("multimind_reflex/signature_entry.py").read_text(encoding="utf-8")
STATE = Path("multimind_reflex/workspace_signature_state.py").read_text(encoding="utf-8")
VERDICT_STATE = Path("multimind_reflex/verdict_state.py").read_text(encoding="utf-8")
SURFACE = Path("multimind_reflex/multimind_reflex.py").read_text(encoding="utf-8")


def test_signature_layer_preserves_accepted_workspace_and_entry_owners():
    assert "from multimind_reflex.multimind_reflex import app" in MOBILE_ENTRY
    assert "from multimind_reflex import verdict_entry as _verdict_entry" in MOBILE_ENTRY
    assert "from multimind_reflex import signature_entry as _signature_entry" in MOBILE_ENTRY
    assert "workspace._authenticated_surface = _signature_authenticated_surface" in SIGNATURE_ENTRY
    assert "workspace._workspace =" not in SIGNATURE_ENTRY
    assert "workspace.HostState =" not in SIGNATURE_ENTRY

    for call in (
        "_workspace_utility_zone()",
        "_workspace_composer_zone()",
        "_workspace_result_zone()",
        "_workspace_history_zone()",
    ):
        assert SURFACE.count(call) == 2
        assert call not in SIGNATURE_ENTRY


def test_signature_state_composes_under_verdict_state_and_is_fail_closed():
    assert "class WorkspaceSignatureState(WorkspaceDnaState)" in STATE
    assert "class VerdictHostState(WorkspaceSignatureState)" in VERDICT_STATE
    assert "resolve_approved_visual_signature" in STATE
    for forbidden in (
        "sqlite3.connect(",
        "DebateOrchestrator(",
        "MultiMindApplication(",
        "provider_registry",
    ):
        assert forbidden not in STATE
    assert "return payload.material_data_uri if payload is not None else \"\"" in STATE
    assert "return str(payload.font_weight) if payload is not None else \"inherit\"" in STATE
    assert "active_signature_mark_available" in STATE
    assert "active_signature_mark_shape" in STATE
    assert "active_signature_mark_width" in STATE
    assert "active_signature_mark_height" in STATE


def test_material_is_bounded_behind_opaque_workspace_zones():
    assert 'class_name="mm-signature-authenticated-frame"' in SIGNATURE_ENTRY
    assert 'data_signature_material_layer="true"' in SIGNATURE_ENTRY
    assert 'pointer_events="none"' in SIGNATURE_ENTRY
    assert "active_signature_material_opacity" in SIGNATURE_ENTRY
    assert "active_signature_material_tile_size" in SIGNATURE_ENTRY
    assert '"transparent !important"' in SIGNATURE_ENTRY
    assert "background_color=HostState.active_surface" in SURFACE
    assert 'class_name=f"mm-zone mm-zone-{area}"' in SURFACE


def test_signature_typography_is_secondary_channel_not_new_renderer():
    assert "active_signature_font_family" in SIGNATURE_ENTRY
    assert "active_signature_heading_font_weight_css" in SIGNATURE_ENTRY
    assert "active_signature_heading_letter_spacing" in SIGNATURE_ENTRY
    assert "active_signature_heading_text_transform" in SIGNATURE_ENTRY
    assert "active_signature_body_letter_spacing" in SIGNATURE_ENTRY
    assert "rx.App(" not in STATE
    assert "rx.App(" not in SIGNATURE_ENTRY


def test_optional_mark_is_visible_bounded_noninteractive_layer_not_theme_renderers():
    assert 'data_signature_mark_layer="true"' in SIGNATURE_ENTRY
    assert "active_signature_mark_pack_id" in SIGNATURE_ENTRY
    assert "active_signature_mark_shape" in SIGNATURE_ENTRY
    assert "active_signature_mark_stroke_width" in SIGNATURE_ENTRY
    assert "active_signature_mark_opacity" in SIGNATURE_ENTRY
    assert 'border_color=HostState.active_accent' in SIGNATURE_ENTRY
    assert 'pointer_events="none"' in SIGNATURE_ENTRY
    assert 'aria_hidden="true"' in SIGNATURE_ENTRY
    # The material stays behind the workspace, while the tiny low-opacity mark
    # must sit above it or the secondary channel can be technically present yet invisible.
    assert 'z_index="2"' in SIGNATURE_ENTRY
    assert 'top="0.75rem"' in SIGNATURE_ENTRY
    assert 'right="0.75rem"' in SIGNATURE_ENTRY
    for forbidden in (
        "<svg",
        "data:image",
        "background_image=HostState.active_signature_mark",
        "cultural_mark",
        "franchise",
    ):
        assert forbidden not in SIGNATURE_ENTRY.casefold()
