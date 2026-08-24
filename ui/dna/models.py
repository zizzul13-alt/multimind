"""
MultiMind AI - Design DNA Contract Models
Defines dataclasses for Design DNA, Material References, and Provenance Metadata.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

VALID_SHARED_RESOURCE_POLICIES = {"disallowed", "allowed"}

# Controlled Material Taxonomy: contract-level valid types vs currently renderable types
VALID_MATERIAL_TYPES = {"graphic_mark", "texture", "font", "pattern"}
CURRENT_RENDERABLE_MATERIAL_TYPES = {"graphic_mark"}


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


@dataclass
class DesignDNA:
    """Explicit Design DNA contract representing visual/design intent derived from a reference."""
    id: str
    display_name: str
    category: str = "generic"
    description: str = ""
    reference_identity: str = ""
    visual_character: str = ""
    color_direction: str = ""
    typography_direction: str = ""
    surface_language: str = ""
    shape_language: str = ""
    interaction_character: str = ""
    materials: List[MaterialReference] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    colors: Dict[str, str] = field(default_factory=dict)
    typography: Dict[str, Any] = field(default_factory=dict)
    spacing: Dict[str, str] = field(default_factory=dict)
    radius: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        """Validates Design DNA contract constraints and attached material references."""
        if not self.id or not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("DesignDNA 'id' must be a non-empty string.")
        if not self.display_name or not isinstance(self.display_name, str) or not self.display_name.strip():
            raise ValueError("DesignDNA 'display_name' must be a non-empty string.")

        for material in self.materials:
            if not isinstance(material, MaterialReference):
                raise TypeError("All items in 'materials' must be instances of MaterialReference.")
            material.validate()
