"""Approved self-hosted material assets.

The private Design-DNA package already productionised and license-checked a
small set of CC0 material textures, each with an immutable SHA256 and a recorded
source URL (see design_dna/asset_selection.py). Those are preferred over anything
new: they are CC0 / Open Access, self-hosted, and require no attribution.

These are material textures -- plywood, rock, concrete, metal, book pattern,
gold leaf -- not photographs. They sit behind the world plate as texture, which
is what the previews do, rather than replacing the scene photo.

If an asset is ever missing here, the order is: check the Design-DNA repo first,
then search, and accept only CC0 / public-domain / OFL / MIT-ISC. No
generative-AI visuals.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MaterialAsset:
    unit_id: str
    name: str
    path: str
    source_url: str
    license_status: str


# Carried from design_dna/asset_selection.py. Same files, same sources, same
# licences -- this module only makes them reachable from the public host.
MATERIALS: dict[str, MaterialAsset] = {
    "M2": MaterialAsset(
        "M2",
        "plywood",
        "/materials/m2_plywood_diff_1k.webp",
        "https://polyhaven.com/a/plywood",
        "CC0_APPROVED_SELF_HOSTED",
    ),
    "M3": MaterialAsset(
        "M3",
        "rock_surface",
        "/materials/m3_rock_surface_diff_1k.webp",
        "https://polyhaven.com/a/rock_surface",
        "CC0_APPROVED_SELF_HOSTED",
    ),
    "M4": MaterialAsset(
        "M4",
        "rough_concrete",
        "/materials/m4_rough_concrete_diff_1k.webp",
        "https://polyhaven.com/a/rough_concrete",
        "CC0_APPROVED_SELF_HOSTED",
    ),
    "M5": MaterialAsset(
        "M5",
        "ambientcg_metal052a_roughness",
        "/materials/m5_metal052a_rough_768.webp",
        "https://ambientcg.com/view?id=Metal052A",
        "CC0_APPROVED_SELF_HOSTED",
    ),
    "M7": MaterialAsset(
        "M7",
        "book_pattern_roughness",
        "/materials/m7_book_pattern_rough_768.webp",
        "https://polyhaven.com/a/book_pattern",
        "CC0_APPROVED_SELF_HOSTED",
    ),
    "CS04": MaterialAsset(
        "CS04",
        "met_242965_gold_leaf_surface",
        "/materials/cs04_met_242965_gold_surface_768.webp",
        "https://www.metmuseum.org/art/collection/search/242965",
        "MET_OPEN_ACCESS_APPROVED_SELF_HOSTED",
    ),
}


def material_for_track(track_id: str) -> MaterialAsset | None:
    """Return a material texture for a track.

    MusicDNA topologies do not map to material engines one-to-one, so this is a
    stable per-track assignment rather than a derivation. The alternative is no
    texture at all, which is what the previews never do.
    """
    slug = str(track_id or "").strip().casefold()
    order = ["M4", "M3", "M2", "M7", "M5", "CS04"]
    if not slug:
        return None
    idx = sum(ord(c) for c in slug) % len(order)
    return MATERIALS[order[idx]]


def material_credit(asset: MaterialAsset | None) -> str:
    """Provenance line for a material, shown in the world rail."""
    if asset is None:
        return ""
    return f"{asset.name} \u00b7 {asset.license_status} \u00b7 {asset.source_url}"


__all__ = [
    "MATERIALS",
    "MaterialAsset",
    "material_credit",
    "material_for_track",
]