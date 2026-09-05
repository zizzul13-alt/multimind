"""Design-DNA M10: reconstructed named-material Track M_R reference corpus.

Track M_R is the accepted 25-member Route-B reconstructed corpus. It is not the
lost historical Track M and it is not the normalized M1-M15 material-engine
catalog. The runtime stays declarative and host-neutral; selector-sensitive
research contracts are represented as bounded static projection policies rather
than pretending CompositionRequest.modifiers already implement a branch engine.
"""
from __future__ import annotations

from typing import Dict, Mapping, Tuple

from design_dna.catalog import MOBILE_VIEWPORT, WIDE_VIEWPORTS, mechanism, unit
from design_dna.models import Axis, DNAUnit, SemanticZone, UnitKind

TRACK_M_R_IDS: Tuple[str, ...] = tuple(f"MR-{index:03d}" for index in range(1, 26))

TRACK_M_R_NAME_BY_ID: Mapping[str, str] = {
    "MR-001": "Aklan Piña",
    "MR-002": "Batik",
    "MR-003": "Khayamiya",
    "MR-004": "Damascene metal inlay",
    "MR-005": "Masi",
    "MR-006": "Siapo",
    "MR-007": "Ngatu",
    "MR-008": "Tukutuku",
    "MR-009": "Jamdani",
    "MR-010": "Shyrdak",
    "MR-011": "Zellij",
    "MR-012": "Kente",
    "MR-013": "Adire",
    "MR-014": "Kuba textile",
    "MR-015": "Bògòlanfini",
    "MR-016": "Guna Mola",
    "MR-017": "Yakan weaving",
    "MR-018": "Turkmen carpet",
    "MR-019": "Baganda barkcloth",
    "MR-020": "Sekishu-Banshi / Washi",
    "MR-021": "Traditional Japanese wooden-architecture conservation skills",
    "MR-022": "Art of dry stone construction",
    "MR-023": "Japanese urushi",
    "MR-024": "Raku ware",
    "MR-025": "Murano mezza filigrana",
}

TRACK_M_R_RECOVERED_EXAMPLE_IDS = frozenset({
    "MR-002", "MR-003", "MR-009", "MR-013",
    "MR-017", "MR-019", "MR-023", "MR-025",
})
TRACK_M_R_V6_HARDENED_IDS = frozenset({
    "MR-004", "MR-005", "MR-006", "MR-012", "MR-014", "MR-018", "MR-021",
})

TRACK_M_R_EVIDENCE_MODE_BY_ID: Mapping[str, str] = {
    ref_id: (
        "V6_SELECTOR_HARDENED"
        if ref_id in TRACK_M_R_V6_HARDENED_IDS
        else "RECOVERED_MECHANISM_EXAMPLE"
        if ref_id in TRACK_M_R_RECOVERED_EXAMPLE_IDS
        else "BOUNDED_EQ3_TRANSLATION"
    )
    for ref_id in TRACK_M_R_IDS
}

# Static selector policy is governance metadata for the accepted project scope.
# M10 does not mutate M0 or claim that request modifiers activate selector branches.
TRACK_M_R_SELECTOR_POLICY_BY_ID: Mapping[str, str] = {
    "MR-001": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-002": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-003": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-004": "TRUE_MECHANICAL_INLAY_ONLY__UNKNOWN_TECHNIQUE_NO_REFERENCE_SPECIFIC_BRANCH",
    "MR-005": "MASI_KESA_STENCIL__MASK_ABOVE_SHEET__UNKNOWN_SUBTYPE_NO_REFERENCE_SPECIFIC_BRANCH",
    "MR-006": "SIAPO_TASINA_ELEI_RUBBING__RELIEF_BELOW_SHEET__UNKNOWN_SCOPE_NO_REFERENCE_SPECIFIC_BRANCH",
    "MR-007": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-008": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-009": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-010": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-011": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-012": "SHARED_NARROW_STRIP_ASSEMBLY_ONLY__BRANCH_SPECIFIC_CLAIMS_REQUIRE_EVIDENCE",
    "MR-013": "SCOPED_RESIST_DYE_CONTRACT__EXACT_VARIANT_NOT_INFERRED",
    "MR-014": "FIXED_MULTI_PANEL_STITCHED_APPLIQUE_WRAPPER__NO_CROSS_VARIANT_SYNTHESIS",
    "MR-015": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-016": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-017": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-018": "OBJECT_TECHNICAL_SELECTOR_REQUIRED__SUBGROUP_OR_GUL_DOES_NOT_FIX_KNOT_TYPE",
    "MR-019": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-020": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-021": "FIXED_STRUCTURAL_WOODWORK_CONSERVATION_OPERATION__NO_UNIVERSAL_JAPANESE_JOINT",
    "MR-022": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-023": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-024": "STATIC_ACCEPTED_EQ3_CONTRACT",
    "MR-025": "STATIC_ACCEPTED_EQ3_CONTRACT",
}

TRACK_M_R_CONSTRUCTION_BY_ID: Mapping[str, str] = {
    "MR-001": "project-bounded-fine-plant-fibre-strands-form-a-woven-open-or-fine-sheet-through-interlacement-not-a-formed-paper-sheet-and-not-a-raster-texture",
    "MR-002": "wax-resist-is-applied-before-dye-uptake-and-resist-removal-or-repeat-cycles-create-process-bounded-field-differences-without-copying-specific-batik-motifs",
    "MR-003": "cut-cloth-elements-are-hand-joined-or-appliqued-onto-a-backing-so-layer-edge-and-seam-relations-remain-construction-not-printed-ornament",
    "MR-004": "harder-metal-host-receives-a-prepared-recess-or-zone-then-softer-contrasting-metal-is-mechanically-seated-or-hammered-and-finished-flush-or-burnished-painted-or-surface-overlay-lines-do-not-qualify",
    "MR-005": "accepted-masi-kesa-scope-uses-a-mask-or-stencil-above-the-prepared-fibre-sheet-and-transfers-color-through-openings-underlying-relief-rubbing-does-not-qualify",
    "MR-006": "accepted-siapo-tasina-elei-collision-scope-places-a-relief-source-below-the-sheet-and-uses-pressure-or-rubbing-transfer-mask-above-stencil-causality-does-not-qualify",
    "MR-007": "prepared-inner-bark-or-fibre-sheet-is-progressively-beaten-expanded-joined-or-extended-as-a-broad-field-so-sheet-formation-and-join-topology-remain-primary-over-surface-motif",
    "MR-008": "rigid-lattice-or-frame-members-and-bounded-thread-or-lashing-occupancy-create-an-open-structural-grid-with-junctions-that-remain-distinct-from-flat-pattern-wallpaper",
    "MR-009": "fine-ground-weave-remains-continuous-while-discontinuous-supplementary-weft-is-introduced-locally-so-ground-and-inserted-weft-relations-remain-legible-without-copying-motifs",
    "MR-010": "felted-fields-are-cut-joined-or-appliqued-so-seams-overlaps-and-layer-boundaries-carry-the-reference-instead-of-photographic-felt-texture-or-specific-ornament",
    "MR-011": "discrete-cut-glazed-ceramic-units-assemble-into-a-tessellated-field-with-visible-joint-topology-and-bounded-module-edges-rather-than-one-printed-mosaic-image",
    "MR-012": "safe-shared-kente-invariant-is-narrow-woven-strips-assembled-by-sewing-into-a-larger-macro-cloth-branch-specific-heddle-supplementary-weft-count-width-or-motif-claims-are-not-inferred",
    "MR-013": "a-resist-stage-precedes-dye-uptake-and-controls-where-dye-reaches-the-cloth-while-the-exact-adire-variant-is-not-inferred-from-color-or-motif-alone",
    "MR-014": "fixed-project-scope-selects-the-evidence-supported-multi-panel-stitched-or-appliqued-wrapper-branch-and-forbids-importing-single-panel-cut-pile-or-embroidery-branch-behavior-into-that-selected-construction",
    "MR-015": "project-bounded-cloth-treatment-uses-process-derived-application-and-reaction-or-removal-stages-as-causal-field-formation-not-a-generic-earth-tone-or-mud-texture-wallpaper",
    "MR-016": "layered-cloth-construction-uses-superposed-fields-selective-cuts-or-reveals-and-stitch-boundaries-so-depth-and-edge-causality-survive-without-copying-specific-mola-designs",
    "MR-017": "ordered-warp-setup-loom-weaving-and-design-forming-weft-or-warp-operations-create-the-structural-field-without-treating-yakan-motif-semantics-as-construction-evidence",
    "MR-018": "pile-and-foundation-construction-must-be-tied-to-object-level-technical-evidence-and-neither-turkmen-subgroup-nor-gul-or-motif-identity-may-be-used-to-infer-symmetric-or-asymmetric-knot-type",
    "MR-019": "mutuba-inner-bark-is-progressively-beaten-stretched-and-expanded-into-a-sheet-so-process-expansion-and-sheet-continuity-remain-primary-over-generic-bark-patterning",
    "MR-020": "prepared-bast-fibres-are-dispersed-and-formed-into-a-bonded-paper-sheet-so-fibre-cloud-sheet-formation-is-distinct-from-woven-thread-interlacement",
    "MR-021": "fixed-project-scope-selects-the-supported-structural-woodwork-conservation-operation-and-preserves-substrate-tool-operation-and-sequence-without-synthesizing-building-repair-roofing-thatching-plastering-lacquer-painting-tatami-or-other-inventory-skills-into-a-universal-japanese-joint",
    "MR-022": "stone-units-are-selected-fitted-and-stacked-through-contact-bearing-interlock-and-gravity-without-mortar-so-load-path-and-joint-topology-not-stone-photography-carry-the-reference",
    "MR-023": "successive-urushi-lacquer-layers-are-applied-cured-and-finished-or-polished-as-a-layered-process-and-reflective-treatment-must-demote-before-glare-or-text-legibility-failure",
    "MR-024": "formed-ceramic-body-and-bounded-raku-firing-cooling-handling-sequence-drive-surface-discontinuity-while-random-crackle-or-dark-palette-alone-never-establishes-raku-identity",
    "MR-025": "clear-glass-rods-with-lattimo-or-colored-centers-are-fused-into-composite-canes-or-rod-bundles-and-then-formed-or-blown-thin-so-internal-linear-composition-survives-without-generic-transparency-effects",
}

TRACK_M_R_ASSET_ON_APPLICABLE = frozenset(TRACK_M_R_IDS)
TRACK_M_R_ASSET_ON_NOT_APPLICABLE = frozenset()

TRACK_M_R_ROUTED_NON_MEMBERS: Mapping[str, str] = {
    "Kanga": "ROUTE_CULTURAL",
    "Māori Wharenui": "ROUTE_CULTURAL_ARCHITECTURE",
    "Dumbara": "HISTORICAL_ROUTE_NOT_TRACK_M_R_MEMBER",
    "Liyelaa": "HISTORICAL_ROUTE_NOT_TRACK_M_R_MEMBER",
    "generic Barkcloth": "ROUTE_M9_ENGINE_PROCESS",
    "Bidri ware": "COMPARATOR_MERGE_ROUTE_NOT_TRACK_M_R_MEMBER",
}

_PROVENANCE = (
    "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_TRACK_M_R_EQ3_FULL_PASS_LOCK_CHECKPOINT_v1.md;"
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_TRACK_M_R_FULL_CORPUS_EQ2_EQUALIZATION_v4__MEMORY_RECONSTRUCTION.md;"
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_TRACK_M_R_EQ3_IMPLEMENTER_INDEPENDENCE_TORTURE_v5__MEMORY_RECONSTRUCTION.md;"
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_TRACK_M_R_FINAL_SEVEN_EQ3_DEEP_CLOSURE_v6__MEMORY_RECONSTRUCTION.md"
)

_LAYOUT = (SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)
_WORK = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8)
_READ = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U7, SemanticZone.U8)


def _identity(ref_id: str):
    return mechanism(
        ref_id,
        "identity",
        Axis.MATERIAL_CONSTRUCTION,
        (
            f"track-m-r-reconstructed-named-material-reference evidence={TRACK_M_R_EVIDENCE_MODE_BY_ID[ref_id]}; "
            f"selector_policy={TRACK_M_R_SELECTOR_POLICY_BY_ID[ref_id]}; "
            f"{TRACK_M_R_CONSTRUCTION_BY_ID[ref_id]}; "
            "named-reference-identity-is-not-engine-family; reconstructed-track-m-r-is-not-lost-historical-track-m; "
            "reference-projection-consumes-existing-semantic-state-only"
        ),
        zones=_WORK,
        rank=96,
    )


def _optical_guard(ref_id: str):
    if ref_id == "MR-023":
        directive = (
            "urushi-reflectivity-is-presentation-only-and-must-demote-to-low-glare-structural-layer-cues-before-"
            "contrast-focus-text-legibility-or-reading-sanctuary-is-compromised"
        )
    elif ref_id == "MR-025":
        directive = (
            "mezza-filigrana-translucency-refraction-and-highlight-effects-are-optional-presentation-cues-and-"
            "must-demote-to-high-contrast-internal-line-structure-before-glare-or-legibility-failure"
        )
    else:
        return ()
    return (
        mechanism(ref_id, "optical-accessibility", Axis.LIGHT, directive, zones=_WORK, rank=95),
    )


def _build(ref_id: str) -> DNAUnit:
    name = TRACK_M_R_NAME_BY_ID[ref_id]
    slug = (
        name.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace("ò", "o")
        .replace("ñ", "n")
        .replace("ā", "a")
        .replace("’", "")
        .replace("'", "")
    )
    mechanisms = (
        _identity(ref_id),
        mechanism(
            ref_id,
            "ontology-firewall",
            Axis.INFORMATION,
            "track-m-r-reference-may-map-to-normalized-material-engines-but-mapping-never-replaces-named-reference-identity-and-no-contract-may-claim-recovery-of-the-lost-historical-track-m-corpus",
            zones=_WORK,
            rank=100,
        ),
        mechanism(
            ref_id,
            "reading-sanctuary",
            Axis.INFORMATION,
            "reading-code-log-research-and-dense-data-surfaces-demote-material-theatricality-before-legibility-semantic-order-focus-or-density-is-compromised",
            zones=_READ,
            rank=98,
        ),
        mechanism(
            ref_id,
            "wide-adaptation",
            Axis.ADAPTATION,
            "wide-view-may-expose-more-construction-topology-around-existing-content-without-changing-domain-state-cultural-claims-or-semantic-order",
            zones=_LAYOUT,
            viewports=WIDE_VIEWPORTS,
            rank=78,
        ),
        mechanism(
            ref_id,
            "mobile-adaptation",
            Axis.ADAPTATION,
            "mobile-serializes-the-construction-cue-into-bounded-joints-layers-fields-or-process-order-without-texture-miniaturization-hidden-critical-state-or-false-hierarchy",
            zones=_LAYOUT,
            viewports=MOBILE_VIEWPORT,
            rank=90,
        ),
        *_optical_guard(ref_id),
    )
    return unit(
        ref_id,
        kind=UnitKind.REFERENCE,
        family="Track M_R reconstructed named material",
        lineage=f"track-m-r-{slug}",
        mechanisms=mechanisms,
        provenance=_PROVENANCE,
        identity_survival="asset-off-construction-causality-with-track-m-r-historical-firewall",
    )


TRACK_M_R_REFERENCES: Tuple[DNAUnit, ...] = tuple(_build(ref_id) for ref_id in TRACK_M_R_IDS)
TRACK_M_R_BY_ID: Dict[str, DNAUnit] = {item.id: item for item in TRACK_M_R_REFERENCES}


def track_m_r_asset_on_applicable(reference_id: str) -> bool:
    if reference_id not in TRACK_M_R_BY_ID:
        raise KeyError(reference_id)
    return reference_id in TRACK_M_R_ASSET_ON_APPLICABLE


def register_track_m_r(registry) -> None:
    for reference in TRACK_M_R_REFERENCES:
        registry.register(reference)
