"""Canonical Country-Web registration seam.

M2 historically exposed a combined proving-slice registrar that also included four
Cultural references. M3 needs the full Cultural Tier-S family, so runtime assembly
must be able to register Country-Web independently without duplicate Cultural IDs.
The canonical unit objects are reused from the accepted M2 catalog.
"""
from __future__ import annotations

from typing import Dict, Tuple

from design_dna.models import DNAUnit
from design_dna.references import COUNTRY_WEB_REFERENCE_IDS, M2_REFERENCE_BY_ID

COUNTRY_WEB_REFERENCES: Tuple[DNAUnit, ...] = tuple(
    M2_REFERENCE_BY_ID[item_id] for item_id in COUNTRY_WEB_REFERENCE_IDS
)
COUNTRY_WEB_BY_ID: Dict[str, DNAUnit] = {item.id: item for item in COUNTRY_WEB_REFERENCES}


def register_country_web_references(registry) -> None:
    for reference in COUNTRY_WEB_REFERENCES:
        registry.register(reference)
