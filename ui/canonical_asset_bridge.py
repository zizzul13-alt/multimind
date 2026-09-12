"""Small public bridge for approved private Design-DNA visual payloads.

The optional private package owns asset approval, bytes, hashes and render hints.
This public boundary exposes only a host-safe data URI and bounded presentation
metadata. Missing/broken private DNA is a valid neutral fallback state.
"""
from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass
from importlib import import_module
import logging
from typing import Optional


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CanonicalApprovedAssetSurface:
    unit_id: str
    candidate_id: str
    data_uri: str
    payload_sha256: str
    surface_opacity: float
    tile_size: str


def _optional_import(module_name: str):
    try:
        return import_module(module_name)
    except Exception as exc:
        logger.warning("Optional canonical asset import failed; neutral fallback retained: %s", exc)
        return None


def resolve_approved_asset_surface(
    unit_id: str,
    *,
    accessibility_veto: bool = False,
    reading_sanctuary_veto: bool = False,
) -> Optional[CanonicalApprovedAssetSurface]:
    """Return an opaque approved surface or ``None`` fail-closed."""

    module = _optional_import("design_dna.asset_selection")
    if module is None:
        return None
    try:
        payload = module.read_approved_host_asset(
            str(unit_id),
            accessibility_veto=bool(accessibility_veto),
            reading_sanctuary_veto=bool(reading_sanctuary_veto),
        )
        if payload is None:
            return None
        mime_type = str(payload.mime_type)
        raw = bytes(payload.payload)
        if not mime_type.startswith("image/") or not raw:
            return None
        opacity = float(payload.surface_opacity)
        if not (0.0 < opacity <= 0.25):
            return None
        tile_size = str(payload.tile_size).strip()
        if not tile_size:
            return None
        data_uri = f"data:{mime_type};base64," + b64encode(raw).decode("ascii")
        return CanonicalApprovedAssetSurface(
            unit_id=str(payload.unit_id),
            candidate_id=str(payload.candidate_id),
            data_uri=data_uri,
            payload_sha256=str(payload.payload_sha256),
            surface_opacity=opacity,
            tile_size=tile_size,
        )
    except Exception as exc:
        logger.warning("Optional approved asset resolution failed; neutral fallback retained: %s", exc)
        return None


__all__ = ["CanonicalApprovedAssetSurface", "resolve_approved_asset_surface"]
