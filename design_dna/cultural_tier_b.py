"""Design-DNA M9: additive Cultural Tier-B reference family.

Tier-B is a historical/research tier, not a quality rank. The calibrated additive
surface is exactly ten references; generic Barkcloth remains routed to Material
M9 and MUST NOT be silently reintroduced as CB05.

Where row-level mechanism prose survived B3/Wave-H, this module preserves a
conservative mechanism translation. Where it did not, the runtime marks the row
as BOUNDED_TRANSLATION and keeps the directive deliberately project-scoped.
"""
from __future__ import annotations

from typing import Dict, Mapping, Tuple

from design_dna.catalog import MOBILE_VIEWPORT, WIDE_VIEWPORTS, mechanism, unit
from design_dna.models import Axis, DNAUnit, SemanticZone, UnitKind

CULTURAL_TIER_B_IDS: Tuple[str, ...] = (
    "CB01", "CB02", "CB03", "CB04", "CB06",
    "CB07", "CB08", "CB09", "CB10", "CB11",
)
CULTURAL_TIER_B_NAME_BY_ID: Mapping[str, str] = {
    "CB01": "Glasgow Geometric-Organic",
    "CB02": "Khayamiya",
    "CB03": "Damascene",
    "CB04": "Liyelaa",
    "CB06": "Masi",
    "CB07": "Tukutuku",
    "CB08": "Kanga",
    "CB09": "Dumbara",
    "CB10": "Yakan",
    "CB11": "Turkmen Carpet",
}
CULTURAL_TIER_B_ROUTED_NON_ADDITIVE: Mapping[str, str] = {
    "CB05": "generic Barkcloth -> Material M9; historical routing retained",
}
CULTURAL_TIER_B_RECOVERED_EXAMPLE_IDS = frozenset({"CB02", "CB03", "CB04", "CB06", "CB09"})
CULTURAL_TIER_B_EVIDENCE_MODE_BY_ID: Mapping[str, str] = {
    item: ("RECOVERED_MECHANISM_EXAMPLE" if item in CULTURAL_TIER_B_RECOVERED_EXAMPLE_IDS else "BOUNDED_TRANSLATION")
    for item in CULTURAL_TIER_B_IDS
}
CULTURAL_TIER_B_ASSET_ON_APPLICABLE = frozenset(CULTURAL_TIER_B_IDS)
CULTURAL_TIER_B_ASSET_ON_NOT_APPLICABLE = frozenset()

_PROVENANCE = (
    "docs/design-dna/calibration/GLOBAL_CALIBRATION_LEDGER.md;"
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_B3_TIER_B_ROUTING_v1__MEMORY_RECONSTRUCTION.md;"
    "docs/design-dna/archive/HISTORICAL_SUPERSESSION_LEDGER.md"
)

_LAYOUT = (SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)
_WORK = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8)
_READ = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U7, SemanticZone.U8)

_RECOVERED: Mapping[str, Tuple[Axis, str]] = {
    "CB02": (
        Axis.MATERIAL_CONSTRUCTION,
        "additive-applique-like-layering-uses-joined-cut-shape-relations-as-construction-not-raster-texture-without-copying-specific-khayamiya-designs-or-claiming-a-production-technique",
    ),
    "CB03": (
        Axis.MATERIAL_CONSTRUCTION,
        "host-and-inlay-like-contrast-keeps-base-field-and-inserted-detail-structurally-distinct-without-reducing-damascene-to-ornament-or-claiming-specific-metalwork-procedure",
    ),
    "CB04": (
        Axis.FORM,
        "liyelaa-jehun-lineage-is-preserved-as-a-lacquer-craft-derived-layer-boundary-and-repeated-form-relation-without-copying-specific-motifs-symbols-or-provenance-claims",
    ),
    "CB06": (
        Axis.SCALE_GRANULARITY,
        "masi-lineage-uses-large-presentation-field-and-bounded-local-mark-regions-without-collapsing-fijian-barkcloth-identity-into-generic-tapa-or-generic-barkcloth",
    ),
    "CB09": (
        Axis.FORM,
        "dumbara-rata-kalala-lineage-uses-bounded-geometric-interlock-and-field-border-relations-without-copying-specific-motifs-technique-symbolism-or-community-claims",
    ),
}

_BOUNDED: Mapping[str, Tuple[Axis, str]] = {
    "CB01": (
        Axis.FORM,
        "project-bounded-geometric-organic-continuity-balances-rectilinear-frame-and-controlled-curvilinear-junctions-without-copying-specific-glasgow-works-or-ornament",
    ),
    "CB07": (
        Axis.INFORMATION,
        "project-bounded-interlaced-panel-like-information-structure-keeps-repeated-local-relations-legible-without-claiming-specific-tukutuku-pattern-meaning-genealogy-or-technique",
    ),
    "CB08": (
        Axis.INFORMATION,
        "project-bounded-message-field-and-border-relationship-keeps-existing-textual-content-primary-without-inventing-kanga-wording-cultural-context-provenance-or-symbolism",
    ),
    "CB10": (
        Axis.FORM,
        "project-bounded-yakan-reference-uses-controlled-repetition-band-and-field-segmentation-without-claiming-specific-weave-motif-community-meaning-technique-or-provenance",
    ),
    "CB11": (
        Axis.SPACE,
        "project-bounded-turkmen-carpet-reference-uses-nested-field-border-and-repeated-cell-zoning-without-collapsing-subgroup-scope-or-copying-specific-gul-symbolism-patterns-or-provenance",
    ),
}


def _identity(ref_id: str):
    axis, directive = (_RECOVERED.get(ref_id) or _BOUNDED[ref_id])
    mode = CULTURAL_TIER_B_EVIDENCE_MODE_BY_ID[ref_id]
    return mechanism(
        ref_id,
        "identity",
        axis,
        (
            f"cultural-tier-b-owner-scoped-reference evidence={mode}; {directive}; "
            "reference-projection-consumes-existing-semantic-state-only; "
            "historical-research-tier-is-not-quality-rank; project-abstraction-is-not-universal-cultural-truth"
        ),
        zones=_WORK,
        rank=94,
    )


def _build(ref_id: str) -> DNAUnit:
    name = CULTURAL_TIER_B_NAME_BY_ID[ref_id]
    slug = (
        name.lower()
        .replace(" ", "-")
        .replace("&", "and")
        .replace("’", "")
        .replace("'", "")
    )
    return unit(
        ref_id,
        kind=UnitKind.REFERENCE,
        family="Cultural Tier B",
        lineage=f"cultural-tier-b-{slug}",
        mechanisms=(
            _identity(ref_id),
            mechanism(
                ref_id,
                "routing-firewall",
                Axis.INFORMATION,
                "presentation-may-not-invent-cultural-meaning-provenance-subgroup-authority-technique-language-chronology-or-semantic-order-and-routed-generic-barkcloth-must-remain-material-not-cultural-reference",
                zones=_WORK,
                rank=100,
            ),
            mechanism(
                ref_id,
                "reading-sanctuary",
                Axis.INFORMATION,
                "reading-code-log-and-research-surfaces-demote-cultural-theatricality-before-legibility-density-or-semantic-order",
                zones=_READ,
                rank=98,
            ),
            mechanism(
                ref_id,
                "wide-adaptation",
                Axis.ADAPTATION,
                "wide-view-may-expand-the-reference-structural-relation-around-existing-content-without-changing-semantic-order-domain-state-or-cultural-claims",
                zones=_LAYOUT,
                viewports=WIDE_VIEWPORTS,
                rank=78,
            ),
            mechanism(
                ref_id,
                "mobile-adaptation",
                Axis.ADAPTATION,
                "mobile-serializes-the-reference-into-bounded-structural-cues-without-hidden-critical-state-false-hierarchy-or-loss-of-content-order",
                zones=_LAYOUT,
                viewports=MOBILE_VIEWPORT,
                rank=90,
            ),
        ),
        provenance=_PROVENANCE,
        identity_survival="asset-off-structural-cultural-tier-b-reference-with-routing-and-epistemic-firewalls",
    )


CULTURAL_TIER_B_REFERENCES: Tuple[DNAUnit, ...] = tuple(_build(item) for item in CULTURAL_TIER_B_IDS)
CULTURAL_TIER_B_BY_ID: Dict[str, DNAUnit] = {item.id: item for item in CULTURAL_TIER_B_REFERENCES}


def cultural_tier_b_asset_on_applicable(reference_id: str) -> bool:
    if reference_id not in CULTURAL_TIER_B_BY_ID:
        raise KeyError(reference_id)
    return reference_id in CULTURAL_TIER_B_ASSET_ON_APPLICABLE


def register_cultural_tier_b(registry) -> None:
    for reference in CULTURAL_TIER_B_REFERENCES:
        registry.register(reference)
