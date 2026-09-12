from pathlib import Path


ENTRY = Path("multimind_reflex/mobile_entry.py").read_text(encoding="utf-8")
STATE = Path("multimind_reflex/workspace_signature_state.py").read_text(encoding="utf-8")
SURFACE = Path("multimind_reflex/multimind_reflex.py").read_text(encoding="utf-8")


def test_signature_layer_reuses_one_accepted_workspace_tree():
    assert "_original_workspace = _surface._workspace" in ENTRY
    assert ENTRY.count("_original_workspace()") == 1
    assert "_surface._workspace = _signature_workspace" in ENTRY
    for call in (
        "_workspace_utility_zone()",
        "_workspace_composer_zone()",
        "_workspace_result_zone()",
        "_workspace_history_zone()",
    ):
        assert SURFACE.count(call) == 2  # definition use + one real workspace instantiation
        assert call not in ENTRY


def test_signature_state_is_presentation_only_and_fail_closed():
    assert "class WorkspaceSignatureState(WorkspaceDnaState)" in STATE
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


def test_material_is_bounded_behind_opaque_workspace_zones():
    assert 'class_name="mm-signature-workspace-frame"' in ENTRY
    assert '"&::before"' in ENTRY
    assert '"pointer_events": "none"' in ENTRY
    assert "active_signature_material_opacity" in ENTRY
    assert "active_signature_material_tile_size" in ENTRY
    assert '"transparent !important"' in ENTRY
    # Accepted semantic zone cards remain opaque and owned by the original surface.
    assert "background_color=HostState.active_surface" in SURFACE
    assert 'class_name=f"mm-zone mm-zone-{area}"' in SURFACE


def test_signature_typography_is_secondary_channel_not_new_renderer():
    assert "active_signature_font_family" in ENTRY
    assert "active_signature_heading_font_weight_css" in ENTRY
    assert "active_signature_heading_letter_spacing" in ENTRY
    assert "active_signature_heading_text_transform" in ENTRY
    assert "active_signature_body_letter_spacing" in ENTRY
    assert "rx.App(" not in STATE
    assert "rx.App(" not in ENTRY
