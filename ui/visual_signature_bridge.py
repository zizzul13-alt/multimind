"""Optional public bridge for final-approved private visual signatures.

The public host never imports private registry types or paths. It receives only
opaque, bounded presentation scalars plus a self-contained material data URI.
Missing, draft, incompatible, or invalid private signatures resolve to ``None``
so MultiMind keeps the existing neutral/canonical structural presentation.

Optional mark decoration is deliberately tiny and declarative. The private
package may request one generic shape from a bounded vocabulary; arbitrary CSS,
SVG, image paths, cultural symbols, and franchise marks never cross this seam.
An absent or invalid mark degrades to no mark without disabling an otherwise
valid material/typography signature.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from functools import lru_cache
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
_ALLOWED_MARK_SHAPES = {"ring", "square", "diamond", "bar"}
_MARK_DEFAULTS = ("", "", 0, 0, 0.0)


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
    mark_pack_id: str = ""
    mark_shape: str = ""
    mark_size_px: int = 0
    mark_stroke_px: int = 0
    mark_opacity: float = 0.0


def _warn(exc: Exception) -> None:
    logger.warning(
        "Optional approved visual-signature bridge failed; keeping safe presentation: %s",
        exc,
    )


@lru_cache(maxsize=1)
def _private_module():
    """Resolve optional private package once for the lifetime of this process.

    Package availability cannot legitimately change without a process restart,
    so repeated import attempts during Reflex computed-var evaluation only add
    startup noise and work while providing no recovery benefit.
    """
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


def _safe_mark(payload) -> tuple[str, str, int, int, float]:
    """Project one optional generic mark or return neutral mark scalars.

    Decoration may fail independently from the required material/typography
    channels. This keeps malformed optional presentation metadata from taking
    down an otherwise accepted signature.
    """
    mark = getattr(payload, "mark", None)
    if mark is None:
        return _MARK_DEFAULTS
    try:
        pack_id = str(mark.pack_id).strip()
        shape = str(mark.shape).strip().lower()
        size_px = int(mark.size_px)
        stroke_px = int(mark.stroke_px)
        opacity = float(mark.opacity)
        if not pack_id:
            raise ValueError("signature mark pack id is empty")
        if shape not in _ALLOWED_MARK_SHAPES:
            raise ValueError(f"unsupported signature mark shape: {shape}")
        if not 8 <= size_px <= 64:
            raise ValueError(f"unsafe signature mark size: {size_px}")
        if not 1 <= stroke_px <= 6:
            raise ValueError(f"unsafe signature mark stroke: {stroke_px}")
        if not 0.05 <= opacity <= 0.70:
            raise ValueError(f"unsafe signature mark opacity: {opacity}")
        return pack_id, shape, size_px, stroke_px, opacity
    except Exception as exc:
        _warn(exc)
        return _MARK_DEFAULTS


@lru_cache(maxsize=256)
def resolve_approved_visual_signature(
    reference_id: str,
) -> Optional[ApprovedVisualSignatureProjection]:
    """Return one immutable final-approved signature or ``None`` on unsafe state.

    Private registry contents are packaged at process start and cannot change in
    place, so caching by canonical reference is safe until the next restart.
    """
    normalized_reference = str(reference_id or "").strip()
    if not normalized_reference:
        return None
    module = _private_module()
    if module is None:
        return None
    try:
        payload = module.read_approved_signature(normalized_reference)
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

        mark_pack_id, mark_shape, mark_size_px, mark_stroke_px, mark_opacity = _safe_mark(payload)
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
            mark_pack_id=mark_pack_id,
            mark_shape=mark_shape,
            mark_size_px=mark_size_px,
            mark_stroke_px=mark_stroke_px,
            mark_opacity=mark_opacity,
        )
    except Exception as exc:
        _warn(exc)
        return None


__all__ = [
    "ApprovedVisualSignatureProjection",
    "resolve_approved_visual_signature",
]
