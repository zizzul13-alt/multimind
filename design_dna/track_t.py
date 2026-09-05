"""Design-DNA M7: Track T-I temporal/music reference corpus.

Implements the locked 16-member Izzul T-I lane as host-neutral references over
the already-additive TP01-TP18 primitive ontology. Identity is structural:
audio, lyrics, cover art, artist imagery, waveforms and video are never required.

The surviving v3 research hardening provides the 16-way topology discriminator,
nearest-negative map, fail-closed tie law, temporal safety laws and operational
primitive boundary. This module records those contracts declaratively and does
not add source-specific branches to the resolver.
"""
from __future__ import annotations

from typing import Dict, Mapping, Tuple

from design_dna.catalog import MOBILE_VIEWPORT, WIDE_VIEWPORTS, mechanism, unit
from design_dna.models import Axis, DNAUnit, SemanticZone, UnitKind

TRACK_T_I_REFERENCE_IDS: Tuple[str, ...] = tuple(f"TI{i:02d}" for i in range(1, 17))
TRACK_T_I_TITLE_BY_ID: Mapping[str, str] = {
    "TI01": 'Night Train — Awesome City Club',
    "TI02": 'Kono Sekai de Mitsuketa Mono — EGOIST',
    "TI03": 'Kohakuiro no Machi, Shanghai Gani no Asa — Quruli',
    "TI04": 'Sweet Soul — KIRINJI',
    "TI05": 'Utsukushiku Moeru Mori / Forest Burning Beautifully — Tokyo Ska Paradise Orchestra feat. Tamio Okuda',
    "TI06": 'Koromogae — governed tofubeats-vocal presentation',
    "TI07": "Orange — Lil'B",
    "TI08": 'JANE DOE — Kenshi Yonezu & Hikaru Utada',
    "TI09": 'Departures ~Anata ni Okuru Ai no Uta~ — EGOIST',
    "TI10": 'Re:Juliet — BASI & THE BASIC BAND',
    "TI11": "Who's Theme — MINMI",
    "TI12": 'Fukashigi no Carte — governed multi-version/six-character recording family',
    "TI13": 'Suisei — Lovely Summer Chan',
    "TI14": 'Hana — Fujii Kaze',
    "TI15": 'Himitsu — Maica_n',
    "TI16": 'Asayake to Nettaigyo — Boku no Lyric no Bouyomi'
}
TRACK_T_I_TOPOLOGY_BY_ID: Mapping[str, str] = {
    "TI01": "forward-inevitability",
    "TI02": "earned-escalation-descent",
    "TI03": "chapter-transformation-active-outro",
    "TI04": "cyclic-rise-nonzero-reset",
    "TI05": "distributed-call-response-density",
    "TI06": "integrated-handoff-contextual-return",
    "TI07": "mode-switching-narrator-handoff",
    "TI08": "parallel-opposed-voices-divergence",
    "TI09": "progressive-escalation-controlled-descent",
    "TI10": "story-world-switch-all-in-outro",
    "TI11": "continuous-field-low-transform-evolution",
    "TI12": "recurring-field-vocal-recolouring",
    "TI13": "small-topology-raw-continuous-flow",
    "TI14": "intro-economy-bridge-lift-efficient-resolution",
    "TI15": "intimate-bounded-restrained-closure",
    "TI16": "atmosphere-continuity-low-friction-progression"
}
TRACK_T_I_NEAREST_NEGATIVE_BY_ID: Mapping[str, str] = {
    "TI01": "TI04",
    "TI02": "TI09",
    "TI03": "TI10",
    "TI04": "TI01",
    "TI05": "TI03",
    "TI06": "TI04",
    "TI07": "TI08",
    "TI08": "TI07",
    "TI09": "TI02",
    "TI10": "TI03",
    "TI11": "TI13",
    "TI12": "TI11",
    "TI13": "TI11",
    "TI14": "TI09",
    "TI15": "TI13",
    "TI16": "TI13"
}
TRACK_T_I_PRIMITIVE_FINGERPRINT_BY_ID: Mapping[str, Tuple[str, ...]] = {
    "TI01": ('TP15', 'TP16', 'TP17'),
    "TI02": ('TP03', 'TP12', 'TP13', 'TP17'),
    "TI03": ('TP02', 'TP13', 'TP17', 'TP18'),
    "TI04": ('TP01', 'TP05', 'TP06', 'TP17'),
    "TI05": ('TP07', 'TP12', 'TP14'),
    "TI06": ('TP07', 'TP06', 'TP13'),
    "TI07": ('TP07', 'TP09', 'TP13'),
    "TI08": ('TP14', 'TP07', 'TP08'),
    "TI09": ('TP03', 'TP12', 'TP17'),
    "TI10": ('TP02', 'TP13', 'TP17'),
    "TI11": ('TP01', 'TP05', 'TP12'),
    "TI12": ('TP01', 'TP05', 'TP07'),
    "TI13": ('TP10', 'TP12', 'TP17'),
    "TI14": ('TP02', 'TP03', 'TP17', 'TP18'),
    "TI15": ('TP10', 'TP17', 'TP18'),
    "TI16": ('TP05', 'TP10', 'TP17')
}
TRACK_T_I_HISTORICAL_NON_ADDITIVE_PRIMITIVES = ("TP19", "TP20")
TRACK_T_I_ASSET_ON_APPLICABLE = frozenset(TRACK_T_I_REFERENCE_IDS)
TRACK_T_I_ASSET_ON_NOT_APPLICABLE = frozenset()

_PROV_CENSUS = (
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_TRACK_T_DUAL_LANE_CORPUS_ONTOLOGY_CENSUS_v1__MEMORY_RECONSTRUCTION.md"
)
_PROV_V3 = (
    "docs/design-dna/archive/reconstructed-memory/"
    "MULTIMIND_DESIGN_DNA_TRACK_T_I_EQ3_PROJECTION_CONTRACT_HARDENING_v3__MEMORY_RECONSTRUCTION.md"
)
_PROVENANCE = f"{_PROV_CENSUS};{_PROV_V3}"

_LAYOUT = (SemanticZone.U1, SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U8)
_WORK = (SemanticZone.U2, SemanticZone.U3, SemanticZone.U4, SemanticZone.U5, SemanticZone.U6, SemanticZone.U8)

def _identity(reference_id: str):
    topology = TRACK_T_I_TOPOLOGY_BY_ID[reference_id]
    nearest = TRACK_T_I_NEAREST_NEGATIVE_BY_ID[reference_id]
    fingerprint = ",".join(TRACK_T_I_PRIMITIVE_FINGERPRINT_BY_ID[reference_id])
    return mechanism(
        reference_id,
        "identity",
        Axis.NARRATIVE_SEQUENCING,
        (
            f"izzul-track-t-i-owner-scoped-reference topology={topology}; "
            f"required-temporal-fingerprint={fingerprint}; nearest-negative={nearest}; "
            "reference-specific-projection-requires-existing-semantic-state; "
            "unknown-or-exact-unresolved-tie-demotes-to-no-reference-specific-projection; "
            "designed-pacing-never-adds-wait-time-or-withholds-available-state"
        ),
        zones=_WORK,
        rank=98,
    )

def _build(reference_id: str) -> DNAUnit:
    topology = TRACK_T_I_TOPOLOGY_BY_ID[reference_id]
    mechanisms = (
        _identity(reference_id),
        mechanism(
            reference_id, "structure", Axis.INFORMATION,
            f"semantic-sections-express-{topology}-only-through-existing-state-zone-topology-relations-without-inventing-domain-events",
            zones=_WORK, rank=88,
        ),
        mechanism(
            reference_id, "temporal-feedback", Axis.MOTION_TEMPORAL,
            "optional-presentation-temporal-feedback-may-reinforce-existing-state-transitions-but-never-delays-provider-network-or-user-visible-ready-state",
            zones=_LAYOUT, fallback="static-structural-temporal-cues", rank=72,
            accessibility_safe=False, reading_safe=False,
        ),
        mechanism(
            reference_id, "wide-adaptation", Axis.ADAPTATION,
            f"wide-layout-may-show-concurrent-context-for-{topology}-while-preserving-semantic-order-and-immediate-availability",
            zones=_LAYOUT, viewports=WIDE_VIEWPORTS, rank=80,
        ),
        mechanism(
            reference_id, "mobile-adaptation", Axis.ADAPTATION,
            f"mobile-linearizes-{topology}-into-explicit-ordered-structural-cues-without-artificial-latency-hidden-state-or-audio-dependency",
            zones=_LAYOUT, viewports=MOBILE_VIEWPORT, rank=90,
        ),
    )
    return unit(
        reference_id,
        kind=UnitKind.REFERENCE,
        family="Track T-I Temporal Reference",
        lineage=f"track-t-i-{topology}",
        mechanisms=mechanisms,
        provenance=_PROVENANCE,
        identity_survival="asset-off-audio-off-static-structural-temporal-identity",
    )

TRACK_T_I_REFERENCES: Tuple[DNAUnit, ...] = tuple(_build(item) for item in TRACK_T_I_REFERENCE_IDS)
TRACK_T_I_REFERENCE_BY_ID: Dict[str, DNAUnit] = {item.id: item for item in TRACK_T_I_REFERENCES}

def track_t_i_reference_asset_on_applicable(reference_id: str) -> bool:
    if reference_id not in TRACK_T_I_REFERENCE_BY_ID:
        raise KeyError(reference_id)
    return reference_id in TRACK_T_I_ASSET_ON_APPLICABLE

def register_m7_track_t_i_references(registry) -> None:
    for reference in TRACK_T_I_REFERENCES:
        registry.register(reference)
