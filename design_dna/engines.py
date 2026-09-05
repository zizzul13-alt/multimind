"""Locked M1 engine catalog: Material M1-M15 + Environment E1-E14.

This module translates the surviving canonical identities and Batch-2 hard laws into
host-neutral runtime contracts. It deliberately does not reconstruct unavailable
historical per-engine prose, create assets, or claim EQ4 host/browser proof.
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

MATERIAL_ENGINE_IDS: Tuple[str, ...] = tuple(f"M{i}" for i in range(1, 16))
ENVIRONMENT_ENGINE_IDS: Tuple[str, ...] = tuple(f"E{i}" for i in range(1, 15))
M1_ENGINE_IDS: Tuple[str, ...] = MATERIAL_ENGINE_IDS + ENVIRONMENT_ENGINE_IDS

# Batch-2 lock: 27 applicable, E1/E5 explicitly not-applicable.
ASSET_ON_NOT_APPLICABLE = frozenset({"E1", "E5"})
ASSET_ON_APPLICABLE = frozenset(M1_ENGINE_IDS) - ASSET_ON_NOT_APPLICABLE

PROVENANCE_MATERIAL = (
    "docs/design-dna/corpora/CORPUS_INDEX.md#material-engines---15-additive;"
    "docs/design-dna/archive/raw/"
    "MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_2_LOCK_CHECKPOINT_v1.md"
)
PROVENANCE_ENVIRONMENT = (
    "docs/design-dna/corpora/CORPUS_INDEX.md#environment-engines---14-additive;"
    "docs/design-dna/archive/raw/"
    "MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_2_LOCK_CHECKPOINT_v1.md"
)

_MATERIAL_ZONES = (
    SemanticZone.U1,
    SemanticZone.U2,
    SemanticZone.U3,
    SemanticZone.U4,
    SemanticZone.U8,
)
_ENVIRONMENT_ZONES = (
    SemanticZone.U1,
    SemanticZone.U2,
    SemanticZone.U3,
    SemanticZone.U4,
    SemanticZone.U6,
    SemanticZone.U8,
)
_ALL_VIEWPORTS = ("desktop", "tablet", "mobile")


def _mechanism(
    engine_id: str,
    suffix: str,
    axis: Axis,
    directive: str,
    *,
    zones: Tuple[SemanticZone, ...],
    fallback: str = "",
    rank: int = 60,
    accessibility_safe: bool = True,
    reading_safe: bool = True,
) -> MechanismContract:
    return MechanismContract(
        id=f"{engine_id.lower()}-{suffix}",
        axis=axis,
        zones=zones,
        directive=directive,
        fallback_directive=fallback,
        ownership_rank=rank,
        viewports=_ALL_VIEWPORTS,
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


def _engine(
    engine_id: str,
    family: str,
    mechanisms: Tuple[MechanismContract, ...],
    *,
    provenance: str,
) -> DNAUnit:
    return DNAUnit(
        id=engine_id,
        kind=UnitKind.ENGINE,
        family=family,
        lineage="normalized-material-environment-wave-c-batch-2",
        provenance_pointer=provenance,
        mechanisms=mechanisms,
        axis_absences=_absences(mechanisms),
        assets=(),
        identity_survival="structural-engine-without-assets",
    )


def _material(engine_id: str, family: str, *mechanisms: MechanismContract) -> DNAUnit:
    return _engine(engine_id, family, tuple(mechanisms), provenance=PROVENANCE_MATERIAL)


def _environment(engine_id: str, family: str, *mechanisms: MechanismContract) -> DNAUnit:
    return _engine(engine_id, family, tuple(mechanisms), provenance=PROVENANCE_ENVIRONMENT)


M1_ENGINES: Tuple[DNAUnit, ...] = (
    _material(
        "M1", "Paper / Fibrous Sheet",
        _mechanism("M1", "layered-sheet", Axis.MATERIAL_CONSTRUCTION, "fibrous-sheet-layering-with-explicit-edges", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M1", "fold-edge", Axis.FORM, "bounded-fold-score-and-sheet-edge-articulation", zones=_MATERIAL_ZONES, rank=56),
    ),
    _material(
        "M2", "Timber / Wood Assembly",
        _mechanism("M2", "joined-members", Axis.MATERIAL_CONSTRUCTION, "joined-linear-members-with-visible-assembly-logic", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M2", "member-direction", Axis.FORM, "directional-member-segmentation-with-bounded-joints", zones=_MATERIAL_ZONES, rank=56),
    ),
    _material(
        "M3", "Stone / Masonry",
        _mechanism("M3", "mass-joints", Axis.MATERIAL_CONSTRUCTION, "massive-unit-assembly-with-explicit-joint-bands", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M3", "thick-boundary", Axis.SPACE, "bounded-thickness-and-recessed-boundary-cues", zones=_MATERIAL_ZONES, rank=56),
    ),
    _material(
        "M4", "Concrete / Cast Monolith",
        _mechanism("M4", "cast-mass", Axis.MATERIAL_CONSTRUCTION, "continuous-cast-mass-with-formwork-seam-logic", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M4", "monolithic-form", Axis.FORM, "continuous-monolithic-form-with-sparse-junctions", zones=_MATERIAL_ZONES, rank=56),
    ),
    _material(
        "M5", "Metal / Fabricated",
        _mechanism("M5", "fabricated-joins", Axis.MATERIAL_CONSTRUCTION, "fabricated-sheet-or-member-assembly-with-explicit-fastening-logic", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M5", "precise-edge", Axis.FORM, "precise-edged-segmented-fabrication", zones=_MATERIAL_ZONES, rank=56),
    ),
    _material(
        "M6", "Glass / Transparent Panel",
        _mechanism("M6", "transparent-panel", Axis.MATERIAL_CONSTRUCTION, "bounded-transparent-panel-with-explicit-frame-or-edge", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M6", "transmission", Axis.LIGHT, "bounded-transmission-refraction-with-content-legibility-preserved", zones=_MATERIAL_ZONES, fallback="reduced-transmission-neutral-panel", rank=54),
    ),
    _material(
        "M7", "Textile / Woven",
        _mechanism("M7", "woven-crossing", Axis.MATERIAL_CONSTRUCTION, "interlaced-woven-crossing-logic-with-bounded-repeat", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M7", "woven-form", Axis.FORM, "soft-grid-deformation-with-structural-weave-rhythm", zones=_MATERIAL_ZONES, rank=55),
    ),
    _material(
        "M8", "Felt / Appliqué / Layered Cloth",
        _mechanism("M8", "layered-cloth", Axis.MATERIAL_CONSTRUCTION, "layered-soft-sheet-overlap-with-explicit-cut-boundaries", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M8", "applique-overlap", Axis.FORM, "bounded-overlap-and-cut-shape-articulation", zones=_MATERIAL_ZONES, rank=55),
    ),
    _material(
        "M9", "Barkcloth / Beaten Fiber Sheet",
        _mechanism("M9", "beaten-fiber", Axis.MATERIAL_CONSTRUCTION, "beaten-fiber-sheet-with-irregular-edge-and-compression-logic", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M9", "fiber-edge", Axis.FORM, "irregular-fibrous-edge-without-cultural-reference-claim", zones=_MATERIAL_ZONES, rank=55),
    ),
    _material(
        "M10", "Mosaic / Tessellated Unit",
        _mechanism("M10", "tessellation", Axis.MATERIAL_CONSTRUCTION, "discrete-tessellated-units-with-explicit-joint-network", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M10", "unit-field", Axis.FORM, "bounded-modular-unit-field-with-nonsemantic-repeat", zones=_MATERIAL_ZONES, rank=55),
    ),
    _material(
        "M11", "Inlay / Host-Insert",
        _mechanism("M11", "host-insert", Axis.MATERIAL_CONSTRUCTION, "host-surface-with-bounded-insert-and-explicit-interface", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M11", "insert-boundary", Axis.FORM, "bounded-inset-shape-distinct-from-host-plane", zones=_MATERIAL_ZONES, rank=55),
    ),
    _material(
        "M12", "Lattice / Open Frame",
        _mechanism("M12", "open-frame", Axis.MATERIAL_CONSTRUCTION, "open-frame-member-network-with-explicit-junctions", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M12", "void-ratio", Axis.SPACE, "bounded-positive-negative-space-lattice-with-content-clearance", zones=_MATERIAL_ZONES, fallback="reduced-open-frame-density", rank=57),
    ),
    _material(
        "M13", "Ceramic / Glazed Unit",
        _mechanism("M13", "glazed-unit", Axis.MATERIAL_CONSTRUCTION, "fired-unit-assembly-with-bounded-glazed-surface", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M13", "glaze-response", Axis.LIGHT, "bounded-specular-glaze-response-without-obscuring-content", zones=_MATERIAL_ZONES, fallback="reduced-glaze-reflectance", rank=54),
    ),
    _material(
        "M14", "Polished / Reflective Surface",
        _mechanism("M14", "polished-surface", Axis.MATERIAL_CONSTRUCTION, "continuous-polished-surface-with-explicit-boundary", zones=_MATERIAL_ZONES, rank=72),
        _mechanism("M14", "reflection", Axis.LIGHT, "bounded-reflective-response-with-controlled-highlight", zones=_MATERIAL_ZONES, fallback="matte-low-glare-response", rank=54, accessibility_safe=False),
    ),
    _material(
        "M15", "Patina / Wear",
        _mechanism("M15", "wear-layer", Axis.MATERIAL_CONSTRUCTION, "nonsemantic-wear-layer-on-explicit-host-surface", zones=_MATERIAL_ZONES, rank=68),
        _mechanism("M15", "bounded-sequencing", Axis.NARRATIVE_SEQUENCING, "bounded-visual-wear-sequencing-never-derived-from-application-age-status-or-health", zones=_MATERIAL_ZONES, fallback="static-neutral-wear-distribution", rank=50),
    ),
    _environment(
        "E1", "Daylight / Diffuse Day",
        _mechanism("E1", "diffuse-day", Axis.LIGHT, "diffuse-day-illumination-with-stable-soft-shadow-envelope", zones=_ENVIRONMENT_ZONES, rank=66),
        _mechanism("E1", "day-ambient", Axis.ATMOSPHERE_ENVIRONMENT, "neutral-day-ambient-without-scenery-or-location-claim", zones=_ENVIRONMENT_ZONES, rank=58),
    ),
    _environment(
        "E2", "Direct Sun / Hard Light",
        _mechanism("E2", "hard-light", Axis.LIGHT, "directional-hard-light-with-bounded-shadow-contrast", zones=_ENVIRONMENT_ZONES, fallback="reduced-directional-contrast", rank=68, accessibility_safe=False),
        _mechanism("E2", "sun-ambient", Axis.ATMOSPHERE_ENVIRONMENT, "high-clarity-direct-sun-ambient-without-location-claim", zones=_ENVIRONMENT_ZONES, rank=58),
    ),
    _environment(
        "E3", "Night / Low Ambient",
        _mechanism("E3", "low-ambient", Axis.LIGHT, "low-ambient-illumination-with-protected-content-contrast", zones=_ENVIRONMENT_ZONES, fallback="raised-low-light-floor", rank=67),
        _mechanism("E3", "night-ambient", Axis.ATMOSPHERE_ENVIRONMENT, "night-low-ambient-condition-without-scenery", zones=_ENVIRONMENT_ZONES, rank=58),
    ),
    _environment(
        "E4", "Dawn / Dusk Transition",
        _mechanism("E4", "transition-light", Axis.LIGHT, "bounded-dawn-dusk-light-transition-envelope", zones=_ENVIRONMENT_ZONES, rank=66),
        _mechanism("E4", "transition-time", Axis.MOTION_TEMPORAL, "presentation-only-dawn-dusk-transition-never-mutating-application-state", zones=_ENVIRONMENT_ZONES, fallback="static-transition-midpoint", rank=55),
    ),
    _environment(
        "E5", "Overcast / Diffuse Low-Contrast",
        _mechanism("E5", "overcast-light", Axis.LIGHT, "diffuse-low-contrast-overcast-illumination-with-content-contrast-floor", zones=_ENVIRONMENT_ZONES, rank=66),
        _mechanism("E5", "overcast-ambient", Axis.ATMOSPHERE_ENVIRONMENT, "overcast-diffuse-ambient-without-weather-feed", zones=_ENVIRONMENT_ZONES, rank=58),
    ),
    _environment(
        "E6", "Rain",
        _mechanism("E6", "rain-visibility", Axis.ATMOSPHERE_ENVIRONMENT, "rain-visibility-attenuation-and-wet-ambient-without-live-weather-dependency", zones=_ENVIRONMENT_ZONES, rank=62),
        _mechanism("E6", "rain-motion", Axis.MOTION_TEMPORAL, "bounded-rainfall-motion-cue", zones=_ENVIRONMENT_ZONES, fallback="static-wetness-and-rain-cue", rank=54, accessibility_safe=False),
    ),
    _environment(
        "E7", "Mist / Fog",
        _mechanism("E7", "visibility-attenuation", Axis.ATMOSPHERE_ENVIRONMENT, "bounded-distance-visibility-attenuation-with-foreground-legibility-floor", zones=_ENVIRONMENT_ZONES, fallback="reduced-atmospheric-attenuation", rank=62),
        _mechanism("E7", "diffuse-fog-light", Axis.LIGHT, "fog-diffused-light-with-reduced-shadow-separation", zones=_ENVIRONMENT_ZONES, rank=58),
    ),
    _environment(
        "E8", "Snow / High-Albedo",
        _mechanism("E8", "high-albedo", Axis.LIGHT, "high-albedo-ambient-with-bounded-glare-and-contrast", zones=_ENVIRONMENT_ZONES, fallback="reduced-albedo-low-glare", rank=68, accessibility_safe=False),
        _mechanism("E8", "snow-ambient", Axis.ATMOSPHERE_ENVIRONMENT, "high-reflectance-cold-ambient-without-scenery", zones=_ENVIRONMENT_ZONES, rank=58),
    ),
    _environment(
        "E9", "Forest / Canopy Filtered Light",
        _mechanism("E9", "canopy-filter", Axis.LIGHT, "filtered-dappled-light-with-bounded-local-contrast", zones=_ENVIRONMENT_ZONES, fallback="diffuse-filtered-light", rank=64),
        _mechanism("E9", "canopy-ambient", Axis.ATMOSPHERE_ENVIRONMENT, "canopy-filtered-ambient-condition-without-forest-wallpaper", zones=_ENVIRONMENT_ZONES, rank=58),
    ),
    _environment(
        "E10", "Water / Caustic-Reflective",
        _mechanism("E10", "caustic-light", Axis.LIGHT, "bounded-caustic-reflective-light-response", zones=_ENVIRONMENT_ZONES, fallback="static-refracted-light-band", rank=65, accessibility_safe=False),
        _mechanism("E10", "caustic-motion", Axis.MOTION_TEMPORAL, "bounded-caustic-motion-cue", zones=_ENVIRONMENT_ZONES, fallback="static-refracted-light-band", rank=53, accessibility_safe=False),
    ),
    _environment(
        "E11", "Urban Night / Multisource Light",
        _mechanism("E11", "multisource-light", Axis.LIGHT, "bounded-multisource-local-light-with-controlled-highlight-collisions", zones=_ENVIRONMENT_ZONES, fallback="reduced-multisource-light", rank=67, accessibility_safe=False),
        _mechanism("E11", "urban-night-ambient", Axis.ATMOSPHERE_ENVIRONMENT, "urban-night-multisource-ambient-without-city-or-country-claim", zones=_ENVIRONMENT_ZONES, rank=58),
    ),
    _environment(
        "E12", "Interior Warm Local Light",
        _mechanism("E12", "warm-local-light", Axis.LIGHT, "warm-local-light-pools-with-readable-neutral-content-floor", zones=_ENVIRONMENT_ZONES, rank=65),
        _mechanism("E12", "interior-ambient", Axis.ATMOSPHERE_ENVIRONMENT, "interior-local-light-ambient-without-room-wallpaper", zones=_ENVIRONMENT_ZONES, rank=58),
    ),
    _environment(
        "E13", "Desert / High-Exposure Dry Light",
        _mechanism("E13", "high-exposure", Axis.LIGHT, "high-exposure-dry-light-with-bounded-glare-and-shadow-contrast", zones=_ENVIRONMENT_ZONES, fallback="reduced-high-exposure-light", rank=68, accessibility_safe=False),
        _mechanism("E13", "dry-ambient", Axis.ATMOSPHERE_ENVIRONMENT, "dry-high-visibility-ambient-without-desert-scenery", zones=_ENVIRONMENT_ZONES, rank=58),
    ),
    _environment(
        "E14", "Seasonal / Ecological Change",
        _mechanism("E14", "seasonal-ambient", Axis.ATMOSPHERE_ENVIRONMENT, "bounded-seasonal-ecological-ambient-state-without-live-location-or-weather-feed", zones=_ENVIRONMENT_ZONES, rank=60),
        _mechanism("E14", "seasonal-transition", Axis.MOTION_TEMPORAL, "presentation-only-seasonal-transition-never-mutating-application-state", zones=_ENVIRONMENT_ZONES, fallback="static-seasonal-state", rank=54),
    ),
)

ENGINE_BY_ID: Dict[str, DNAUnit] = {unit.id: unit for unit in M1_ENGINES}

if tuple(ENGINE_BY_ID) != M1_ENGINE_IDS:
    raise RuntimeError("M1 engine catalog order/membership drift")


def engine_asset_on_applicable(engine_id: str) -> bool:
    """Return locked Batch-2 asset-on applicability for an M1 engine."""
    if engine_id not in ENGINE_BY_ID:
        raise KeyError(engine_id)
    return engine_id in ASSET_ON_APPLICABLE


def register_m1_engines(registry) -> None:
    """Register all 29 engine units into an existing DNARegistry."""
    for unit in M1_ENGINES:
        registry.register(unit)
