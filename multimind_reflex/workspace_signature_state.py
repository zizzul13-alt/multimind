"""Presentation-only approved visual-signature extension for the Reflex workspace.

This layer derives material/typography scalars from the already-active canonical
reference. It owns no application/session/provider/persistence truth. Missing or
invalid private Design-DNA signatures collapse to neutral empty values, leaving
the accepted structural workspace unchanged.
"""
from __future__ import annotations

import reflex as rx

from multimind_reflex.workspace_dna_state import WorkspaceDnaState
from ui.visual_signature_bridge import resolve_approved_visual_signature


def _signature(reference_id: str):
    if not str(reference_id or "").strip():
        return None
    return resolve_approved_visual_signature(reference_id)


class WorkspaceSignatureState(WorkspaceDnaState):
    """Adds fail-closed visual-signature projections to presentation state."""

    @rx.var
    def active_signature_available(self) -> bool:
        return _signature(self.active_canonical_reference_id) is not None

    @rx.var
    def active_signature_material_data_uri(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return payload.material_data_uri if payload is not None else ""

    @rx.var
    def active_signature_material_opacity(self) -> float:
        payload = _signature(self.active_canonical_reference_id)
        return payload.material_opacity if payload is not None else 0.0

    @rx.var
    def active_signature_material_tile_size(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return payload.material_tile_size if payload is not None else "auto"

    @rx.var
    def active_signature_material_placement_mode(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return payload.material_placement_mode if payload is not None else ""

    @rx.var
    def active_signature_font_family(self) -> str:
        payload = _signature(self.active_canonical_reference_id)
        return payload.font_family if payload is not None else self.active_font_family

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
    def draft_signature_available(self) -> bool:
        return _signature(self.draft_canonical_reference_id) is not None

    @rx.var
    def draft_signature_material_data_uri(self) -> str:
        payload = _signature(self.draft_canonical_reference_id)
        return payload.material_data_uri if payload is not None else ""

    @rx.var
    def draft_signature_material_opacity(self) -> float:
        payload = _signature(self.draft_canonical_reference_id)
        return payload.material_opacity if payload is not None else 0.0

    @rx.var
    def draft_signature_material_tile_size(self) -> str:
        payload = _signature(self.draft_canonical_reference_id)
        return payload.material_tile_size if payload is not None else "auto"

    @rx.var
    def draft_signature_font_family(self) -> str:
        payload = _signature(self.draft_canonical_reference_id)
        return payload.font_family if payload is not None else self.draft_font_family

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
