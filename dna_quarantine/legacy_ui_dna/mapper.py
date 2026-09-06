"""
MultiMind AI - Design DNA to Theme Adapter Mapper
Pure adapter translating DesignDNA visual intent into S5 Theme contract instances.
"""
import copy
from .models import DesignDNA
from ui.themes.models import Theme, ThemeMetadata


def dna_to_theme(dna: DesignDNA) -> Theme:
    """Translates a DesignDNA instance into a pure Theme contract object.

    Does not mutate the source DesignDNA object or canonical base tokens.
    Does not register the generated Theme with ThemeRegistry automatically.
    """
    if not isinstance(dna, DesignDNA):
        raise TypeError("dna must be an instance of DesignDNA dataclass.")

    dna.validate()

    # Map DNA-level metadata and provenance to ThemeMetadata
    provenance = dna.provenance or {}
    meta = ThemeMetadata(
        description=dna.description or f"Theme generated from Design DNA '{dna.id}'",
        author=str(provenance.get("author", "")),
        license=str(provenance.get("license", "")),
        source=str(provenance.get("source", "")),
        attribution=str(provenance.get("attribution", "")),
        reference=dna.reference_identity,
        asset_scope=dna.category,
    )

    theme = Theme(
        id=dna.id,
        display_name=dna.display_name,
        category=dna.category,
        description=dna.description,
        metadata=meta,
        colors=copy.deepcopy(dna.colors),
        typography=copy.deepcopy(dna.typography),
        spacing=copy.deepcopy(dna.spacing),
        radius=copy.deepcopy(dna.radius),
    )

    theme.validate()
    return theme
