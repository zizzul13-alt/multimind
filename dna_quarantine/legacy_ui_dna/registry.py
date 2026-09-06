"""
MultiMind AI - Design DNA Registry
Central registry for Design DNA registration, material ownership enforcement, and lookup.
"""
import copy
import logging
from typing import Dict, List, Optional, Tuple
from .models import DesignDNA, MaterialReference

logger = logging.getLogger(__name__)


class DNARegistry:
    """Central registry managing Design DNA objects and material ownership policies."""

    def __init__(self):
        self._dna_map: Dict[str, DesignDNA] = {}
        # Tracks material_id -> (canonical MaterialReference copy, owner_dna_id)
        self._material_records: Dict[str, Tuple[MaterialReference, str]] = {}

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

        # Validate material ownership policies against canonical registered materials
        new_materials_to_record: Dict[str, Tuple[MaterialReference, str]] = {}

        for mat in dna.materials:
            if mat.id in self._material_records:
                orig_mat, orig_dna_id = self._material_records[mat.id]
                orig_is_shared = (not orig_mat.scope_lock) and (orig_mat.shared_resource_policy == "allowed")
                inc_is_shared = (not mat.scope_lock) and (mat.shared_resource_policy == "allowed")

                if not orig_is_shared:
                    if not inc_is_shared:
                        # Case 1: Original non-shared + incoming non-shared -> reject
                        raise ValueError(
                            f"MaterialReference '{mat.id}' in DesignDNA '{dna.id}' is scope-locked/non-shared "
                            f"and is already owned by DesignDNA '{orig_dna_id}'."
                        )
                    else:
                        # Case 2: Original non-shared + incoming claims shared -> reject
                        raise ValueError(
                            f"MaterialReference '{mat.id}' in DesignDNA '{dna.id}' claims to be shared, "
                            f"but material '{mat.id}' was originally registered as scope-locked/non-shared "
                            f"by DesignDNA '{orig_dna_id}'."
                        )
                else:
                    if inc_is_shared:
                        # Case 3: Original shared + incoming shared -> allow
                        pass
                    else:
                        # Case 4: Original shared + incoming claims non-shared -> reject
                        raise ValueError(
                            f"MaterialReference '{mat.id}' in DesignDNA '{dna.id}' claims to be scope-locked/non-shared, "
                            f"but material '{mat.id}' was originally registered as an explicitly shared resource "
                            f"by DesignDNA '{orig_dna_id}'."
                        )
            else:
                # Deep copy material reference to prevent external mutation from altering canonical policy
                new_materials_to_record[mat.id] = (copy.deepcopy(mat), dna.id)

        # Commit registration
        self._dna_map[dna.id] = dna
        self._material_records.update(new_materials_to_record)

    def combine_materials(self, *dnas: DesignDNA) -> Tuple[MaterialReference, ...]:
        """Validates and combines registered DNA materials using registry ownership rules."""
        combined_registry = DNARegistry()
        for dna in dnas:
            if dna is not None:
                combined_registry.register_dna(dna)
        return tuple(material for dna in dnas if dna is not None for material in dna.materials)

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
