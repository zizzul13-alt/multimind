"""Design-DNA M8: additive Cultural Tier-A reference family.

The locked Cultural denominator contains 29 additive Tier-A references. Seven
historical B2 rows remain non-additive holds and are preserved as accounting
metadata only. The original row-by-row source prose is not uniformly available;
therefore this module distinguishes recovered mechanism examples from bounded,
conservative translations of the locked names and corpus-level contracts.

Cultural references are presentation abstractions, not claims of universal
cultural truth. They never invent chronology, hierarchy, authority, language,
technique, provenance, subgroup identity, or cultural meaning.
"""
from __future__ import annotations

from typing import Dict, Mapping, Tuple

from design_dna.catalog import MOBILE_VIEWPORT, WIDE_VIEWPORTS, mechanism, unit
from design_dna.models import Axis, DNAUnit, SemanticZone, UnitKind

CULTURAL_TIER_A_IDS: Tuple[str, ...] = (
    "CA01", "CA04", "CA08", "CA09", "CA10", "CA11", "CA12", "CA13",
    "CA14", "CA15", "CA16", "CA17", "CA18", "CA19", "CA20", "CA21",
    "CA22", "CA23", "CA24", "CA25", "CA26", "CA27", "CA28", "CA29",
    "CA30", "CA32", "CA34", "CA35", "CA36",
)
CULTURAL_TIER_A_NAME_BY_ID: Mapping[str, str] = {
    "CA01": "Batik",
    "CA04": "Hikifuda",
    "CA08": "Stepwell",
    "CA09": "Truck Total Surface",
    "CA10": "Jamdani",
    "CA11": "Shyrdak",
    "CA12": "Yurt",
    "CA13": "Zellij",
    "CA14": "Ghadamès",
    "CA15": "Kente",
    "CA16": "Adire",
    "CA17": "Harar",
    "CA18": "Kuba",
    "CA19": "Bògòlanfini",
    "CA20": "Arts & Crafts",
    "CA21": "De Stijl",
    "CA22": "Cassandre",
    "CA23": "Guimard",
    "CA24": "Art Deco",
    "CA25": "Polish Poster",
    "CA26": "Secession",
    "CA27": "Streamline",
    "CA28": "Eames",
    "CA29": "Guna Mola",
    "CA30": "Noailles",
    "CA32": "ICAIC",
    "CA34": "Māori Wharenui",
    "CA35": "Siapo",
    "CA36": "Ngatu",
}
CULTURAL_TIER_A_HISTORICAL_NON_ADDITIVE: Mapping[str, str] = {
    "CA02": "Vernacular Street",
    "CA03": "Poetic Editorial",
    "CA05": "Computational Experimental",
    "CA06": "Calligraphic Kinetic",
    "CA07": "Miniature Narrative Field",
    "CA31": "Gingerbread",
    "CA33": "Constructive Symbol Grid",
}
CULTURAL_TIER_A_RECOVERED_EXAMPLE_IDS = frozenset(
    {"CA01", "CA04", "CA08", "CA10", "CA11", "CA12", "CA13", "CA15", "CA16", "CA17", "CA18", "CA19"}
)
CULTURAL_TIER_A_EVIDENCE_MODE_BY_ID: Mapping[str, str] = {
    item: ("RECOVERED_MECHANISM_EXAMPLE" if item in CULTURAL_TIER_A_RECOVERED_EXAMPLE_IDS else "BOUNDED_TRANSLATION")
    for item in CULTURAL_TIER_A_IDS
}
CULTURAL_TIER_A_ASSET_ON_APPLICABLE = frozenset(CULTURAL_TIER_A_IDS)
CULTURAL_TIER_A_ASSET_ON_NOT_APPLICABLE = frozenset()

_PROVENANCE = (
    "docs/design-dna/corpora/CORPUS_INDEX.md;"
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_B2_TIER_A_v1__MEMORY_RECONSTRUCTION.md;"
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_6_CULTURAL_v1__MEMORY_RECONSTRUCTION.md"
)

_LAYOUT = (SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)
_WORK = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8)
_READ = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U7, SemanticZone.U8)

# Recovered examples preserve the mechanism-level distinctions surviving B2.
_RECOVERED: Mapping[str, Tuple[Axis, str]] = {
    "CA01": (Axis.MATERIAL_CONSTRUCTION, "iterative-resist-and-layer-construction-organizes-existing-presentation-fields-without-reducing-batik-to-wallpaper-or-claiming-a-specific-tradition-technique"),
    "CA04": (Axis.INFORMATION, "reusable-promotional-carrier-separates-stable-presentation-frame-from-swappable-existing-commercial-or-informational-payload-without-fake-antique-copy"),
    "CA08": (Axis.NARRATIVE_SEQUENCING, "staged-descent-depth-and-reveal-sequences-existing-information-without-literal-stone-stair-imitation-or-invented-chronology"),
    "CA10": (Axis.MATERIAL_CONSTRUCTION, "motif-is-structurally-integrated-into-the-presentation-field-rather-than-applied-as-detached-wallpaper"),
    "CA11": (Axis.FORM, "layered-interlocking-geometry-and-bounded-border-hierarchy-organize-existing-regions-without-copying-specific-ornamental-motifs"),
    "CA12": (Axis.SPACE, "radial-enclosure-and-modular-portable-construction-logic-organizes-existing-content-without-literal-building-replication"),
    "CA13": (Axis.FORM, "modular-cut-and-joined-geometric-units-build-a-field-from-parts-without-collapsing-to-a-generic-star-pattern"),
    "CA15": (Axis.MATERIAL_CONSTRUCTION, "narrow-band-like-modules-assemble-into-a-larger-coherent-field-without-copying-specific-textile-patterns-or-meanings"),
    "CA16": (Axis.SPACE, "reserved-negative-areas-are-created-by-structural-field-contrast-rather-than-color-alone-or-literal-textile-copy"),
    "CA17": (Axis.SPACE, "perimeter-gate-core-and-maze-like-access-zones-structure-existing-navigation-without-inventing-social-hierarchy-or-cultural-authority"),
    "CA18": (Axis.FORM, "controlled-asymmetry-and-local-variation-operate-inside-a-coherent-constructed-field-without-raster-texture-substitution"),
    "CA19": (Axis.MATERIAL_CONSTRUCTION, "joined-strip-like-modules-and-process-bound-surface-relations-form-a-coherent-field-without-claiming-or-copying-specific-production-technique"),
}

# For rows without surviving row-level mechanism prose, use deliberately bounded
# project translations. They are identity-distinct but make no universal claim.
_BOUNDED: Mapping[str, Tuple[Axis, str]] = {
    "CA09": (Axis.INFORMATION, "project-bounded-total-surface-composition-coordinates-dense-existing-signals-across-the-whole-frame-while-preserving-semantic-compartments-and-control-legibility"),
    "CA14": (Axis.SPACE, "project-bounded-enclosure-threshold-and-passage-translation-stages-existing-regions-without-claiming-specific-architectural-social-or-historical-meaning"),
    "CA20": (Axis.MATERIAL_CONSTRUCTION, "project-bounded-craft-and-construction-integration-keeps-form-surface-and-join-logic-coherent-without-claiming-a-universal-arts-and-crafts-rule"),
    "CA21": (Axis.FORM, "project-bounded-orthogonal-field-and-asymmetric-balance-translation-organizes-existing-content-without-making-color-blocks-the-sole-identity"),
    "CA22": (Axis.TYPOGRAPHY_SCRIPT, "project-bounded-geometric-poster-hierarchy-translation-uses-scale-crop-and-type-image-relations-without-copying-specific-posters-or-letterforms"),
    "CA23": (Axis.FORM, "project-bounded-continuous-organic-frame-translation-links-edges-openings-and-containers-without-copying-specific-ornament-or-built-work"),
    "CA24": (Axis.FORM, "project-bounded-stepped-geometric-and-streamlined-luxury-hierarchy-translation-uses-structure-not-decorative-stock-motifs"),
    "CA25": (Axis.INFORMATION, "project-bounded-expressive-poster-field-translation-allows-controlled-graphic-tension-around-existing-message-hierarchy-without-copying-specific-works"),
    "CA26": (Axis.FORM, "project-bounded-rectilinear-frame-and-integrated-ornamental-field-translation-keeps-ornament-subordinate-to-content-semantics"),
    "CA27": (Axis.FORM, "project-bounded-horizontal-flow-and-rounded-continuity-translation-guides-existing-reading-and-navigation-without-introducing-artificial-motion-or-delay"),
    "CA28": (Axis.SCALE_GRANULARITY, "project-bounded-human-scale-modular-and-component-coherence-translation-preserves-clear-part-to-whole-relations-without-product-copying"),
    "CA29": (Axis.MATERIAL_CONSTRUCTION, "project-bounded-layered-cut-field-translation-uses nested-positive-negative-shape-relations-without-copying-specific-mola-designs-or-cultural-symbols"),
    "CA30": (Axis.SPACE, "project-bounded-composed-open-field-and-framed-object-translation-balances-existing-content-islands-without-claiming-a-specific-site-or-social-program"),
    "CA32": (Axis.INFORMATION, "project-bounded-cinematic-poster-communication-translation-uses-bold-message-image-tension-for-existing-content-without-copying-specific-ICAIC-artworks"),
    "CA34": (Axis.SPACE, "project-bounded-structural-frame-and-collective-enclosure-translation-organizes-existing-regions-without-inventing-sacred-genealogical-or-cultural-meaning"),
    "CA35": (Axis.FORM, "project-bounded-large-field-boundary-and-repetition-translation-operates-as-composition-without-claiming-specific-siapo-technique-symbolism-or-provenance"),
    "CA36": (Axis.FORM, "project-bounded-large-field-boundary-and-grouped-mark-translation-operates-as-composition-without-claiming-specific-ngatu-technique-symbolism-or-provenance"),
}


def _identity(ref_id: str):
    axis, directive = (_RECOVERED.get(ref_id) or _BOUNDED[ref_id])
    mode = CULTURAL_TIER_A_EVIDENCE_MODE_BY_ID[ref_id]
    return mechanism(
        ref_id,
        "identity",
        axis,
        (
            f"cultural-tier-a-owner-scoped-reference evidence={mode}; {directive}; "
            "reference-projection-consumes-existing-semantic-state-only; "
            "project-abstraction-is-not-universal-cultural-truth"
        ),
        zones=_WORK,
        rank=94,
    )


def _build(ref_id: str) -> DNAUnit:
    name = CULTURAL_TIER_A_NAME_BY_ID[ref_id]
    slug = name.lower().replace(" ", "-").replace("&", "and").replace("’", "").replace("'", "")
    return unit(
        ref_id,
        kind=UnitKind.REFERENCE,
        family="Cultural Tier A",
        lineage=f"cultural-tier-a-{slug}",
        mechanisms=(
            _identity(ref_id),
            mechanism(
                ref_id,
                "semantic-firewall",
                Axis.INFORMATION,
                "presentation-may-not-invent-chronology-hierarchy-authority-relationships-confidence-translation-subgroup-technique-provenance-or-cultural-meaning-and-may-not-promote-engine-or-country-lens-into-reference-truth",
                zones=_WORK,
                rank=99,
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
                "wide-view-may-expand-the-reference-structural-relation-around-existing-content-without-changing-semantic-order-or-domain-state",
                zones=_LAYOUT,
                viewports=WIDE_VIEWPORTS,
                rank=78,
            ),
            mechanism(
                ref_id,
                "mobile-adaptation",
                Axis.ADAPTATION,
                "mobile-serializes-the-reference-into-explicit-bounded-structural-cues-without-hidden-critical-state-false-hierarchy-or-loss-of-content-order",
                zones=_LAYOUT,
                viewports=MOBILE_VIEWPORT,
                rank=90,
            ),
        ),
        provenance=_PROVENANCE,
        identity_survival="asset-off-structural-cultural-reference-without-universal-truth-claim",
    )


CULTURAL_TIER_A_REFERENCES: Tuple[DNAUnit, ...] = tuple(_build(item) for item in CULTURAL_TIER_A_IDS)
CULTURAL_TIER_A_BY_ID: Dict[str, DNAUnit] = {item.id: item for item in CULTURAL_TIER_A_REFERENCES}


def cultural_tier_a_asset_on_applicable(reference_id: str) -> bool:
    if reference_id not in CULTURAL_TIER_A_BY_ID:
        raise KeyError(reference_id)
    return reference_id in CULTURAL_TIER_A_ASSET_ON_APPLICABLE


def register_cultural_tier_a(registry) -> None:
    for reference in CULTURAL_TIER_A_REFERENCES:
        registry.register(reference)
