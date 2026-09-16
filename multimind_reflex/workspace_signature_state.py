"""Presentation-only visual-signature extension for the Reflex workspace.

Canonical references keep their approved material/typography/mark payloads.
Atomic MusicDNA themes reuse the same outer presentation layer only when their
private runtime provides a real/open asset; otherwise the track survives through
its typography, palette and archetype topology.  No application/session/
provider/persistence truth is owned here.
"""
from __future__ import annotations

import reflex as rx

from multimind_reflex.workspace_dna_state import WorkspaceDnaState
from ui.visual_signature_bridge import resolve_approved_visual_signature
from ui.music_dna_bridge import realize_music_theme


def _signature(reference_id: str):
    if not str(reference_id or "").strip():
        return None
    return resolve_approved_visual_signature(reference_id)


def _music_plan(identity_dna_id: str, archetype_id: str):
    value = str(identity_dna_id or "").strip()
    if not value.startswith("music:"):
        return None
    track_id = value.split(":", 1)[1].strip()
    if not track_id:
        return None
    return realize_music_theme(track_id, str(archetype_id or "chat_first"))


def _mark_dimensions(payload) -> tuple[str, str]:
    if payload is None or not payload.mark_pack_id:
        return "0px", "0px"
    size = int(payload.mark_size_px)
    if payload.mark_shape == "bar":
        return f"{size * 2}px", f"{max(payload.mark_stroke_px * 3, size // 3)}px"
    return f"{size}px", f"{size}px"


class WorkspaceSignatureState(WorkspaceDnaState):
    """Adds fail-closed canonical and MusicDNA visual projections."""

    @rx.var
    def active_signature_available(self) -> bool:
        if _signature(self.active_canonical_reference_id) is not None:
            return True
        music = _music_plan(self.active_identity_dna, self.active_archetype)
        return bool(music is not None and music.asset_url)

    @rx.var
    def active_signature_material_data_uri(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        if payload is not None:
            return payload.material_data_uri
        music = _music_plan(self.active_identity_dna, self.active_archetype)
        return music.asset_url if music is not None else ""

    @rx.var
    def active_signature_material_opacity(self) -> float:
        payload = _signature(self.active_canonical_reference_id)
        if payload is not None:
            return payload.material_opacity
        music = _music_plan(self.active_identity_dna, self.active_archetype)
        return 0.24 if music is not None and music.asset_url else 0.0

    @rx.var
    def active_signature_material_tile_size(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        if payload is not None:
            return payload.material_tile_size
        music = _music_plan(self.active_identity_dna, self.active_archetype)
        return "cover" if music is not None and music.asset_url else "auto"

    @rx.var
    def active_signature_material_placement_mode(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        if payload is not None:
            return payload.material_placement_mode
        music = _music_plan(self.active_identity_dna, self.active_archetype)
        return music.layout_flow if music is not None else ""

    @rx.var
    def active_signature_font_family(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        if payload is not None:
            return payload.font_family
        music = _music_plan(self.active_identity_dna, self.active_archetype)
        return music.font_family if music is not None else self.active_font_family

    @rx.var
    def active_signature_heading_font_weight_css(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return str(payload.font_weight) if payload is not None else "inherit"

    @rx.var
    def active_signature_heading_letter_spacing(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return payload.heading_letter_spacing if payload is not None else "normal"

    @rx.var
    def active_signature_heading_text_transform(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return payload.heading_text_transform if payload is not None else "none"

    @rx.var
    def active_signature_body_letter_spacing(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return payload.body_letter_spacing if payload is not None else "normal"

    @rx.var
    def active_signature_line_height(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return str(payload.line_height) if payload is not None else "1.5"

    @rx.var
    def active_signature_mark_available(self) -> bool:
        payload = _signature(self.active_canonical_reference_id)
        return bool(payload is not None and payload.mark_pack_id)

    @rx.var
    def active_signature_mark_pack_id(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return payload.mark_pack_id if payload is not None else ""

    @rx.var
    def active_signature_mark_shape(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return payload.mark_shape if payload is not None else ""

    @rx.var
    def active_signature_mark_width(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return _mark_dimensions(payload)[0]

    @rx.var
    def active_signature_mark_height(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return _mark_dimensions(payload)[1]

    @rx.var
    def active_signature_mark_stroke_width(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return f"{payload.mark_stroke_px}px" if payload is not None and payload.mark_pack_id else "0px"

    @rx.var
    def active_signature_mark_opacity(self) -> float:
        payload = _signature(self.active_canonical_reference_id)
        return payload.mark_opacity if payload is not None and payload.mark_pack_id else 0.0

    @rx.var
    def active_signature_mark_radius(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return "999px" if payload is not None and payload.mark_shape == "ring" else "0px"

    @rx.var
    def active_signature_mark_transform(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return "rotate(45deg)" if payload is not None and payload.mark_shape == "diamond" else "none"

    @rx.var
    def draft_signature_available(self) -> bool:
        if _signature(self.draft_canonical_reference_id) is not None:
            return True
        music = _music_plan(self.draft_identity_dna, self.draft_archetype)
        return bool(music is not None and music.asset_url)

    @rx.var
    def draft_signature_material_data_uri(self) -> str:
        payload = _signature(self.draft_canonical_reference_id)
        if payload is not None:
            return payload.material_data_uri
        music = _music_plan(self.draft_identity_dna, self.draft_archetype)
        return music.asset_url if music is not None else ""

    @rx.var
    def draft_signature_material_opacity(self) -> float:
        payload = _signature(self.draft_canonical_reference_id)
        if payload is not None:
            return payload.material_opacity
        music = _music_plan(self.draft_identity_dna, self.draft_archetype)
        return 0.24 if music is not None and music.asset_url else 0.0

    @rx.var
    def draft_signature_material_tile_size(self) -> str:
        payload = _signature(self.draft_canonical_reference_id)
        if payload is not None:
            return payload.material_tile_size
        music = _music_plan(self.draft_identity_dna, self.draft_archetype)
        return "cover" if music is not None and music.asset_url else "auto"

    @rx.var
    def draft_signature_font_family(self) -> str:
        payload = _signature(self.draft_canonical_reference_id)
        if payload is not None:
            return payload.font_family
        music = _music_plan(self.draft_identity_dna, self.draft_archetype)
        return music.font_family if music is not None else self.draft_font_family

    @rx.var
    def draft_signature_heading_font_weight_css(self) -> str:
        payload = _signature(self.draft_canonical_reference_id)
        return str(payload.font_weight) if payload is not None else "inherit"

    @rx.var
    def draft_signature_heading_letter_spacing(self) -> str:
        payload = _signature(self.draft_canonical_reference_id)
        return payload.heading_letter_spacing if payload is not None else "normal"

    @rx.var
    def draft_signature_heading_text_transform(self) -> str:
        payload = _signature(self.draft_canonical_reference_id)
        return payload.heading_text_transform if payload is not None else "none"


__all__ = ["WorkspaceSignatureState"]
