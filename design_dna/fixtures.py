"""Design-DNA M11: governed benchmark / marriage fixtures.

Fixtures are executable benchmark contracts, not selectable DNA references.
The historical corpus contained F01-F15; F11 remains historical/non-additive.
Where the original marriage cannot be recovered from surviving repository
material, M11 records an explicit evidence gap instead of fabricating truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

from design_dna.catalog import MOBILE_VIEWPORT, WIDE_VIEWPORTS, mechanism, unit
from design_dna.models import AssetState, Axis, DNAUnit, SemanticZone, UnitKind, Viewport
from design_dna.registry import DNARegistry

M11_FIXTURE_IDS: Tuple[str, ...] = (
    "F01", "F02", "F03", "F04", "F05", "F06", "F07",
    "F08", "F09", "F10", "F12", "F13", "F14", "F15",
)
M11_HISTORICAL_NON_ADDITIVE: Mapping[str, str] = {
    "F11": "Argentina Concrete Open Frame × Poland Expressive Typography × Terminal; historical refusal because Concrete Open Frame identity/mechanism remains unrecovered",
}

FIXTURE_ASSET_ON_APPLICABLE = frozenset({
    "F01", "F02", "F04", "F07", "F08", "F09", "F12", "F13", "F15",
})
FIXTURE_ASSET_ON_NOT_APPLICABLE = frozenset({"F03", "F05", "F06", "F10", "F14"})

FIXTURE_COMPOSITION_BY_ID: Mapping[str, str] = {
    "F01": "UNKNOWN_ORIGINAL_COMPOSITION",
    "F02": "Rinpa × Japan High-Density Information × Chat-first",
    "F03": "Czech Cubism × Netherlands Concept-First Web × Agent Canvas",
    "F04": "UNKNOWN_ORIGINAL_COMPOSITION__CKT_BLOCKER_CLOSED_BY_ACCEPTED_WAVE_H",
    "F05": "Quipu × China Service Convergence × Command Center",
    "F06": "Neo-Concrete × Silicon Valley Product Web × Workspace",
    "F07": "UNKNOWN_ORIGINAL_COMPOSITION",
    "F08": "UNKNOWN_ORIGINAL_COMPOSITION",
    "F09": "UNKNOWN_ORIGINAL_COMPOSITION",
    "F10": "UNKNOWN_ORIGINAL_COMPOSITION",
    "F12": "Māori Wharenui Relational × Aotearoa Bicultural Web × Research Lab",
    "F13": "Art Deco × Italy Editorial lens × Minimal SaaS",
    "F14": "Marshallese Navigation × Germany Rational lens × Agent Canvas",
    "F15": "Japan Print/Ink × U.S./Silicon Valley Product Web × Chat-first",
}

FIXTURE_EVIDENCE_STATE_BY_ID: Mapping[str, str] = {
    fixture_id: (
        "RECOVERED_COMPOSITION"
        if not composition.startswith("UNKNOWN_ORIGINAL_COMPOSITION")
        else "BOUNDED_EVIDENCE_GAP"
    )
    for fixture_id, composition in FIXTURE_COMPOSITION_BY_ID.items()
}

_PROVENANCE = (
    "docs/design-dna/archive/raw/MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_8_LOCK_CHECKPOINT_v1.md;"
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_8_FIXTURES_v1__MEMORY_RECONSTRUCTION.md;"
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_B6_BENCHMARK_MARRIAGES_v1__MEMORY_RECONSTRUCTION.md"
)

_LAYOUT = (SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)
_WORK = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8)
_READ = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U7, SemanticZone.U8)


@dataclass(frozen=True)
class FixtureProjectionContract:
    fixture_id: str
    composition: str
    evidence_state: str
    viewport: Viewport
    asset_state: AssetState
    reading_sanctuary: bool
    reduced_motion: bool
    structural_directives: Tuple[str, ...]
    asset_enrichment_allowed: bool
    fixture_owned_asset: bool = False


def fixture_asset_on_applicable(fixture_id: str) -> bool:
    if fixture_id not in M11_FIXTURE_IDS:
        raise KeyError(f"unknown additive fixture: {fixture_id}")
    return fixture_id in FIXTURE_ASSET_ON_APPLICABLE


def fixture_projection_contract(
    fixture_id: str,
    *,
    viewport: Viewport = Viewport.DESKTOP,
    asset_state: AssetState = AssetState.OFF,
    reading_sanctuary: bool = True,
    reduced_motion: bool = False,
) -> FixtureProjectionContract:
    """Return deterministic benchmark projection law without mutating domain truth."""
    if fixture_id not in M11_FIXTURE_IDS:
        raise KeyError(f"unknown additive fixture: {fixture_id}")
    if not isinstance(viewport, Viewport):
        raise TypeError("viewport must be Viewport")
    if not isinstance(asset_state, AssetState):
        raise TypeError("asset_state must be AssetState")

    composition = FIXTURE_COMPOSITION_BY_ID[fixture_id]
    evidence_state = FIXTURE_EVIDENCE_STATE_BY_ID[fixture_id]
    directives = [
        "semantic-state-precedes-presentation",
        "single-primary-owner-per-axis-zone-with-bounded-secondary-contributions",
        "hard-accessibility-veto-is-never-averaged-into-contradiction-budget",
        "fixture-selection-never-promotes-or-mutates-underlying-reference-truth",
    ]
    if evidence_state == "BOUNDED_EVIDENCE_GAP":
        directives.append("unknown-original-marriage-remains-explicit-and-must-not-be-invented")
    if reading_sanctuary:
        directives.append("reading-sanctuary-demotes-aesthetic-theatricality-before-content-order-or-legibility")
    if reduced_motion:
        directives.append("reduced-motion-removes-nonessential-transition-theatricality-without-changing-fixture-identity")
    if viewport is Viewport.MOBILE:
        directives.append("mobile-serializes-owned-zones-without-generic-style-stacking-or-hidden-critical-state")
    elif viewport is Viewport.TABLET:
        directives.append("tablet-compresses-secondary-contributions-while-preserving-primary-axis-zone-ownership")
    else:
        directives.append("desktop-may-expose-secondary-structure-within-dominance-caps")

    asset_allowed = fixture_id in FIXTURE_ASSET_ON_APPLICABLE and asset_state is not AssetState.OFF
    if asset_allowed:
        directives.append("asset-enrichment-is-component-owned-and-may-never-be-required-for-structural-fixture-survival")
    else:
        directives.append("structural-fixture-contract-remains-usable-without-assets")

    return FixtureProjectionContract(
        fixture_id=fixture_id,
        composition=composition,
        evidence_state=evidence_state,
        viewport=viewport,
        asset_state=asset_state,
        reading_sanctuary=reading_sanctuary,
        reduced_motion=reduced_motion,
        structural_directives=tuple(directives),
        asset_enrichment_allowed=asset_allowed,
    )


def _build_fixture(fixture_id: str) -> DNAUnit:
    evidence = FIXTURE_EVIDENCE_STATE_BY_ID[fixture_id]
    composition = FIXTURE_COMPOSITION_BY_ID[fixture_id]
    mechanisms = (
        mechanism(
            fixture_id,
            "benchmark-contract",
            Axis.INFORMATION,
            (
                f"fixture-benchmark-contract evidence={evidence}; composition={composition}; "
                "fixture-is-not-dna-and-does-not-promote-reference-engine-or-primitive; "
                "semantic-state-axis-zone-ownership-dominance-conflict-demotion-projection-survival-order"
            ),
            zones=_WORK,
            rank=100,
        ),
        mechanism(
            fixture_id,
            "reading-sanctuary",
            Axis.INTERACTION,
            "reading-code-citation-table-and-log-surfaces-preserve-logical-order-focus-and-usable-density-before-aesthetic-collision-effects",
            zones=_READ,
            rank=100,
        ),
        mechanism(
            fixture_id,
            "wide-adaptation",
            Axis.ADAPTATION,
            "wide-layout-may-show-bounded-secondary-contributions-but-one-primary-owner-per-relevant-axis-zone-remains-authoritative",
            zones=_LAYOUT,
            viewports=WIDE_VIEWPORTS,
            rank=90,
        ),
        mechanism(
            fixture_id,
            "mobile-adaptation",
            Axis.MOTION_TEMPORAL,
            "mobile-and-reduced-motion-transform-the-benchmark-into-deterministic-serialized-structure-without-hiding-critical-state-or-requiring-animation",
            zones=_LAYOUT,
            viewports=MOBILE_VIEWPORT,
            rank=95,
        ),
    )
    return unit(
        fixture_id,
        kind=UnitKind.FIXTURE,
        family="benchmark_marriage_fixture",
        lineage="B6 benchmark marriages → Global Calibration Batch 8 → M11",
        mechanisms=mechanisms,
        provenance=_PROVENANCE,
        identity_survival="benchmark composition law survives asset-off; fixture never becomes runtime reference truth",
    )


M11_FIXTURES: Tuple[DNAUnit, ...] = tuple(_build_fixture(fixture_id) for fixture_id in M11_FIXTURE_IDS)
FIXTURE_BY_ID: Mapping[str, DNAUnit] = {item.id: item for item in M11_FIXTURES}


def register_m11_fixtures(registry: DNARegistry) -> None:
    for fixture in M11_FIXTURES:
        registry.register(fixture)
