"""Deterministic Design-DNA registry and type firewall."""
from __future__ import annotations

from typing import Dict, Iterable, Tuple

from design_dna.models import CompositionRequest, DNAUnit, UnitKind


class RegistryError(ValueError):
    """Base class for explicit registry/composition failures."""


class UnknownUnitError(RegistryError):
    pass


class UnitKindMismatchError(RegistryError):
    pass


class DuplicateUnitError(RegistryError):
    pass


class DNARegistry:
    """Small host-neutral registry with deterministic iteration order."""

    def __init__(self, units: Iterable[DNAUnit] = ()) -> None:
        self._units: Dict[str, DNAUnit] = {}
        for unit in units:
            self.register(unit)

    def register(self, unit: DNAUnit) -> None:
        if not isinstance(unit, DNAUnit):
            raise TypeError("registry accepts DNAUnit instances only")
        unit.validate()
        if unit.id in self._units:
            raise DuplicateUnitError(f"DNA unit '{unit.id}' is already registered")
        self._units[unit.id] = unit

    def get(self, unit_id: str) -> DNAUnit | None:
        if not isinstance(unit_id, str) or not unit_id.strip():
            return None
        return self._units.get(unit_id.strip())

    def require(self, unit_id: str, expected_kind: UnitKind | None = None) -> DNAUnit:
        unit = self.get(unit_id)
        if unit is None:
            raise UnknownUnitError(f"Unknown DNA unit '{unit_id}'")
        if expected_kind is not None and unit.kind is not expected_kind:
            raise UnitKindMismatchError(
                f"DNA unit '{unit_id}' is {unit.kind.value}; expected {expected_kind.value}"
            )
        return unit

    def list_units(self, kind: UnitKind | None = None) -> Tuple[DNAUnit, ...]:
        units = self._units.values()
        if kind is not None:
            units = (unit for unit in units if unit.kind is kind)
        return tuple(sorted(units, key=lambda unit: unit.id))

    def select(self, request: CompositionRequest) -> Tuple[DNAUnit, ...]:
        """Resolve a composition request without allowing kind substitution.

        Fixtures are deliberately not selectable runtime composition inputs.
        Request ordering does not affect selection ordering or downstream output.
        """
        request.validate()
        selected = [self.require(request.selected_reference_id, UnitKind.REFERENCE)]
        selected.extend(self.require(unit_id, UnitKind.ENGINE) for unit_id in sorted(request.engine_ids))
        selected.extend(self.require(unit_id, UnitKind.PRIMITIVE) for unit_id in sorted(request.primitive_ids))
        return tuple(selected)
