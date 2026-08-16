"""
MultiMind AI - Design DNA Contract & Registry Package
Exposes DesignDNA models, MaterialReference, DNA → Theme mapper, and central DNARegistry.
"""
from ui.dna.models import MaterialReference, DesignDNA
from ui.dna.mapper import dna_to_theme
from ui.dna.registry import (
    DNARegistry,
    get_registry,
    register_dna,
    list_dna,
    get_dna,
)

__all__ = [
    "MaterialReference",
    "DesignDNA",
    "dna_to_theme",
    "DNARegistry",
    "get_registry",
    "register_dna",
    "list_dna",
    "get_dna",
]
