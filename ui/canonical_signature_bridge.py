"""Optional public bridge for private Design-DNA visual-signature proving.

Draft signature packs are exposed only through the private package's explicit
proving seam. Missing/broken private DNA is a neutral fallback state. Normal
production presentation must use final-approved signature resolution instead.
"""
from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass
from importlib import import_module
import logging
from typing import Optional


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CanonicalTypographySurface:
    pack_id: str
    font_family: str
    font_weight: int
    heading_letter_spacing: str
    heading_text_transform: str
    body_letter_spacing: str
    line_height: float


@dataclass(frozen=True)
class CanonicalSignatureSurface:
    reference_id: str
    material_unit_id: str
    material_variant: str
    material_candidate_id: str
    data_uri: str
    payload_sha256: str
    surface_opacity: float
    tile_size: str
    placement_mode: str
    typography: CanonicalTypographySurface
    final_approved: bool


def _optional_import(module_name: str):
    try:
        return import_module(module_name)
    except Exception as exc:
        logger.warning("Optional canonical signature import failed; neutral fallback retained: %s", exc)
        return None


def resolve_signature_for_proving(reference_id: str) -> Optional[CanonicalSignatureSurface]:
    module = _optional_import("design_dna.visual_signature_host")
    if module is None:
        return None
    try:
        payload = module.read_signature_for_proving(str(reference_id))
        if payload is None:
            return None
        raw = bytes(payload.material_payload)
        mime = str(payload.material_mime_type)
        if not raw or not mime.startswith("image/"):
            return None
        typography = payload.typography
        return CanonicalSignatureSurface(
            reference_id=str(payload.reference_id),
            material_unit_id=str(payload.material_unit_id),
            material_variant=str(payload.material_variant),
            material_candidate_id=str(payload.material_candidate_id),
            data_uri=f"data:{mime};base64," + b64encode(raw).decode("ascii"),
            payload_sha256=str(payload.material_sha256),
            surface_opacity=float(payload.material_opacity),
            tile_size=str(payload.material_tile_size),
            placement_mode=str(payload.material_placement_mode),
            typography=CanonicalTypographySurface(
                pack_id=str(typography.pack_id),
                font_family=str(typography.font_family),
                font_weight=int(typography.font_weight),
                heading_letter_spacing=str(typography.heading_letter_spacing),
                heading_text_transform=str(typography.heading_text_transform),
                body_letter_spacing=str(typography.body_letter_spacing),
                line_height=float(typography.line_height),
            ),
            final_approved=bool(payload.final_approved),
        )
    except Exception as exc:
        logger.warning("Optional visual-signature proving resolution failed; neutral fallback retained: %s", exc)
        return None


__all__ = [
    "CanonicalSignatureSurface",
    "CanonicalTypographySurface",
    "resolve_signature_for_proving",
]
