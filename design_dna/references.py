"""Design-DNA M2 proving slice.

Scope is intentionally narrow:
- all five locked Country-Web references (CW01-CW05);
- four adversarial Cultural Tier-S references selected for mechanism coverage;
- no new primitive IDs because the surviving locked metadata does not identify
  primitive dependencies for this slice.

This module is a conservative translation of surviving implementation-ready
fingerprints. It does not reconstruct unavailable row-by-row historical prose,
does not add production assets, and does not claim EQ4/browser evidence.
"""
from __future__ import annotations

from typing import Dict, Iterable, Tuple

from design_dna.models import (
    AbsenceState,
    Axis,
    AxisAbsence,
    DNAUnit,
    MechanismContract,
    SemanticZone,
    UnitKind,
)

COUNTRY_WEB_REFERENCE_IDS: Tuple[str, ...] = tuple(f"CW{i:02d}" for i in range(1, 6))
M2_CULTURAL_REFERENCE_IDS: Tuple[str, ...] = ("CS07", "CS08", "CS10", "CS17")
M2_PROVING_REFERENCE_IDS: Tuple[str, ...] = COUNTRY_WEB_REFERENCE_IDS + M2_CULTURAL_REFERENCE_IDS

# Execution-time audit: none of the selected proving references has a locked,
# explicit primitive dependency in the surviving canonical metadata.
M2_REQUIRED_PRIMITIVE_IDS: Tuple[str, ...] = ()

COUNTRY_WEB_ASSET_ON_NOT_APPLICABLE = frozenset({"CW02"})
COUNTRY_WEB_ASSET_ON_APPLICABLE = frozenset(COUNTRY_WEB_REFERENCE_IDS) - COUNTRY_WEB_ASSET_ON_NOT_APPLICABLE
M2_CULTURAL_ASSET_ON_APPLICABLE = frozenset(M2_CULTURAL_REFERENCE_IDS)
M2_ASSET_ON_APPLICABLE = COUNTRY_WEB_ASSET_ON_APPLICABLE | M2_CULTURAL_ASSET_ON_APPLICABLE
M2_ASSET_ON_NOT_APPLICABLE = COUNTRY_WEB_ASSET_ON_NOT_APPLICABLE

PROVENANCE_COUNTRY_WEB = (
    "docs/design-dna/archive/raw/"
    "MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_7_LOCK_CHECKPOINT_v1.md;"
    "docs/design-dna/archive/raw/"
    "MULTIMIND_DESIGN_DNA_WAVE_G_LOCK_CHECKPOINT_v1(20260902-074208).md"
)
PROVENANCE_CULTURAL = (
    "docs/design-dna/archive/raw/"
    "MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_6_LOCK_CHECKPOINT_v1.md;"
    "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_MIGRATION_BATCH_MAP_v1.md"
)
PROVENANCE_CKT = (
    PROVENANCE_CULTURAL
    + ";docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_WAVE_H_MD_FIRST_DEEP_EXTERNAL_RECOVERY_FORENSICS_v2__MEMORY_RECONSTRUCTION.md"
)

_ALL_VIEWPORTS = ("desktop", "tablet", "mobile")
_WIDE_VIEWPORTS = ("desktop", "tablet")
_MOBILE_VIEWPORT = ("mobile",)

_SHELL_WORK_ZONES = (
    SemanticZone.U1,
    SemanticZone.U2,
    SemanticZone.U3,
    SemanticZone.U4,
    SemanticZone.U5,
    SemanticZone.U6,
    SemanticZone.U8,
)
_WORK_ZONES = (
    SemanticZone.U2,
    SemanticZone.U3,
    SemanticZone.U4,
    SemanticZone.U5,
    SemanticZone.U6,
    SemanticZone.U8,
)
_LAYOUT_ZONES = (
    SemanticZone.U1,
    SemanticZone.U2,
    SemanticZone.U3,
    SemanticZone.U4,
    SemanticZone.U8,
)
_READING_AND_WORK_ZONES = (
    SemanticZone.U2,
    SemanticZone.U3,
    SemanticZone.U4,
    SemanticZone.U7,
    SemanticZone.U8,
)


def _mechanism(
    reference_id: str,
    suffix: str,
    axis: Axis,
    directive: str,
    *,
    zones: Tuple[SemanticZone, ...],
    fallback: str = "",
    rank: int = 80,
    viewports: Tuple[str, ...] = _ALL_VIEWPORTS,
    accessibility_safe: bool = True,
    reading_safe: bool = True,
) -> MechanismContract:
    return MechanismContract(
        id=f"{reference_id.lower()}-{suffix}",
        axis=axis,
        zones=zones,
        directive=directive,
        fallback_directive=fallback,
        ownership_rank=rank,
        viewports=viewports,
        states=("all",),
        accessibility_safe=accessibility_safe,
        reading_safe=reading_safe,
    )


def _absences(mechanisms: Iterable[MechanismContract]) -> Tuple[AxisAbsence, ...]:
    covered = {item.axis for item in mechanisms}
    return tuple(
        AxisAbsence(axis=axis, state=AbsenceState.NOT_APPLICABLE)
        for axis in Axis
        if axis not in covered
    )


def _reference(
    reference_id: str,
    family: str,
    lineage: str,
    mechanisms: Tuple[MechanismContract, ...],
    *,
    provenance: str,
) -> DNAUnit:
    return DNAUnit(
        id=reference_id,
        kind=UnitKind.REFERENCE,
        family=family,
        lineage=lineage,
        provenance_pointer=provenance,
        mechanisms=mechanisms,
        axis_absences=_absences(mechanisms),
        assets=(),
        identity_survival="structural-reference-without-assets",
    )


M2_PROVING_REFERENCES: Tuple[DNAUnit, ...] = (
    _reference(
        "CW01",
        "Switzerland — Swiss institutional/product typographic-system lineage",
        "country-web-scoped-digital-lineage",
        (
            _mechanism("CW01", "role-grid", Axis.INFORMATION, "digital-role-hierarchy-with-consistent-alignment-and-grid-across-existing-information", zones=_WORK_ZONES, rank=88),
            _mechanism("CW01", "typographic-role", Axis.TYPOGRAPHY_SCRIPT, "typographic-role-consistency-and-measured-hierarchy-without-national-decoration", zones=_SHELL_WORK_ZONES, rank=90),
            _mechanism("CW01", "ordered-space", Axis.SPACE, "ordered-digital-grid-spacing-with-explicit-role-alignment", zones=_LAYOUT_ZONES, rank=82),
            _mechanism("CW01", "wide-adaptation", Axis.ADAPTATION, "wide-view-preserves-role-grid-and-cross-view-alignment-consistency", zones=_LAYOUT_ZONES, rank=80, viewports=_WIDE_VIEWPORTS),
            _mechanism("CW01", "mobile-adaptation", Axis.ADAPTATION, "mobile-recomposes-grid-into-ordered-flow-while-preserving-role-and-alignment-identity", zones=_LAYOUT_ZONES, rank=84, viewports=_MOBILE_VIEWPORT),
        ),
        provenance=PROVENANCE_COUNTRY_WEB,
    ),
    _reference(
        "CW02",
        "USA — U.S. product-web/SaaS design-system lineage",
        "country-web-scoped-digital-lineage",
        (
            _mechanism("CW02", "component-task", Axis.FORM, "reusable-task-component-boundaries-with-consistent-functional-role", zones=_WORK_ZONES, rank=82),
            _mechanism("CW02", "workflow-hierarchy", Axis.INFORMATION, "task-first-component-hierarchy-exposing-existing-workflow-and-state-without-reprioritizing-domain-truth", zones=_WORK_ZONES, rank=88),
            _mechanism("CW02", "state-grammar", Axis.INTERACTION, "reusable-action-state-grammar-with-visible-existing-loading-error-success-and-disabled-state-continuity", zones=(SemanticZone.U4, SemanticZone.U5, SemanticZone.U6), rank=90),
            _mechanism("CW02", "task-sequence", Axis.NARRATIVE_SEQUENCING, "task-to-action-to-existing-state-sequencing-without-inventing-workflow-steps", zones=(SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6), rank=78),
            _mechanism("CW02", "wide-adaptation", Axis.ADAPTATION, "wide-layout-reuses-component-and-state-grammar-across-task-regions", zones=_LAYOUT_ZONES, rank=78, viewports=_WIDE_VIEWPORTS),
            _mechanism("CW02", "mobile-adaptation", Axis.ADAPTATION, "mobile-reflows-components-without-changing-task-state-or-action-grammar", zones=_LAYOUT_ZONES, rank=84, viewports=_MOBILE_VIEWPORT),
        ),
        provenance=PROVENANCE_COUNTRY_WEB,
    ),
    _reference(
        "CW03",
        "Japan — Japanese commerce/public-service high-information lineage",
        "country-web-scoped-digital-lineage",
        (
            _mechanism("CW03", "controlled-density", Axis.INFORMATION, "high-simultaneous-information-availability-with-explicit-local-grouping-scanability-hierarchy-and-actionable-access", zones=_WORK_ZONES, rank=92),
            _mechanism("CW03", "group-space-wide", Axis.SPACE, "compact-wide-information-regions-with-explicit-group-boundaries-and-legibility-floor", zones=_LAYOUT_ZONES, rank=82, viewports=_WIDE_VIEWPORTS),
            _mechanism("CW03", "group-space-mobile", Axis.SPACE, "mobile-serializes-local-groups-with-explicit-boundaries-never-shrinking-everything-to-preserve-density", zones=_LAYOUT_ZONES, rank=86, viewports=_MOBILE_VIEWPORT),
            _mechanism("CW03", "granularity", Axis.SCALE_GRANULARITY, "compact-but-legible-local-group-granularity-without-small-font-or-clutter-substitution", zones=_WORK_ZONES, rank=84),
            _mechanism("CW03", "mobile-adaptation", Axis.ADAPTATION, "mobile-preserves-controlled-information-access-through-group-recomposition-not-desktop-shrink", zones=_LAYOUT_ZONES, rank=88, viewports=_MOBILE_VIEWPORT),
            _mechanism("CW03", "wide-adaptation", Axis.ADAPTATION, "wide-view-preserves-simultaneous-group-access-with-clear-local-hierarchy", zones=_LAYOUT_ZONES, rank=82, viewports=_WIDE_VIEWPORTS),
        ),
        provenance=PROVENANCE_COUNTRY_WEB,
    ),
    _reference(
        "CW04",
        "China — Chinese service-platform ecosystem convergence lineage",
        "country-web-scoped-digital-lineage",
        (
            _mechanism("CW04", "service-clusters", Axis.INFORMATION, "bounded-multi-service-grouping-with-explicit-service-and-context-boundaries", zones=_WORK_ZONES, rank=92),
            _mechanism("CW04", "service-continuity", Axis.INTERACTION, "service-context-continuity-across-existing-actions-and-states-without-inventing-services-or-permissions", zones=(SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8), rank=90),
            _mechanism("CW04", "cluster-space", Axis.SPACE, "separated-service-clusters-with-bounded-convergence-never-giant-undifferentiated-launcher", zones=_LAYOUT_ZONES, rank=84),
            _mechanism("CW04", "wide-adaptation", Axis.ADAPTATION, "wide-view-keeps-service-clusters-visible-with-explicit-context-boundaries", zones=_LAYOUT_ZONES, rank=82, viewports=_WIDE_VIEWPORTS),
            _mechanism("CW04", "mobile-adaptation", Axis.ADAPTATION, "mobile-serializes-service-clusters-while-preserving-context-continuity-and-return-paths", zones=_LAYOUT_ZONES, rank=88, viewports=_MOBILE_VIEWPORT),
        ),
        provenance=PROVENANCE_COUNTRY_WEB,
    ),
    _reference(
        "CW05",
        "Aotearoa New Zealand — public-cultural bilingual/bicultural integration lineage",
        "country-web-scoped-digital-lineage",
        (
            _mechanism("CW05", "semantic-pairing", Axis.INFORMATION, "governed-bilingual-semantic-pairing-with-equivalent-existing-role-and-priority-never-inventing-translation", zones=_WORK_ZONES, rank=92),
            _mechanism("CW05", "language-role", Axis.TYPOGRAPHY_SCRIPT, "paired-language-role-presentation-with-correct-language-metadata-and-no-fabricated-equivalence", zones=_READING_AND_WORK_ZONES, rank=94),
            _mechanism("CW05", "language-state", Axis.INTERACTION, "language-state-continuity-across-existing-navigation-actions-and-system-state", zones=(SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8), rank=90),
            _mechanism("CW05", "wide-adaptation", Axis.ADAPTATION, "wide-view-keeps-associated-language-roles-visibly-paired-with-semantic-equivalence", zones=_LAYOUT_ZONES, rank=82, viewports=_WIDE_VIEWPORTS),
            _mechanism("CW05", "mobile-adaptation", Axis.ADAPTATION, "mobile-stacks-associated-language-roles-with-continuity-markers-without-losing-pairing", zones=_LAYOUT_ZONES, rank=88, viewports=_MOBILE_VIEWPORT),
        ),
        provenance=PROVENANCE_COUNTRY_WEB,
    ),
    _reference(
        "CS07",
        "Swiss International Typographic",
        "cultural-tier-s-swiss-international-typographic",
        (
            _mechanism("CS07", "asymmetric-grid", Axis.SPACE, "cultural-typographic-composition-uses-rational-grid-with-bounded-asymmetric-tension", zones=_LAYOUT_ZONES, rank=86),
            _mechanism("CS07", "hierarchy", Axis.TYPOGRAPHY_SCRIPT, "cultural-reference-typographic-hierarchy-through-scale-weight-spacing-and-alignment-not-country-web-system-identity", zones=_READING_AND_WORK_ZONES, rank=92),
            _mechanism("CS07", "restrained-form", Axis.FORM, "restrained-geometric-typographic-composition-without-decorative-national-symbols", zones=_LAYOUT_ZONES, rank=78),
            _mechanism("CS07", "mobile-adaptation", Axis.ADAPTATION, "mobile-preserves-typographic-hierarchy-and-asymmetric-grid-tension-through-ordered-recomposition", zones=_LAYOUT_ZONES, rank=84, viewports=_MOBILE_VIEWPORT),
            _mechanism("CS07", "wide-adaptation", Axis.ADAPTATION, "wide-view-preserves-asymmetric-grid-and-hierarchical-typographic-relations", zones=_LAYOUT_ZONES, rank=80, viewports=_WIDE_VIEWPORTS),
        ),
        provenance=PROVENANCE_CULTURAL,
    ),
    _reference(
        "CS08",
        "Horta Continuous Organic",
        "cultural-tier-s-horta-continuous-organic",
        (
            _mechanism("CS08", "continuous-organic-form", Axis.FORM, "continuous-organic-structural-contour-links-bounded-regions-without-applied-floral-wallpaper", zones=_LAYOUT_ZONES + (SemanticZone.U7,), fallback="reduced-organic-edge-continuity", rank=90, reading_safe=False),
            _mechanism("CS08", "flowing-space", Axis.SPACE, "flowing-spatial-continuity-around-content-islands-with-protected-content-clearance", zones=_LAYOUT_ZONES + (SemanticZone.U7,), fallback="linearized-content-clearance-with-organic-edge-cue", rank=86, reading_safe=False),
            _mechanism("CS08", "structural-ornament", Axis.MATERIAL_CONSTRUCTION, "ornament-expressed-as-structural-continuity-and-junction-logic-not-texture-pack", zones=_LAYOUT_ZONES, rank=78),
            _mechanism("CS08", "mobile-adaptation", Axis.ADAPTATION, "mobile-reduces-organic-complexity-to-bounded-continuity-cues-with-content-clearance", zones=_LAYOUT_ZONES, rank=86, viewports=_MOBILE_VIEWPORT),
            _mechanism("CS08", "wide-adaptation", Axis.ADAPTATION, "wide-view-allows-continuous-organic-routing-between-bounded-content-regions", zones=_LAYOUT_ZONES, rank=80, viewports=_WIDE_VIEWPORTS),
        ),
        provenance=PROVENANCE_CULTURAL,
    ),
    _reference(
        "CS10",
        "Futurist Typography",
        "cultural-tier-s-futurist-typography",
        (
            _mechanism("CS10", "directional-type", Axis.TYPOGRAPHY_SCRIPT, "directional-typographic-force-through-scale-angle-spacing-and-grouping-without-changing-text-meaning", zones=_READING_AND_WORK_ZONES, fallback="static-directional-typographic-hierarchy", rank=94, reading_safe=False),
            _mechanism("CS10", "asymmetric-force", Axis.SPACE, "asymmetric-directional-field-with-bounded-content-anchors-and-legibility-clearance", zones=_LAYOUT_ZONES + (SemanticZone.U7,), fallback="reduced-asymmetric-field-with-stable-reading-column", rank=88, reading_safe=False),
            _mechanism("CS10", "kinetic-cue", Axis.MOTION_TEMPORAL, "presentation-only-directional-kinetic-cue-never-mutating-application-state-or-semantic-order", zones=(SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8), fallback="static-directional-force-cue", rank=90, accessibility_safe=False, reading_safe=False),
            _mechanism("CS10", "directional-form", Axis.FORM, "diagonal-directional-form-punctuation-without-obscuring-actions-or-status", zones=_LAYOUT_ZONES, fallback="reduced-directional-form-punctuation", rank=84, accessibility_safe=False),
            _mechanism("CS10", "mobile-adaptation", Axis.ADAPTATION, "mobile-serializes-directional-force-into-bounded-vertical-punctuation-with-stable-reading-order", zones=_LAYOUT_ZONES, rank=90, viewports=_MOBILE_VIEWPORT),
            _mechanism("CS10", "wide-adaptation", Axis.ADAPTATION, "wide-view-allows-bounded-multidirectional-typographic-force-around-stable-content-anchors", zones=_LAYOUT_ZONES, rank=82, viewports=_WIDE_VIEWPORTS),
        ),
        provenance=PROVENANCE_CULTURAL,
    ),
    _reference(
        "CS17",
        "Continuous Knowledge Traversal",
        "project-abstraction-with-recovered-vanuatu-sand-drawing-lineage",
        (
            _mechanism("CS17", "constrained-traversal", Axis.NARRATIVE_SEQUENCING, "continuous-constrained-traversal-through-existing-knowledge-anchors-without-inventing-order-relationships-or-meaning", zones=_READING_AND_WORK_ZONES, rank=94),
            _mechanism("CS17", "traversal-space", Axis.SPACE, "implied-grid-and-continuous-path-connect-existing-anchors-with-protected-reading-clearance", zones=_LAYOUT_ZONES + (SemanticZone.U7,), fallback="linear-continuous-trace-with-reading-clearance", rank=88, reading_safe=False),
            _mechanism("CS17", "anchor-information", Axis.INFORMATION, "knowledge-anchors-remain-locally-readable-while-continuity-is-exposed-without-fabricated-hierarchy", zones=_READING_AND_WORK_ZONES, rank=90),
            _mechanism("CS17", "traversal-interaction", Axis.INTERACTION, "interaction-preserves-continuity-between-existing-semantic-anchors-with-reversible-local-navigation", zones=(SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U7, SemanticZone.U8), rank=86),
            _mechanism("CS17", "mobile-adaptation", Axis.ADAPTATION, "mobile-linearizes-two-dimensional-traversal-into-continuous-ordered-trace-without-changing-semantic-relations", zones=_LAYOUT_ZONES, rank=90, viewports=_MOBILE_VIEWPORT),
            _mechanism("CS17", "wide-adaptation", Axis.ADAPTATION, "wide-view-preserves-bounded-grid-traversal-and-local-anchor-legibility", zones=_LAYOUT_ZONES, rank=82, viewports=_WIDE_VIEWPORTS),
        ),
        provenance=PROVENANCE_CKT,
    ),
)

M2_REFERENCE_BY_ID: Dict[str, DNAUnit] = {unit.id: unit for unit in M2_PROVING_REFERENCES}

if tuple(M2_REFERENCE_BY_ID) != M2_PROVING_REFERENCE_IDS:
    raise RuntimeError("M2 proving reference catalog order/membership drift")


def m2_reference_asset_on_applicable(reference_id: str) -> bool:
    """Return locked asset-on applicability for an M2 proving reference."""
    if reference_id not in M2_REFERENCE_BY_ID:
        raise KeyError(reference_id)
    return reference_id in M2_ASSET_ON_APPLICABLE


def register_m2_proving_references(registry) -> None:
    """Register the M2 proving references into an existing DNARegistry."""
    for unit in M2_PROVING_REFERENCES:
        registry.register(unit)
