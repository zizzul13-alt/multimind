"""Shared host-neutral builders for declarative Design-DNA catalogs.

This module exists to keep scale-out batches data-oriented. It must remain free of
presentation hosts, application/core semantics, providers, persistence and network IO.
"""
from __future__ import annotations

from typing import Iterable, Tuple

from design_dna.models import (
    AbsenceState,
    Axis,
    AxisAbsence,
    DNAUnit,
    MechanismContract,
    SemanticZone,
    UnitKind,
)

ALL_VIEWPORTS = ("desktop", "tablet", "mobile")
WIDE_VIEWPORTS = ("desktop", "tablet")
MOBILE_VIEWPORT = ("mobile",)


def mechanism(
    unit_id: str,
    suffix: str,
    axis: Axis,
    directive: str,
    *,
    zones: Tuple[SemanticZone, ...],
    fallback: str = "",
    rank: int = 80,
    viewports: Tuple[str, ...] = ALL_VIEWPORTS,
    accessibility_safe: bool = True,
    reading_safe: bool = True,
) -> MechanismContract:
    return MechanismContract(
        id=f"{unit_id.lower()}-{suffix}",
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


def explicit_absences(mechanisms: Iterable[MechanismContract]) -> Tuple[AxisAbsence, ...]:
    covered = {item.axis for item in mechanisms}
    return tuple(
        AxisAbsence(axis=axis, state=AbsenceState.NOT_APPLICABLE)
        for axis in Axis
        if axis not in covered
    )


def unit(
    unit_id: str,
    *,
    kind: UnitKind,
    family: str,
    lineage: str,
    mechanisms: Tuple[MechanismContract, ...],
    provenance: str,
    identity_survival: str,
) -> DNAUnit:
    return DNAUnit(
        id=unit_id,
        kind=kind,
        family=family,
        lineage=lineage,
        provenance_pointer=provenance,
        mechanisms=mechanisms,
        axis_absences=explicit_absences(mechanisms),
        assets=(),
        identity_survival=identity_survival,
    )
