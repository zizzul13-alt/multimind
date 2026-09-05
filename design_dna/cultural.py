"""Design-DNA M3: complete additive Cultural Tier-S family.

The exact historical row-by-row Batch-6 prose is not available in the repository.
This module therefore preserves the locked 16-member identity set and translates
surviving names, hard laws, collision requirements and provenance into conservative,
host-neutral structural contracts. Four M2-proven units are reused verbatim.
"""
from __future__ import annotations

from typing import Dict, Tuple

from design_dna.catalog import MOBILE_VIEWPORT, WIDE_VIEWPORTS, mechanism, unit
from design_dna.models import Axis, DNAUnit, SemanticZone, UnitKind
from design_dna.references import M2_REFERENCE_BY_ID

CULTURAL_TIER_S_IDS: Tuple[str, ...] = (
    "CS01", "CS02", "CS03", "CS04", "CS05", "CS06", "CS07", "CS08",
    "CS09", "CS10", "CS11", "CS12", "CS13", "CS14", "CS16", "CS17",
)
CULTURAL_TIER_S_HISTORICAL_NON_ADDITIVE = ("CS15",)
CULTURAL_TIER_S_M2_REUSED_IDS = ("CS07", "CS08", "CS10", "CS17")
CULTURAL_TIER_S_ASSET_ON_APPLICABLE = frozenset(CULTURAL_TIER_S_IDS)

PROVENANCE_TIER_S = (
    "docs/design-dna/archive/raw/"
    "MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_6_LOCK_CHECKPOINT_v1.md;"
    "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_MIGRATION_BATCH_MAP_v1.md;"
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_B1_TIER_S_v1__MEMORY_RECONSTRUCTION.md"
)

_LAYOUT = (SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)
_WORK = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8)
_READ_WORK = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U7, SemanticZone.U8)
_INTERACTION = (SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8)


def _reference(ref_id: str, family: str, lineage: str, mechanisms):
    return unit(
        ref_id,
        kind=UnitKind.REFERENCE,
        family=family,
        lineage=lineage,
        mechanisms=tuple(mechanisms),
        provenance=PROVENANCE_TIER_S,
        identity_survival="structural-cultural-reference-without-assets",
    )


_NEW_TIER_S: Tuple[DNAUnit, ...] = (
    _reference(
        "CS01", "Javanese Axial", "cultural-tier-s-javanese-axial",
        (
            mechanism("CS01", "axial-space", Axis.SPACE, "bounded-axial-composition-aligns-existing-content-regions-around-a-clear-primary-spatial-spine-without-inventing-authority", zones=_LAYOUT, rank=90),
            mechanism("CS01", "threshold-sequence", Axis.NARRATIVE_SEQUENCING, "presentation-thresholds-stage-existing-sections-along-the-axial-spine-without-inventing-chronology-ritual-or-semantic-rank", zones=_WORK, rank=86),
            mechanism("CS01", "balanced-form", Axis.FORM, "balanced-framing-and-repeated-structural-bays-reinforce-the-axis-without-cultural-motif-substitution", zones=_LAYOUT, rank=82),
            mechanism("CS01", "wide-adaptation", Axis.ADAPTATION, "wide-view-preserves-the-primary-axis-and-bounded-threshold-relations", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=80),
            mechanism("CS01", "mobile-adaptation", Axis.ADAPTATION, "mobile-linearizes-the-axis-into-ordered-thresholds-while-preserving-section-identity-and-semantic-order", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=86),
        ),
    ),
    _reference(
        "CS02", "Balinese Subak", "cultural-tier-s-balinese-subak",
        (
            mechanism("CS02", "distributed-network", Axis.INFORMATION, "distributed-peer-linked-grouping-exposes-only-existing-relations-and-dependencies-without-inventing-social-hierarchy-resource-rights-or-authority", zones=_WORK, rank=90),
            mechanism("CS02", "branching-space", Axis.SPACE, "branching-connected-regions-balance-local-autonomy-and-whole-system-continuity-without-literal-landscape-imitation", zones=_LAYOUT, rank=84),
            mechanism("CS02", "coordination-sequence", Axis.NARRATIVE_SEQUENCING, "coordinated-branch-to-shared-context-sequencing-follows-existing-application-relations-only", zones=_WORK, rank=82),
            mechanism("CS02", "wide-adaptation", Axis.ADAPTATION, "wide-view-shows-bounded-branching-relations-and-shared-context-concurrently", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=80),
            mechanism("CS02", "mobile-adaptation", Axis.ADAPTATION, "mobile-serializes-branches-with-explicit-return-to-shared-context-without-collapsing-peer-relations-into-false-hierarchy", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=88),
        ),
    ),
    _reference(
        "CS03", "Japan Print / Ink", "cultural-tier-s-japan-print-ink",
        (
            mechanism("CS03", "ink-mass", Axis.FORM, "high-contrast-solid-and-open-form-masses-create-compositional-emphasis-without-literal-print-motif-or-illustration-copying", zones=_LAYOUT, rank=88),
            mechanism("CS03", "negative-space", Axis.SPACE, "active-negative-space-and-asymmetric-cropping-frame-existing-content-with-protected-legibility", zones=_READ_WORK, rank=90),
            mechanism("CS03", "restrained-color", Axis.COLOR, "restrained-value-contrast-supports-ink-like-mass-relations-without-making-palette-the-reference-identity", zones=_LAYOUT, rank=72),
            mechanism("CS03", "wide-adaptation", Axis.ADAPTATION, "wide-view-preserves-asymmetric-mass-to-void-relations-and-bounded-cropping", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=80),
            mechanism("CS03", "mobile-adaptation", Axis.ADAPTATION, "mobile-recomposes-mass-and-negative-space-around-linear-content-without-cropping-critical-information", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=88),
        ),
    ),
    _reference(
        "CS04", "Rinpa", "cultural-tier-s-rinpa",
        (
            mechanism("CS04", "paired-fields", Axis.FORM, "paired-or-counterweighted-flat-structural-fields-create-asymmetric-balance-without-motif-pack-substitution", zones=_LAYOUT, rank=88),
            mechanism("CS04", "field-space", Axis.SPACE, "broad-open-fields-and-bounded-clusters-create-deliberate-intervals-around-existing-content", zones=_READ_WORK, rank=86),
            mechanism("CS04", "repeat-variation", Axis.NARRATIVE_SEQUENCING, "bounded-repetition-with-variation-links-existing-peer-sections-without-implying-new-chronology-or-authority", zones=_WORK, rank=78),
            mechanism("CS04", "wide-adaptation", Axis.ADAPTATION, "wide-view-maintains-counterweighted-fields-and-deliberate-open-intervals", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=78),
            mechanism("CS04", "mobile-adaptation", Axis.ADAPTATION, "mobile-stacks-counterweighted-fields-with-preserved-interval-rhythm-and-no-loss-of-content-order", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=86),
        ),
    ),
    _reference(
        "CS05", "Suzhou Garden", "cultural-tier-s-suzhou-garden",
        (
            mechanism("CS05", "framed-view", Axis.SPACE, "bounded-framing-reveals-existing-content-through-nested-viewports-and-clear-occlusion-limits-without-scenery-wallpaper", zones=_LAYOUT, rank=90),
            mechanism("CS05", "reveal-sequence", Axis.NARRATIVE_SEQUENCING, "progressive-spatial-reveal-orders-only-existing-sections-and-never-fabricates-chronology-meaning-or-hidden-content", zones=_WORK, rank=88),
            mechanism("CS05", "layered-form", Axis.FORM, "foreground-midground-boundary-planes-create-depth-cues-without-literal-garden-motif-copying", zones=_LAYOUT, rank=78),
            mechanism("CS05", "wide-adaptation", Axis.ADAPTATION, "wide-view-supports-multiple-bounded-framed-relations-with-clear-navigation-continuity", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=80),
            mechanism("CS05", "mobile-adaptation", Axis.ADAPTATION, "mobile-converts-nested-framing-to-sequential-reveal-with-explicit-backtracking-and-no-hidden-critical-state", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=90),
        ),
    ),
    _reference(
        "CS06", "Hangeul Structural", "cultural-tier-s-hangeul-structural",
        (
            mechanism("CS06", "block-structure", Axis.FORM, "modular-block-composition-uses-balanced-internal-relations-as-structural-geometry-without-substituting-or-altering-user-text", zones=_LAYOUT, rank=90),
            mechanism("CS06", "script-safety", Axis.TYPOGRAPHY_SCRIPT, "typographic-structure-respects-actual-script-language-and-reading-order-and-never-fabricates-hangeul-or-transliteration", zones=_READ_WORK, rank=96),
            mechanism("CS06", "modular-scale", Axis.SCALE_GRANULARITY, "nested-module-scale-preserves-whole-to-part-legibility-without-forcing-text-into-decorative-glyph-shapes", zones=_WORK, rank=82),
            mechanism("CS06", "wide-adaptation", Axis.ADAPTATION, "wide-view-uses-modular-block-relations-across-existing-content-groups-with-script-safety", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=80),
            mechanism("CS06", "mobile-adaptation", Axis.ADAPTATION, "mobile-linearizes-modules-while-preserving-internal-grouping-language-metadata-and-reading-order", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=88),
        ),
    ),
    _reference(
        "CS09", "Czech Cubist Space", "cultural-tier-s-czech-cubist-space",
        (
            mechanism("CS09", "faceted-form", Axis.FORM, "faceted-angular-planes-articulate-container-boundaries-without-turning-content-into-illegible-decoration", zones=_LAYOUT, rank=90),
            mechanism("CS09", "angular-space", Axis.SPACE, "bounded-oblique-spatial-tension-and-interlocking-planes-preserve-content-clearance-and-semantic-order", zones=_LAYOUT, rank=88),
            mechanism("CS09", "construction", Axis.MATERIAL_CONSTRUCTION, "structural-plane-intersections-read-as-construction-logic-not-applied-cubist-texture", zones=_LAYOUT, rank=76),
            mechanism("CS09", "wide-adaptation", Axis.ADAPTATION, "wide-view-supports-interlocking-faceted-regions-with-bounded-oblique-tension", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=80),
            mechanism("CS09", "mobile-adaptation", Axis.ADAPTATION, "mobile-reduces-oblique-overlap-to-faceted-edge-and-section-cues-without-content-collision", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=88),
        ),
    ),
    _reference(
        "CS11", "Mexico '68", "cultural-tier-s-mexico-68",
        (
            mechanism("CS11", "line-rhythm", Axis.FORM, "concentric-and-parallel-line-rhythm-builds-structural-emphasis-without-copying-event-marks-symbols-or-cultural-motifs", zones=_LAYOUT, rank=88),
            mechanism("CS11", "optical-type", Axis.TYPOGRAPHY_SCRIPT, "high-contrast-optical-typographic-framing-preserves-text-content-language-and-reading-order", zones=_READ_WORK, fallback="static-high-contrast-typographic-framing", rank=92, accessibility_safe=False),
            mechanism("CS11", "pulse", Axis.MOTION_TEMPORAL, "optional-presentation-only-line-pulse-never-delays-content-or-mutates-state", zones=(SemanticZone.U1, SemanticZone.U2, SemanticZone.U8), fallback="static-line-rhythm", rank=72, accessibility_safe=False, reading_safe=False),
            mechanism("CS11", "wide-adaptation", Axis.ADAPTATION, "wide-view-allows-broader-line-rhythm-around-bounded-content-fields", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=78),
            mechanism("CS11", "mobile-adaptation", Axis.ADAPTATION, "mobile-reduces-line-frequency-and-keeps-optical-framing-outside-critical-reading-and-controls", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=90),
        ),
    ),
    _reference(
        "CS12", "Neo-Concrete", "cultural-tier-s-neo-concrete",
        (
            mechanism("CS12", "relational-geometry", Axis.FORM, "relational-geometric-elements-compose-around-existing-content-as-bounded-part-whole-relationships-not-abstract-wallpaper", zones=_LAYOUT, rank=88),
            mechanism("CS12", "participatory-feedback", Axis.INTERACTION, "presentation-feedback-may-reorient-visual-relations-after-existing-user-actions-but-never-add-actions-change-permissions-or-mutate-domain-state", zones=_INTERACTION, fallback="static-relational-geometry", rank=86),
            mechanism("CS12", "bounded-motion", Axis.MOTION_TEMPORAL, "optional-reorientation-is-immediate-presentation-feedback-not-added-wait-time-or-semantic-transition", zones=(SemanticZone.U3, SemanticZone.U4, SemanticZone.U8), fallback="static-relational-geometry", rank=70, accessibility_safe=False, reading_safe=False),
            mechanism("CS12", "wide-adaptation", Axis.ADAPTATION, "wide-view-distributes-relational-elements-around-existing-content-regions-with-clear-action-boundaries", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=80),
            mechanism("CS12", "mobile-adaptation", Axis.ADAPTATION, "mobile-reduces-relational-reorientation-to-static-or-local-feedback-without-reordering-application-state", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=90),
        ),
    ),
    _reference(
        "CS13", "MASP", "cultural-tier-s-masp",
        (
            mechanism("CS13", "elevated-frame", Axis.FORM, "strong-primary-frame-and-suspended-subframes-separate-shell-from-content-without-inventing-institutional-hierarchy", zones=_LAYOUT, rank=90),
            mechanism("CS13", "open-span", Axis.SPACE, "open-span-spacing-keeps-primary-work-surface-visually-clear-beneath-or-within-structural-frames", zones=_LAYOUT, rank=88),
            mechanism("CS13", "display-plane", Axis.MATERIAL_CONSTRUCTION, "thin-suspended-display-planes-read-as-structural-support-logic-not-museum-prop-or-texture", zones=(SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8), rank=78),
            mechanism("CS13", "wide-adaptation", Axis.ADAPTATION, "wide-view-preserves-primary-frame-open-span-and-suspended-plane-relations", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=80),
            mechanism("CS13", "mobile-adaptation", Axis.ADAPTATION, "mobile-converts-suspended-plane-relations-to-stacked-framed-panels-while-preserving-open-clearance", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=88),
        ),
    ),
    _reference(
        "CS14", "Quipu", "cultural-tier-s-quipu",
        (
            mechanism("CS14", "strand-topology", Axis.INFORMATION, "strand-and-node-topology-maps-only-existing-relations-and-groupings-and-never-encodes-invented-cultural-meaning-data-or-hierarchy", zones=_WORK, rank=94),
            mechanism("CS14", "relational-sequence", Axis.NARRATIVE_SEQUENCING, "branch-and-return-traversal-follows-existing-relational-structure-without-inventing-chronology-or-causality", zones=_WORK, rank=90),
            mechanism("CS14", "structural-symbol", Axis.SYMBOL_ICONOGRAPHY, "abstract-node-and-strand-cues-serve-relational-structure-only-and-do-not-claim-literal-quipu-encoding", zones=(SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8), rank=82),
            mechanism("CS14", "wide-adaptation", Axis.ADAPTATION, "wide-view-shows-bounded-branching-strands-and-cross-relations-where-the-application-already-has-them", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=82),
            mechanism("CS14", "mobile-adaptation", Axis.ADAPTATION, "mobile-linearizes-strands-into-indented-relational-traces-with-explicit-return-links-and-no-fabricated-order", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=92),
        ),
    ),
    _reference(
        "CS16", "Marshallese Navigation", "cultural-tier-s-marshallese-navigation",
        (
            mechanism("CS16", "orientation-field", Axis.SPACE, "relational-orientation-field-positions-existing-sections-by-application-defined-nearness-direction-or-linkage-only-without-geographic-claim", zones=_LAYOUT, rank=92),
            mechanism("CS16", "navigation-relations", Axis.INFORMATION, "navigation-lines-and-reference-points-expose-existing-links-and-destinations-without-inventing-route-authority-geography-or-cultural-meaning", zones=_WORK, rank=94),
            mechanism("CS16", "traversal", Axis.NARRATIVE_SEQUENCING, "orientation-to-destination-traversal-follows-existing-navigation-state-and-keeps-return-context-visible", zones=_WORK, rank=88),
            mechanism("CS16", "wide-adaptation", Axis.ADAPTATION, "wide-view-may-show-multiple-existing-orientation-relations-concurrently-with-clear-reference-points", zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=82),
            mechanism("CS16", "mobile-adaptation", Axis.ADAPTATION, "mobile-serializes-orientation-relations-into-stepwise-navigation-with-persistent-origin-and-return-context", zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=92),
        ),
    ),
)

_NEW_BY_ID: Dict[str, DNAUnit] = {item.id: item for item in _NEW_TIER_S}

CULTURAL_TIER_S_REFERENCES: Tuple[DNAUnit, ...] = tuple(
    M2_REFERENCE_BY_ID[item_id] if item_id in CULTURAL_TIER_S_M2_REUSED_IDS else _NEW_BY_ID[item_id]
    for item_id in CULTURAL_TIER_S_IDS
)
CULTURAL_TIER_S_BY_ID: Dict[str, DNAUnit] = {item.id: item for item in CULTURAL_TIER_S_REFERENCES}


def cultural_tier_s_asset_on_applicable(reference_id: str) -> bool:
    if reference_id not in CULTURAL_TIER_S_BY_ID:
        raise KeyError(reference_id)
    return True


def register_cultural_tier_s(registry) -> None:
    for reference in CULTURAL_TIER_S_REFERENCES:
        registry.register(reference)
