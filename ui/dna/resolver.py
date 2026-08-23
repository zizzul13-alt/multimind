"""
MultiMind AI - Material Resolver Core
Deterministic, generic resolution engine that maps Themes and Design DNAs
to validated repository material assets with strict path containment security.
"""
from dataclasses import dataclass
import os
import logging
from typing import Optional, Union, Any, List

from ui.dna.models import DesignDNA, MaterialReference
from ui.dna import get_registry as get_dna_registry
from ui.themes import get_theme, Theme

logger = logging.getLogger(__name__)

# Canonical relative path to approved UI material root
APPROVED_MATERIAL_ROOT_RELATIVE = os.path.join("ui", "assets", "materials")


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

    # Case 1: Direct DesignDNA instance
    if isinstance(theme_or_dna_input, DesignDNA):
        return theme_or_dna_input

    dna_reg = get_dna_registry()

    # Case 2: String ID (Theme ID or Design DNA ID)
    if isinstance(theme_or_dna_input, str):
        clean_id = theme_or_dna_input.strip()
        if not clean_id:
            return None

        # Direct DNA lookup
        dna = dna_reg.get_dna(clean_id)
        if dna:
            return dna

        # Parse prefix if present (e.g. "dna:japan-print-ink" or "theme:japan-print-ink")
        if ":" in clean_id:
            raw_target = clean_id.split(":", 1)[-1].strip()
            dna_target = dna_reg.get_dna(raw_target)
            if dna_target:
                return dna_target

        # Registered Theme lookup & provenance metadata inspection
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

    # Case 3: Theme object
    if isinstance(theme_or_dna_input, Theme):
        # Direct lookup by Theme ID
        dna = dna_reg.get_dna(theme_or_dna_input.id)
        if dna:
            return dna

        # Metadata provenance inspection for custom Theme instances
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
    """
    Validates that raw_asset_path is repository-relative, contained strictly within
    the approved material root, exists on disk as a file, and does not perform path traversal.

    Returns the absolute path if valid, or None if invalid/unsafe.
    """
    if not raw_asset_path or not isinstance(raw_asset_path, str) or not raw_asset_path.strip():
        return None

    clean_path = raw_asset_path.strip()

    # Security check 1: Reject absolute paths
    if os.path.isabs(clean_path):
        logger.warning(f"Material asset path rejected: absolute path '{clean_path}' is disallowed.")
        return None

    base_dir = os.path.abspath(root_dir or APPROVED_MATERIAL_ROOT_RELATIVE)
    target_abs = os.path.abspath(clean_path)

    # Security check 2: Strict path containment verification using commonpath
    try:
        common = os.path.commonpath([base_dir, target_abs])
        if common != base_dir:
            logger.warning(f"Material asset path rejected: '{clean_path}' escapes material root '{base_dir}'.")
            return None
    except (ValueError, Exception) as e:
        logger.warning(f"Material asset path containment check failed for '{clean_path}': {e}")
        return None

    # Security check 3: Prefix verification
    if not (target_abs == base_dir or target_abs.startswith(base_dir + os.sep)):
        logger.warning(f"Material asset path rejected: '{clean_path}' does not reside inside material root.")
        return None

    # Security check 4: Expected file existence and type
    if not os.path.isfile(target_abs):
        logger.warning(f"Material asset path rejected: file does not exist at '{target_abs}'.")
        return None

    return target_abs


def resolve_material(
    theme_or_dna_input: Union[str, Theme, DesignDNA, None],
    material_type: Optional[str] = None,
    material_root: Optional[str] = None
) -> MaterialResolutionResult:
    """
    Deterministic material resolution entry point.
    Resolves the source DesignDNA for the given theme/DNA input, finds the matching
    MaterialReference, validates the asset path containment, and returns a MaterialResolutionResult.
    """
    dna = resolve_source_dna(theme_or_dna_input)
    if not dna or not dna.materials:
        return MaterialResolutionResult(
            status="fallback",
            error_reason="No DesignDNA or materials bound to input"
        )

    # Find matching material by type, or use first bound material as default
    target_mat: Optional[MaterialReference] = None
    if material_type:
        for mat in dna.materials:
            if mat.material_type == material_type:
                target_mat = mat
                break
    else:
        target_mat = dna.materials[0]

    if not target_mat or not target_mat.asset_path:
        return MaterialResolutionResult(
            status="fallback",
            error_reason="No matching MaterialReference or missing asset_path"
        )

    validated_abs_path = validate_material_asset_path(target_mat.asset_path, root_dir=material_root)
    if not validated_abs_path:
        return MaterialResolutionResult(
            status="fallback",
            material=target_mat,
            error_reason=f"Asset path '{target_mat.asset_path}' failed security or existence validation"
        )

    return MaterialResolutionResult(
        status="resolved",
        material=target_mat,
        resolved_path=validated_abs_path
    )
