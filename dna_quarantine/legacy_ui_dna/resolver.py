"""
MultiMind AI - Material Resolver Core
Deterministic, generic resolution engine that maps Themes and Design DNAs
to validated repository material assets with strict path containment security.
"""
from dataclasses import dataclass
import os
import logging
from types import MappingProxyType
from typing import Optional, Union, Any, Dict

from .models import (
    DesignDNA,
    MaterialReference,
    VALID_MATERIAL_TYPES,
    CURRENT_RENDERABLE_MATERIAL_TYPES,
    IdentityPresentationProjection,
)
from .registry import get_registry as get_dna_registry
from ui.themes import get_theme, Theme

logger = logging.getLogger(__name__)

# Absolute path to repository root, anchored deterministically to this module file
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_MODULE_DIR, "..", ".."))

# Canonical relative path and absolute root for approved UI materials
APPROVED_MATERIAL_ROOT_RELATIVE = os.path.join("ui", "assets", "materials")
APPROVED_MATERIAL_ROOT_ABS = os.path.abspath(os.path.join(_REPO_ROOT, APPROVED_MATERIAL_ROOT_RELATIVE))


@dataclass
class MaterialResolutionResult:
    """Read-only result payload returned by the material resolver."""
    status: str  # "resolved" | "fallback"
    material: Optional[MaterialReference] = None
    resolved_path: Optional[str] = None
    error_reason: Optional[str] = None

    @property
    def is_resolved(self) -> bool:
        return self.status == "resolved" and bool(self.resolved_path)


def resolve_source_dna(theme_or_dna_input: Union[str, Theme, DesignDNA, None]) -> Optional[DesignDNA]:
    """
    Deterministically resolves a DesignDNA instance from a theme ID, Theme object,
    or DesignDNA object without theme-specific branching.
    """
    if theme_or_dna_input is None:
        return None

    if isinstance(theme_or_dna_input, DesignDNA):
        return theme_or_dna_input

    dna_reg = get_dna_registry()

    if isinstance(theme_or_dna_input, str):
        clean_id = theme_or_dna_input.strip()
        if not clean_id:
            return None

        dna = dna_reg.get_dna(clean_id)
        if dna:
            return dna

        if ":" in clean_id:
            raw_target = clean_id.split(":", 1)[-1].strip()
            dna_target = dna_reg.get_dna(raw_target)
            if dna_target:
                return dna_target

        theme = get_theme(clean_id)
        if theme and theme.metadata:
            for candidate_field in (theme.metadata.reference, theme.metadata.source):
                if candidate_field:
                    ref_id = candidate_field.strip()
                    if ":" in ref_id:
                        ref_id = ref_id.split(":", 1)[-1].strip()
                    dna_from_meta = dna_reg.get_dna(ref_id)
                    if dna_from_meta:
                        return dna_from_meta

        return None

    if isinstance(theme_or_dna_input, Theme):
        dna = dna_reg.get_dna(theme_or_dna_input.id)
        if dna:
            return dna

        if theme_or_dna_input.metadata:
            for candidate_field in (theme_or_dna_input.metadata.reference, theme_or_dna_input.metadata.source):
                if candidate_field:
                    ref_id = candidate_field.strip()
                    if ":" in ref_id:
                        ref_id = ref_id.split(":", 1)[-1].strip()
                    dna_from_meta = dna_reg.get_dna(ref_id)
                    if dna_from_meta:
                        return dna_from_meta

        return None

    return None


def validate_material_asset_path(raw_asset_path: str, root_dir: Optional[str] = None) -> Optional[str]:
    """Validate repository-relative material path containment and file existence."""
    if not raw_asset_path or not isinstance(raw_asset_path, str) or not raw_asset_path.strip():
        return None

    clean_path = raw_asset_path.strip()
    if os.path.isabs(clean_path):
        logger.warning(f"Material asset path rejected: absolute path '{clean_path}' is disallowed.")
        return None

    base_dir = os.path.abspath(root_dir) if root_dir else APPROVED_MATERIAL_ROOT_ABS
    target_abs = os.path.abspath(os.path.join(_REPO_ROOT, clean_path))

    try:
        common = os.path.commonpath([base_dir, target_abs])
        if common != base_dir:
            logger.warning(f"Material asset path rejected: '{clean_path}' escapes material root '{base_dir}'.")
            return None
    except (ValueError, Exception) as e:
        logger.warning(f"Material asset path containment check failed for '{clean_path}': {e}")
        return None

    if not (target_abs == base_dir or target_abs.startswith(base_dir + os.sep)):
        logger.warning(f"Material asset path rejected: '{clean_path}' does not reside inside material root.")
        return None

    if not os.path.isfile(target_abs):
        logger.warning(f"Material asset path rejected: file does not exist at '{target_abs}'.")
        return None

    return target_abs


def resolve_material(
    theme_or_dna_input: Union[str, Theme, DesignDNA, None],
    material_type: Optional[str] = None,
    material_root: Optional[str] = None
) -> MaterialResolutionResult:
    """Resolve a validated material with safe fallback."""
    dna = resolve_source_dna(theme_or_dna_input)
    if not dna or not dna.materials:
        return MaterialResolutionResult(status="fallback", error_reason="No DesignDNA or materials bound to input")

    target_mat: Optional[MaterialReference] = None
    if material_type:
        for mat in dna.materials:
            if mat.material_type == material_type:
                target_mat = mat
                break
    else:
        target_mat = dna.materials[0]

    if not target_mat or not target_mat.asset_path:
        return MaterialResolutionResult(status="fallback", error_reason="No matching MaterialReference or missing asset_path")

    if target_mat.material_type not in CURRENT_RENDERABLE_MATERIAL_TYPES:
        return MaterialResolutionResult(
            status="fallback",
            material=target_mat,
            error_reason=f"Material type '{target_mat.material_type}' is valid but currently unrenderable"
        )

    validated_abs_path = validate_material_asset_path(target_mat.asset_path, root_dir=material_root)
    if not validated_abs_path:
        return MaterialResolutionResult(
            status="fallback",
            material=target_mat,
            error_reason=f"Asset path '{target_mat.asset_path}' failed security or existence validation"
        )

    return MaterialResolutionResult(status="resolved", material=target_mat, resolved_path=validated_abs_path)


def resolve_identity_projection(identity_dna: Optional[DesignDNA]) -> IdentityPresentationProjection:
    """Deterministically project Identity DesignDNA semantic intent."""
    if not identity_dna:
        return IdentityPresentationProjection()

    shape_char = identity_dna.shape_character
    border_style = "crisp" if shape_char == "sharp" else ("soft" if shape_char in ("organic", "soft") else "solid")

    return IdentityPresentationProjection(
        hierarchy_contrast=identity_dna.hierarchy_strength or "strong",
        border_stroke_style=border_style,
        energy_emphasis=identity_dna.visual_energy or "balanced",
        surface_treatment=identity_dna.surface_character or "flat",
        transition_speed=identity_dna.interaction_intensity or "deliberate",
    )


# ==============================================================================
# S8.1 DESIGN DNA COMPOSITION RESOLVER
# ==============================================================================

from .models import DesignComposition, ComposedProjection, PresentationPolicy
from .mapper import dna_to_theme


def resolve_composition(
    composition: DesignComposition,
    dna_registry=None
) -> ComposedProjection:
    """Deterministically resolve a DesignComposition into a ComposedProjection.

    The presentation-archetype dependency is imported lazily so the quarantined
    resolver remains safe when legacy public compatibility shims are importing it.
    """
    from ui.presentation.resolver import get_archetype_definition, CANONICAL_ARCHETYPE_IDS

    if not isinstance(composition, DesignComposition):
        raise TypeError("composition must be an instance of DesignComposition.")

    composition.validate()

    if dna_registry is not None:
        identity_dna = dna_registry.get_dna(composition.identity_dna_id)
    else:
        identity_dna = get_dna_registry().get_dna(composition.identity_dna_id)

    if not identity_dna:
        raise ValueError(f"Identity DesignDNA with ID '{composition.identity_dna_id}' is not registered.")

    if identity_dna.role != "identity":
        raise ValueError(
            f"DesignDNA '{identity_dna.id}' has role '{identity_dna.role}', "
            f"but was provided as identity_dna_id (expected role 'identity')."
        )

    web_dna: Optional[DesignDNA] = None
    if composition.web_information_dna_id:
        if dna_registry is not None:
            web_dna = dna_registry.get_dna(composition.web_information_dna_id)
        else:
            web_dna = get_dna_registry().get_dna(composition.web_information_dna_id)

        if not web_dna:
            raise ValueError(
                f"Web / Information DesignDNA with ID '{composition.web_information_dna_id}' is not registered."
            )

        if web_dna.role != "web_information":
            raise ValueError(
                f"DesignDNA '{web_dna.id}' has role '{web_dna.role}', "
                f"but was provided as web_information_dna_id (expected role 'web_information')."
            )

    arch_def = get_archetype_definition(composition.archetype_id)
    if composition.archetype_id not in CANONICAL_ARCHETYPE_IDS:
        raise ValueError(f"Archetype ID '{composition.archetype_id}' is not a recognized canonical archetype.")

    theme_instance = dna_to_theme(identity_dna)

    if web_dna and web_dna.presentation_policy:
        policy = web_dna.presentation_policy
    else:
        is_compact = identity_dna.spatial_density in ("compact", "dense")
        policy = PresentationPolicy(secondary_compactness=is_compact)

    registry = dna_registry if dna_registry is not None else get_dna_registry()
    resolved_materials = registry.combine_materials(identity_dna, web_dna)

    provenance: Dict[str, Any] = {
        "identity_dna_id": identity_dna.id,
        "web_information_dna_id": web_dna.id if web_dna else None,
        "archetype_id": arch_def.id,
        "identity_display_name": identity_dna.display_name,
        "web_information_display_name": web_dna.display_name if web_dna else None,
        "archetype_display_name": arch_def.display_name,
    }

    identity_proj = resolve_identity_projection(identity_dna)

    return ComposedProjection(
        theme=theme_instance,
        presentation_policy=policy,
        archetype_id=arch_def.id,
        identity_projection=identity_proj,
        materials=resolved_materials,
        provenance=MappingProxyType(provenance),
    )
