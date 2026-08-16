"""
MultiMind AI - Design DNA Registry
Central registry for Design DNA registration, material ownership enforcement, and lookup.
"""
import logging
from typing import Dict, List, Optional
from ui.dna.models import DesignDNA, MaterialReference

logger = logging.getLogger(__name__)


class DNARegistry:
    """Central registry managing Design DNA objects and material ownership policies."""

    def __init__(self):
        self._dna_map: Dict[str, DesignDNA] = {}
        # Tracks material_id -> dna_id for registered material references
        self._material_ownership: Dict[str, str] = {}

    def register_dna(self, dna: DesignDNA) -> None:
        """Registers a new DesignDNA object after validating contract and material ownership rules.

        Raises:
            TypeError: If dna is not a DesignDNA instance.
            ValueError: If dna ID is duplicate or material scope ownership rule is violated.
        """
        if not isinstance(dna, DesignDNA):
            raise TypeError("dna must be an instance of DesignDNA dataclass.")

        dna.validate()

        if dna.id in self._dna_map:
            raise ValueError(f"DesignDNA with ID '{dna.id}' is already registered.")

        # Check material ownership rules across registered materials
        for mat in dna.materials:
            if mat.id in self._material_ownership:
                owner_dna_id = self._material_ownership[mat.id]
                if owner_dna_id != dna.id:
                    # Non-shared material reuse is disallowed
                    if mat.scope_lock or mat.shared_resource_policy == "disallowed":
                        raise ValueError(
                            f"MaterialReference '{mat.id}' in DesignDNA '{dna.id}' is scope-locked/non-shared "
                            f"and is already owned by DesignDNA '{owner_dna_id}'."
                        )

        # Store DNA and record material ownership
        self._dna_map[dna.id] = dna
        for mat in dna.materials:
            # Record ownership for non-shared materials or first registration
            if mat.id not in self._material_ownership:
                self._material_ownership[mat.id] = dna.id

    def list_dna(self) -> List[DesignDNA]:
        """Returns a list of all registered DesignDNA objects."""
        return list(self._dna_map.values())

    def get_dna(self, dna_id: Optional[str]) -> Optional[DesignDNA]:
        """Retrieves a DesignDNA object by ID.

        Returns None if dna_id is unknown, empty, or None (no fallback DNA behavior).
        """
        if not dna_id or not isinstance(dna_id, str):
            return None
        return self._dna_map.get(dna_id.strip())


# Global singleton instance
_global_dna_registry = DNARegistry()


def get_registry() -> DNARegistry:
    """Returns the global DNARegistry singleton."""
    return _global_dna_registry


def register_dna(dna: DesignDNA) -> None:
    """Helper function to register DNA in the global registry."""
    _global_dna_registry.register_dna(dna)


def list_dna() -> List[DesignDNA]:
    """Helper function to list all DNA in the global registry."""
    return _global_dna_registry.list_dna()


def get_dna(dna_id: Optional[str]) -> Optional[DesignDNA]:
    """Helper function to retrieve DNA from the global registry."""
    return _global_dna_registry.get_dna(dna_id)
