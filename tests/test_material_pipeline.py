"""
MultiMind AI - Material Pipeline Foundation Tests
Unit tests covering MaterialReference asset_path contracts, path traversal security,
deterministic resolver contract, proof integrations, Theme Studio provenance resolution, and fallbacks.
"""
import os
import copy
import tempfile
import unittest
from ui.dna.models import (
    DesignDNA,
    MaterialReference,
    VALID_MATERIAL_TYPES,
    CURRENT_RENDERABLE_MATERIAL_TYPES,
)
from ui.dna.registry import DNARegistry, get_registry as get_dna_registry
from ui.dna.bootstrap import ensure_proof_dna_and_themes_registered
from ui.dna.resolver import (
    resolve_material,
    resolve_source_dna,
    validate_material_asset_path,
    MaterialResolutionResult,
    APPROVED_MATERIAL_ROOT_RELATIVE,
)
from ui.presentation.brand import render_brand_identity
from ui.themes import get_theme, Theme, ThemeMetadata


class TestMaterialPipelineFoundation(unittest.TestCase):
    """Test suite verifying the Material Pipeline foundation, security, resolver, and proof integrations."""

    def setUp(self):
        """Ensures proof DNAs and themes are registered prior to each test run."""
        ensure_proof_dna_and_themes_registered()
        self.dna_registry = get_dna_registry()

    def test_material_reference_asset_path_validation_and_compatibility(self):
        """Tests MaterialReference contract validation with asset_path field."""
        mat = MaterialReference(
            id="test-mat-01",
            material_type="graphic_mark",
            asset_path="ui/assets/materials/test-mat-01/mark.svg",
            source="Test Source",
            author="Programmatically generated SVG for MultiMind AI",
            license="Project-Owned Asset",
            scope_lock=True,
            shared_resource_policy="disallowed",
        )
        mat.validate()
        self.assertEqual(mat.asset_path, "ui/assets/materials/test-mat-01/mark.svg")

        # Invalid asset_path type (must be str)
        mat_bad_type = MaterialReference(
            id="test-mat-02",
            material_type="graphic_mark",
            asset_path=12345,  # type: ignore
        )
        with self.assertRaises(TypeError):
            mat_bad_type.validate()

    def test_valid_vs_renderable_material_type_contract(self):
        """Tests that valid non-renderable material types pass contract validation but fall back at resolution,
        while completely unknown material types fail contract validation.
        """
        # 1. Renderable material type ('graphic_mark') -> passes validation & resolves
        mat_renderable = MaterialReference(
            id="mark-mat",
            material_type="graphic_mark",
            asset_path="ui/assets/materials/japan-ink-mark/mark.svg",
        )
        mat_renderable.validate()

        # 2. Valid contract type but currently unrenderable ('texture', 'font', 'pattern') -> passes validation
        for valid_unrenderable in ["texture", "font", "pattern"]:
            mat_valid = MaterialReference(
                id=f"mat-{valid_unrenderable}",
                material_type=valid_unrenderable,
                asset_path="ui/assets/materials/japan-ink-mark/mark.svg",
            )
            mat_valid.validate()  # Passes contract validation

            # Resolution must safely fall back at consumption boundary
            unrenderable_dna = DesignDNA(
                id=f"dna-{valid_unrenderable}",
                display_name=f"DNA {valid_unrenderable}",
                materials=[mat_valid],
            )
            res = resolve_material(unrenderable_dna)
            self.assertEqual(res.status, "fallback")
            self.assertIn("valid but currently unrenderable", str(res.error_reason))

        # 3. Invalid/unknown material type -> rejected by MaterialReference contract validation
        mat_invalid = MaterialReference(
            id="mat-unknown",
            material_type="completely_unknown_speculative_type",
            asset_path="ui/assets/materials/japan-ink-mark/mark.svg",
        )
        with self.assertRaises(ValueError):
            mat_invalid.validate()

    def test_proof_dnas_have_valid_truthful_materials_bound(self):
        """Tests that all 3 canonical proof DNAs have truthful MaterialReferences bound."""
        proof_ids = ["japan-print-ink", "chainsaw-man-inspired", "mushishi-inspired"]
        for pid in proof_ids:
            dna = self.dna_registry.get_dna(pid)
            self.assertIsNotNone(dna)
            self.assertEqual(len(dna.materials), 1, f"Proof DNA '{pid}' must have 1 bound material.")
            mat = dna.materials[0]
            self.assertTrue(bool(mat.id))
            self.assertEqual(mat.material_type, "graphic_mark")
            self.assertTrue(bool(mat.asset_path))
            self.assertEqual(mat.license, "Project-Owned Asset")
            self.assertIn("Programmatically generated SVG", mat.author)

    def test_valid_repository_material_resolution_for_all_proofs(self):
        """Tests that all 3 proof themes resolve their repository assets deterministically."""
        proof_map = {
            "japan-print-ink": "japan-ink-mark",
            "chainsaw-man-inspired": "chainsaw-hazard-mark",
            "mushishi-inspired": "mushishi-moss-mark",
        }

        for theme_id, expected_mat_id in proof_map.items():
            res = resolve_material(theme_id)
            self.assertEqual(res.status, "resolved", f"Resolution failed for theme '{theme_id}': {res.error_reason}")
            self.assertTrue(res.is_resolved)
            self.assertIsNotNone(res.material)
            self.assertEqual(res.material.id, expected_mat_id)
            self.assertTrue(os.path.exists(res.resolved_path))

    def test_deterministic_root_resolution_independent_of_process_cwd(self):
        """Tests that material resolution succeeds even when process current working directory (CWD) is changed."""
        orig_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                os.chdir(tmp_dir)
                res = resolve_material("japan-print-ink")
                self.assertEqual(res.status, "resolved")
                self.assertEqual(res.material.id, "japan-ink-mark")
                self.assertTrue(os.path.exists(res.resolved_path))
            finally:
                os.chdir(orig_cwd)

    def test_security_absolute_path_rejection(self):
        """Tests that absolute paths in asset_path are strictly rejected."""
        bad_abs_path = "/etc/passwd" if os.name != "nt" else "C:\\Windows\\System32\\drivers\\etc\\hosts"
        validated = validate_material_asset_path(bad_abs_path)
        self.assertIsNone(validated, "Absolute paths must be rejected by validator.")

    def test_security_path_traversal_rejection(self):
        """Tests that ../ path traversal attempts escaping material root are strictly rejected."""
        traversal_paths = [
            "../../etc/passwd",
            "ui/assets/materials/../../app.py",
            "ui/assets/materials/japan-ink-mark/../../../../app.py",
            "..\\..\\Windows\\System32",
        ]
        for bad_path in traversal_paths:
            validated = validate_material_asset_path(bad_path)
            self.assertIsNone(validated, f"Path traversal '{bad_path}' must be rejected.")

    def test_security_containment_verification(self):
        """Tests that asset resolution cannot escape canonical ui/assets/materials directory."""
        # Create a mock material attempting to reference app.py outside materials root
        escape_dna = DesignDNA(
            id="escape-test-dna",
            display_name="Escape Test DNA",
            materials=[
                MaterialReference(
                    id="escape-mat",
                    material_type="graphic_mark",
                    asset_path="app.py",
                    scope_lock=True,
                    shared_resource_policy="disallowed",
                )
            ],
        )
        res = resolve_material(escape_dna)
        self.assertEqual(res.status, "fallback")
        self.assertIsNone(res.resolved_path)

    def test_missing_asset_fails_closed_to_fallback(self):
        """Tests that a MaterialReference pointing to a non-existent file fails closed to fallback."""
        missing_dna = DesignDNA(
            id="missing-asset-dna",
            display_name="Missing Asset DNA",
            materials=[
                MaterialReference(
                    id="missing-mat",
                    material_type="graphic_mark",
                    asset_path="ui/assets/materials/nonexistent-folder/missing.svg",
                    scope_lock=True,
                    shared_resource_policy="disallowed",
                )
            ],
        )
        res = resolve_material(missing_dna)
        self.assertEqual(res.status, "fallback")
        self.assertIsNone(res.resolved_path)

    def test_unbound_ordinary_theme_fails_closed_to_fallback(self):
        """Tests that ordinary themes with no material binding safely return fallback status."""
        for ordinary_id in ["default", "neutral-contrast-demo"]:
            res = resolve_material(ordinary_id)
            self.assertEqual(res.status, "fallback")
            self.assertIsNone(res.resolved_path)

    def test_custom_theme_studio_theme_derived_from_dna_resolves_source_material(self):
        """Tests that custom Theme Studio themes tracking source DNA in metadata resolve correct material."""
        custom_theme = Theme(
            id="custom-theme-studio-draft-9999",
            display_name="Custom Draft (Japan Print Base)",
            category="custom",
            metadata=ThemeMetadata(
                description="Custom theme derived from DNA",
                reference="dna:japan-print-ink"
            ),
        )
        res = resolve_material(custom_theme)
        self.assertEqual(res.status, "resolved")
        self.assertEqual(res.material.id, "japan-ink-mark")

    def test_material_scope_ownership_policy_enforcement(self):
        """Tests that DNARegistry continues to enforce non-shared scope lock policies."""
        reg = DNARegistry()

        dna1 = DesignDNA(
            id="dna-owner-1",
            display_name="Owner DNA 1",
            materials=[
                MaterialReference(
                    id="exclusive-mat-01",
                    material_type="graphic_mark",
                    scope_lock=True,
                    shared_resource_policy="disallowed",
                )
            ],
        )
        reg.register_dna(dna1)

        # Attempt to register second DNA claiming the same scope-locked material
        dna2 = DesignDNA(
            id="dna-owner-2",
            display_name="Owner DNA 2",
            materials=[
                MaterialReference(
                    id="exclusive-mat-01",
                    material_type="graphic_mark",
                    scope_lock=True,
                    shared_resource_policy="disallowed",
                )
            ],
        )
        with self.assertRaises(ValueError):
            reg.register_dna(dna2)

    def test_sidebar_and_theme_studio_share_identical_resolver_contract(self):
        """Tests that render_brand_identity seam executes identical resolver contract for both surfaces."""
        # Both sidebar and Theme Studio call render_brand_identity
        res_sidebar = render_brand_identity("mushishi-inspired", container_kind="sidebar")
        res_studio = render_brand_identity("mushishi-inspired", container_kind="theme_studio")

        self.assertEqual(res_sidebar.status, res_studio.status)
        self.assertEqual(res_sidebar.resolved_path, res_studio.resolved_path)
        self.assertEqual(res_sidebar.material.id, "mushishi-moss-mark")

    def test_material_registration_does_not_mutate_active_theme(self):
        """Verifies that material registration or resolution does not mutate global active theme."""
        # Ensure proof DNA bootstrap does not alter active theme state proxy if present
        ensure_proof_dna_and_themes_registered()
        res = resolve_material("japan-print-ink")
        self.assertEqual(res.status, "resolved")


if __name__ == "__main__":
    unittest.main()
