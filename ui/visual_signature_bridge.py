"""Optional public bridge for final-approved private visual signatures.

The public host never imports private registry types or paths. It receives only
opaque, bounded presentation scalars plus a self-contained material data URI.
Missing, draft, incompatible, or invalid private signatures resolve to ``None``
so MultiMind keeps the existing neutral/canonical structural presentation.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from importlib import import_module
import logging
from typing import Optional


logger = logging.getLogger(__name__)

_SURFACE_OVERLAY = "surface_overlay"
_FRAME_OUTSIDE_TEXT = "bounded_material_frame_outside_text_surface"
_ALLOWED_PLACEMENTS = {_SURFACE_OVERLAY, _FRAME_OUTSIDE_TEXT}
_MAX_OPACITY = {
    _SURFACE_OVERLAY: 0.25,
    _FRAME_OUTSIDE_TEXT: 0.50,
}


@dataclass(frozen=True)
class ApprovedVisualSignatureProjection:
    reference_id: str
    material_unit_id: str
    material_variant: str
    material_candidate_id: str
    material_data_uri: str
    material_sha256: str
    material_opacity: float
    material_tile_size: str
    material_placement_mode: str
    typography_pack_id: str
    font_family: str
    font_weight: int
    heading_letter_spacing: str
    heading_text_transform: str
    body_letter_spacing: str
    line_height: float


def _warn(exc: Exception) -> None:
    logger.warning(
        "Optional approved visual-signature bridge failed; keeping safe presentation: %s",
        exc,
    )


def _private_module():
    try:
        return import_module("design_dna.visual_signature_host")
    except Exception as exc:
        _warn(exc)
        return None


def _data_uri(mime_type: str, payload: bytes) -> str:
    if not mime_type.startswith("image/"):
        raise ValueError("signature material MIME type must be image/*")
    encoded = base64.b64encode(payload).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def resolve_approved_visual_signature(
    reference_id: str,
) -> Optional[ApprovedVisualSignatureProjection]:
    """Return one final-approved signature or ``None`` on any unsafe state."""
    module = _private_module()
    if module is None:
        return None
    try:
        payload = module.read_approved_signature(str(reference_id or "").strip())
        if payload is None or not bool(getattr(payload, "final_approved", False)):
            return None

        placement = str(payload.material_placement_mode)
        if placement not in _ALLOWED_PLACEMENTS:
            raise ValueError(f"unsupported signature material placement: {placement}")
        opacity = float(payload.material_opacity)
        if opacity < 0 or opacity > _MAX_OPACITY[placement]:
            raise ValueError(f"unsafe signature material opacity for {placement}: {opacity}")

        typography = payload.typography
        weight = int(typography.font_weight)
        if weight < 100 or weight > 900:
            raise ValueError(f"unsafe signature typography weight: {weight}")
        line_height = float(typography.line_height)
        if line_height < 1.2 or line_height > 2.0:
            raise ValueError(f"unsafe signature line height: {line_height}")

        return ApprovedVisualSignatureProjection(
            reference_id=str(payload.reference_id),
            material_unit_id=str(payload.material_unit_id),
            material_variant=str(payload.material_variant),
            material_candidate_id=str(payload.material_candidate_id),
            material_data_uri=_data_uri(str(payload.material_mime_type), bytes(payload.material_payload)),
            material_sha256=str(payload.material_sha256),
            material_opacity=opacity,
            material_tile_size=str(payload.material_tile_size),
            material_placement_mode=placement,
            typography_pack_id=str(typography.pack_id),
            font_family=str(typography.font_family),
            font_weight=weight,
            heading_letter_spacing=str(typography.heading_letter_spacing),
            heading_text_transform=str(typography.heading_text_transform),
            body_letter_spacing=str(typography.body_letter_spacing),
            line_height=line_height,
        )
    except Exception as exc:
        _warn(exc)
        return None


__all__ = [
    "ApprovedVisualSignatureProjection",
    "resolve_approved_visual_signature",
]
