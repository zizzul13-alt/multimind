"""
MultiMind AI - Design DNA Contract Models
Defines dataclasses for Design DNA, Material References, and Provenance Metadata.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Dict, List, Any, Mapping, Optional, Tuple

VALID_SHARED_RESOURCE_POLICIES = {"disallowed", "allowed"}

# Controlled Material Taxonomy: contract-level valid types vs currently renderable types
VALID_MATERIAL_TYPES = {"graphic_mark", "texture", "font", "pattern"}
CURRENT_RENDERABLE_MATERIAL_TYPES = {"graphic_mark"}

# Controlled DNA Roles Taxonomy
VALID_DNA_ROLES = {"identity", "web_information"}
DEFAULT_DNA_ROLE = "identity"

# Bounded Production Semantic Taxonomy (S8.2)
VALID_VISUAL_ENERGY = {"quiet", "restrained", "balanced", "expressive", "aggressive"}
VALID_SPATIAL_DENSITY = {"spacious", "balanced", "compact", "dense"}
VALID_COMPOSITION_BALANCE = {"regular", "asymmetric", "organic"}
VALID_HIERARCHY_STRENGTH = {"soft", "moderate", "strong", "dramatic"}
VALID_SURFACE_CHARACTER = {"flat", "layered", "paper", "atmospheric", "poster"}
VALID_SHAPE_CHARACTER = {"soft", "restrained", "sharp", "organic"}
VALID_ORNAMENT_EMPHASIS = {"none", "subtle", "selective", "prominent"}
VALID_INTERACTION_INTENSITY = {"gentle", "restrained", "deliberate", "assertive"}
VALID_RESPONSIVE_IDENTITY_PRIORITY = {"minimal", "preserve_core", "preserve_strong"}


@dataclass
class MaterialReference:
    """Contract for design materials / provenance assets."""
    id: str
    material_type: str
    asset_path: str = ""
    source: str = ""
    author: str = ""
    license: str = ""
    attribution: str = ""
    reference_ip: str = ""
    scope_lock: bool = True
    shared_resource_policy: str = "disallowed"

    def validate(self) -> None:
        """Validates material reference constraints, material_type contracts, and sharing policy consistency."""
        if not self.id or not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("MaterialReference 'id' must be a non-empty string.")
        if not self.material_type or not isinstance(self.material_type, str) or not self.material_type.strip():
            raise ValueError("MaterialReference 'material_type' must be a non-empty string.")
        if self.material_type not in VALID_MATERIAL_TYPES:
            raise ValueError(
                f"MaterialReference 'material_type' must be one of {VALID_MATERIAL_TYPES}, "
                f"got '{self.material_type}'."
            )
        if not isinstance(self.asset_path, str):
            raise TypeError("MaterialReference 'asset_path' must be a string.")
        if self.shared_resource_policy not in VALID_SHARED_RESOURCE_POLICIES:
            raise ValueError(
                f"MaterialReference 'shared_resource_policy' must be one of {VALID_SHARED_RESOURCE_POLICIES}, "
                f"got '{self.shared_resource_policy}'."
            )

        # Enforce canonical non-contradictory relationship:
        # Non-shared: scope_lock=True & shared_resource_policy="disallowed"
        # Shared:     scope_lock=False & shared_resource_policy="allowed"
        if self.scope_lock and self.shared_resource_policy != "disallowed":
            raise ValueError(
                "Contradictory material sharing state: when 'scope_lock' is True, "
                "'shared_resource_policy' must be 'disallowed'."
            )
        if not self.scope_lock and self.shared_resource_policy != "allowed":
            raise ValueError(
                "Contradictory material sharing state: when 'scope_lock' is False, "
                "'shared_resource_policy' must be 'allowed'."
            )


@dataclass(frozen=True)
class IdentityPresentationProjection:
    """Read-only bounded semantic presentation projection derived generically from Identity DesignDNA.

    Translates Identity DesignDNA semantic intent into typed presentation attributes:
    - hierarchy_contrast: str ('soft', 'moderate', 'strong', 'dramatic') -> typography/heading contrast emphasis
    - border_stroke_style: str ('solid', 'crisp', 'soft') -> bounded PARTIAL shape character
    - energy_emphasis: str ('quiet', 'restrained', 'balanced', 'expressive', 'aggressive') -> hover/focus elevation emphasis
    - surface_treatment: str ('flat', 'layered', 'paper', 'atmospheric', 'poster') -> bounded PARTIAL surface elevation/border treatment
    - transition_speed: str ('gentle', 'restrained', 'deliberate', 'assertive') -> motion transition speed
    """
    hierarchy_contrast: str = "strong"
    border_stroke_style: str = "solid"
    energy_emphasis: str = "balanced"
    surface_treatment: str = "flat"
    transition_speed: str = "deliberate"


@dataclass(frozen=True)
class PresentationPolicy:
    """Read-only presentation policy expressing Web / Information DNA behavior.

    CLASSIFICATION OF DIMENSIONS:
    - PRESENTATION POLICY (minimal & bounded to current consumers):
        - metadata_prominence: str (e.g. 'high', 'standard', 'minimal')
        - status_richness: str (e.g. 'rich', 'standard')
        - navigation_density: str (e.g. 'compact', 'standard')
        - secondary_compactness: bool
    - DEFERRED / INFORMATIONAL (tracked as semantic intent):
        - information_discoverability: str
        - utility_grouping: str
    """
    metadata_prominence: str = "standard"
    status_richness: str = "standard"
    navigation_density: str = "standard"
    secondary_compactness: bool = False
    information_discoverability: str = "standard"
    utility_grouping: str = "standard"


@dataclass
class DesignDNA:
    """Explicit Design DNA contract representing visual/design intent derived from a reference."""
    id: str
    display_name: str
    role: str = "identity"
    category: str = "generic"
    description: str = ""
    reference_identity: str = ""
    visual_character: str = ""
    color_direction: str = ""
    typography_direction: str = ""
    surface_language: str = ""
    shape_language: str = ""
    interaction_character: str = ""
    presentation_policy: Optional[PresentationPolicy] = None
    materials: List[MaterialReference] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    colors: Dict[str, str] = field(default_factory=dict)
    typography: Dict[str, Any] = field(default_factory=dict)
    spacing: Dict[str, str] = field(default_factory=dict)
    radius: Dict[str, str] = field(default_factory=dict)

    # S8.2 Production Semantic Dimensions (Optional with bounded validation when set)
    visual_energy: Optional[str] = None
    spatial_density: Optional[str] = None
    composition_balance: Optional[str] = None
    hierarchy_strength: Optional[str] = None
    surface_character: Optional[str] = None
    shape_character: Optional[str] = None
    ornament_emphasis: Optional[str] = None
    interaction_intensity: Optional[str] = None
    responsive_identity_priority: Optional[str] = None

    def validate(self) -> None:
        """Validates Design DNA contract constraints, role classification, semantic dimensions, and attached material references."""
        if not self.id or not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("DesignDNA 'id' must be a non-empty string.")
        if not self.display_name or not isinstance(self.display_name, str) or not self.display_name.strip():
            raise ValueError("DesignDNA 'display_name' must be a non-empty string.")
        if self.role not in VALID_DNA_ROLES:
            raise ValueError(
                f"DesignDNA 'role' must be one of {VALID_DNA_ROLES}, got '{self.role}'."
            )
        if self.role == "web_information" and not isinstance(self.presentation_policy, PresentationPolicy):
            raise ValueError("Web / Information DesignDNA requires a PresentationPolicy.")
        if self.role == "identity" and self.presentation_policy is not None:
            raise ValueError("Only Web / Information DesignDNA may define a PresentationPolicy.")

        # S8.2 Semantic Dimensions Bounded Validation
        if self.visual_energy is not None and self.visual_energy not in VALID_VISUAL_ENERGY:
            raise ValueError(
                f"DesignDNA 'visual_energy' must be one of {VALID_VISUAL_ENERGY}, got '{self.visual_energy}'."
            )
        if self.spatial_density is not None and self.spatial_density not in VALID_SPATIAL_DENSITY:
            raise ValueError(
                f"DesignDNA 'spatial_density' must be one of {VALID_SPATIAL_DENSITY}, got '{self.spatial_density}'."
            )
        if self.composition_balance is not None and self.composition_balance not in VALID_COMPOSITION_BALANCE:
            raise ValueError(
                f"DesignDNA 'composition_balance' must be one of {VALID_COMPOSITION_BALANCE}, got '{self.composition_balance}'."
            )
        if self.hierarchy_strength is not None and self.hierarchy_strength not in VALID_HIERARCHY_STRENGTH:
            raise ValueError(
                f"DesignDNA 'hierarchy_strength' must be one of {VALID_HIERARCHY_STRENGTH}, got '{self.hierarchy_strength}'."
            )
        if self.surface_character is not None and self.surface_character not in VALID_SURFACE_CHARACTER:
            raise ValueError(
                f"DesignDNA 'surface_character' must be one of {VALID_SURFACE_CHARACTER}, got '{self.surface_character}'."
            )
        if self.shape_character is not None and self.shape_character not in VALID_SHAPE_CHARACTER:
            raise ValueError(
                f"DesignDNA 'shape_character' must be one of {VALID_SHAPE_CHARACTER}, got '{self.shape_character}'."
            )
        if self.ornament_emphasis is not None and self.ornament_emphasis not in VALID_ORNAMENT_EMPHASIS:
            raise ValueError(
                f"DesignDNA 'ornament_emphasis' must be one of {VALID_ORNAMENT_EMPHASIS}, got '{self.ornament_emphasis}'."
            )
        if self.interaction_intensity is not None and self.interaction_intensity not in VALID_INTERACTION_INTENSITY:
            raise ValueError(
                f"DesignDNA 'interaction_intensity' must be one of {VALID_INTERACTION_INTENSITY}, got '{self.interaction_intensity}'."
            )
        if self.responsive_identity_priority is not None and self.responsive_identity_priority not in VALID_RESPONSIVE_IDENTITY_PRIORITY:
            raise ValueError(
                f"DesignDNA 'responsive_identity_priority' must be one of {VALID_RESPONSIVE_IDENTITY_PRIORITY}, got '{self.responsive_identity_priority}'."
            )

        for material in self.materials:
            if not isinstance(material, MaterialReference):
                raise TypeError("All items in 'materials' must be instances of MaterialReference.")
            material.validate()


@dataclass(frozen=True)
class DesignComposition:
    """Immutable contract declaring independent role selections for composition.

    Referenced by identity IDs rather than duplicating full DNA objects.
    - identity_dna_id: ID of DNA with role 'identity'
    - web_information_dna_id: Optional ID of DNA with role 'web_information'
    - archetype_id: Active canonical archetype ID (e.g. 'chat_first')
    """
    identity_dna_id: str
    web_information_dna_id: Optional[str] = None
    archetype_id: str = "chat_first"

    def validate(self) -> None:
        """Validates basic composition field constraints."""
        if not self.identity_dna_id or not isinstance(self.identity_dna_id, str) or not self.identity_dna_id.strip():
            raise ValueError("DesignComposition 'identity_dna_id' must be a non-empty string.")
        if self.web_information_dna_id is not None:
            if not isinstance(self.web_information_dna_id, str) or not self.web_information_dna_id.strip():
                raise ValueError("DesignComposition 'web_information_dna_id' must be a non-empty string if provided.")
        if not self.archetype_id or not isinstance(self.archetype_id, str) or not self.archetype_id.strip():
            raise ValueError("DesignComposition 'archetype_id' must be a non-empty string.")


@dataclass(frozen=True)
class ComposedProjection:
    """Read-only resolved projection produced deterministically from a DesignComposition.

    - theme: Resolved S5 Theme contract instance (primary visual tokens owned by Identity DNA)
    - presentation_policy: Bounded presentation policy (owned by Web / Information DNA)
    - archetype_id: Active archetype ID (owned by UI/UX Archetype)
    - materials: Tuple of resolved MaterialReference objects
    - provenance: Immutable metadata mapping tracking role provenance
    """
    theme: Any
    presentation_policy: PresentationPolicy
    archetype_id: str
    identity_projection: Optional[IdentityPresentationProjection] = None
    materials: Tuple[MaterialReference, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
