"""
MultiMind AI - Design DNA Tests
Unit tests covering Design DNA contract models, MaterialReference constraints,
DNARegistry material ownership policies, pure adapter mapping, and S6.2 proof definitions.
"""
import copy
import unittest
from ui.dna.models import DesignDNA, MaterialReference
from ui.dna.registry import DNARegistry, get_registry
from ui.dna.mapper import dna_to_theme
from ui.themes.registry import ThemeRegistry
from ui import tokens


class TestDesignDNA(unittest.TestCase):
    """Test suite verifying Design DNA contract models, material ownership policies, and mapper adapter."""

    def setUp(self):
        """Prepares isolated registry instances for clean test runs."""
        self.dna_registry = DNARegistry()
        self.theme_registry = ThemeRegistry()

    def test_material_reference_contract_validation_and_canonical_sharing_policy(self):
        """Tests MaterialReference contract validation and canonical sharing policy rule enforcement."""
        # Valid reference-specific (non-shared) material
        mat_locked = MaterialReference(
            id="mat-editorial-paper",
            material_type="texture",
            scope_lock=True,
            shared_resource_policy="disallowed"
        )
        mat_locked.validate()

        # Valid explicitly shared material
        mat_shared = MaterialReference(
            id="mat-font-serif",
            material_type="font",
            scope_lock=False,
            shared_resource_policy="allowed"
        )
        mat_shared.validate()

        # Contradiction Case A: scope_lock=True but shared_resource_policy="allowed"
        mat_invalid_a = MaterialReference(
            id="mat-invalid-a",
            material_type="font",
            scope_lock=True,
            shared_resource_policy="allowed"
        )
        with self.assertRaises(ValueError):
            mat_invalid_a.validate()

        # Contradiction Case B: scope_lock=False but shared_resource_policy="disallowed"
        mat_invalid_b = MaterialReference(
            id="mat-invalid-b",
            material_type="font",
            scope_lock=False,
            shared_resource_policy="disallowed"
        )
        with self.assertRaises(ValueError):
            mat_invalid_b.validate()

        # Invalid empty ID
        mat_empty_id = MaterialReference(id="", material_type="font")
        with self.assertRaises(ValueError):
            mat_empty_id.validate()

        # Invalid policy string
        mat_bad_policy = MaterialReference(
            id="mat-bad-policy",
            material_type="font",
            shared_resource_policy="invalid_policy"
        )
        with self.assertRaises(ValueError):
            mat_bad_policy.validate()

    def test_design_dna_contract_validation(self):
        """Tests DesignDNA dataclass validation constraints."""
        dna = DesignDNA(
            id="test-editorial-dna",
            display_name="Test Editorial DNA",
            category="generic",
            materials=[
                MaterialReference(
                    id="mat-editorial-paper",
                    material_type="texture",
                    scope_lock=True,
                    shared_resource_policy="disallowed"
                )
            ]
        )
        dna.validate()

        # Invalid empty ID
        dna_invalid_id = DesignDNA(id="", display_name="Test DNA")
        with self.assertRaises(ValueError):
            dna_invalid_id.validate()

        # Invalid materials list element type
        dna_invalid_mat = DesignDNA(
            id="test-dna",
            display_name="Test DNA",
            materials=["not_a_material_reference_object"]  # type: ignore
        )
        with self.assertRaises(TypeError):
            dna_invalid_mat.validate()

    def test_dna_registry_registration_lookup_and_duplicates(self):
        """Tests DNARegistry registration, listing, lookup, and duplicate ID prevention."""
        dna = DesignDNA(
            id="test-editorial-dna",
            display_name="Test Editorial DNA",
            category="generic"
        )
        self.dna_registry.register_dna(dna)

        registered = self.dna_registry.list_dna()
        self.assertEqual(len(registered), 1)
        self.assertEqual(registered[0].id, "test-editorial-dna")

        retrieved = self.dna_registry.get_dna("test-editorial-dna")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.display_name, "Test Editorial DNA")

        # Unknown DNA lookup must return None (no default fallback)
        self.assertIsNone(self.dna_registry.get_dna("nonexistent-dna-id"))
        self.assertIsNone(self.dna_registry.get_dna(None))
        self.assertIsNone(self.dna_registry.get_dna("   "))

        # Duplicate ID registration must raise ValueError
        duplicate_dna = DesignDNA(
            id="test-editorial-dna",
            display_name="Duplicate Editorial DNA"
        )
        with self.assertRaises(ValueError):
            self.dna_registry.register_dna(duplicate_dna)

    def test_material_scope_ownership_and_shared_resource_policy_cases(self):
        """Tests all 4 material scope ownership and sharing policy cases strictly."""
        # Setup Case 1 & 2: Original material is non-shared (locked)
        mat_locked_orig = MaterialReference(
            id="mat-locked-01",
            material_type="graphic",
            scope_lock=True,
            shared_resource_policy="disallowed"
        )
        dna_owner_locked = DesignDNA(
            id="dna-owner-locked",
            display_name="Locked Owner DNA",
            materials=[mat_locked_orig]
        )
        self.dna_registry.register_dna(dna_owner_locked)

        # Case 1: Original non-shared + incoming non-shared -> reject
        dna_case1 = DesignDNA(
            id="dna-case1",
            display_name="Case 1 DNA",
            materials=[
                MaterialReference(
                    id="mat-locked-01",
                    material_type="graphic",
                    scope_lock=True,
                    shared_resource_policy="disallowed"
                )
            ]
        )
        with self.assertRaises(ValueError):
            self.dna_registry.register_dna(dna_case1)

        # Case 2: Original non-shared + incoming claims shared -> reject (CANNOT bypass original locked policy)
        dna_case2 = DesignDNA(
            id="dna-case2",
            display_name="Case 2 DNA",
            materials=[
                MaterialReference(
                    id="mat-locked-01",
                    material_type="graphic",
                    scope_lock=False,
                    shared_resource_policy="allowed"
                )
            ]
        )
        with self.assertRaises(ValueError):
            self.dna_registry.register_dna(dna_case2)

        # Setup Case 3 & 4: Original material is explicitly shared
        mat_shared_orig = MaterialReference(
            id="mat-shared-01",
            material_type="font",
            scope_lock=False,
            shared_resource_policy="allowed"
        )
        dna_owner_shared = DesignDNA(
            id="dna-owner-shared",
            display_name="Shared Owner DNA",
            materials=[mat_shared_orig]
        )
        self.dna_registry.register_dna(dna_owner_shared)

        # Case 3: Original shared + incoming shared -> allow
        dna_case3 = DesignDNA(
            id="dna-case3",
            display_name="Case 3 DNA",
            materials=[
                MaterialReference(
                    id="mat-shared-01",
                    material_type="font",
                    scope_lock=False,
                    shared_resource_policy="allowed"
                )
            ]
        )
        self.dna_registry.register_dna(dna_case3)
        self.assertIsNotNone(self.dna_registry.get_dna("dna-case3"))

        # Case 4: Original shared + incoming claims non-shared -> reject
        dna_case4 = DesignDNA(
            id="dna-case4",
            display_name="Case 4 DNA",
            materials=[
                MaterialReference(
                    id="mat-shared-01",
                    material_type="font",
                    scope_lock=True,
                    shared_resource_policy="disallowed"
                )
            ]
        )
        with self.assertRaises(ValueError):
            self.dna_registry.register_dna(dna_case4)

    def test_material_policy_protected_from_external_mutation(self):
        """Tests that post-registration mutation of a caller-owned MaterialReference does not alter canonical registry policy."""
        mat_mutable = MaterialReference(
            id="mat-mutable-01",
            material_type="texture",
            scope_lock=True,
            shared_resource_policy="disallowed"
        )
        dna_owner = DesignDNA(
            id="dna-mutable-owner",
            display_name="Mutable Owner DNA",
            materials=[mat_mutable]
        )
        self.dna_registry.register_dna(dna_owner)

        # Mutate the caller-owned MaterialReference object externally afterward
        mat_mutable.scope_lock = False
        mat_mutable.shared_resource_policy = "allowed"

        # Attempt reuse from another DNA claiming shared usage
        dna_reuser = DesignDNA(
            id="dna-mutable-reuser",
            display_name="Reuser DNA",
            materials=[
                MaterialReference(
                    id="mat-mutable-01",
                    material_type="texture",
                    scope_lock=False,
                    shared_resource_policy="allowed"
                )
            ]
        )
        # Registry must still enforce original scope-locked policy and reject reuse
        with self.assertRaises(ValueError):
            self.dna_registry.register_dna(dna_reuser)

    def test_dna_to_theme_mapping_and_theme_engine_compatibility(self):
        """Tests dna_to_theme mapper adapter and verifies mapped Theme compatibility with ThemeRegistry."""
        dna = DesignDNA(
            id="test-editorial-dna",
            display_name="Test Editorial DNA",
            category="generic",
            description="Generic test editorial DNA instance.",
            reference_identity="reference-editorial-01",
            provenance={
                "author": "MultiMind Design Team",
                "license": "Internal Test",
                "source": "Synthetic Fixture",
                "attribution": "MultiMind Core",
            },
            colors={
                "primary": "#0F52BA",
                "surface": "#121824",
                "accent": "#7B1FA2"
            },
            typography={
                "font_family_base": "Georgia, serif",
                "roles": {
                    "heading": {"size": "1.8rem", "weight": "700", "line_height": "1.25"}
                }
            },
            spacing={"md": "1.1rem"},
            radius={"md": "0.25rem"}
        )

        # Pure adapter translation
        theme = dna_to_theme(dna)
        self.assertEqual(theme.id, dna.id)
        self.assertEqual(theme.display_name, dna.display_name)
        self.assertEqual(theme.category, dna.category)
        self.assertEqual(theme.colors["primary"], "#0F52BA")
        self.assertEqual(theme.metadata.author, "MultiMind Design Team")
        self.assertEqual(theme.metadata.license, "Internal Test")
        self.assertEqual(theme.metadata.reference, "reference-editorial-01")

        # Register converted Theme into an isolated ThemeRegistry instance
        self.theme_registry.register_theme(theme)
        resolved_theme, token_groups = self.theme_registry.resolve_theme("test-editorial-dna")

        self.assertEqual(resolved_theme.id, "test-editorial-dna")
        self.assertEqual(token_groups["colors"]["primary"], "#0F52BA")
        self.assertEqual(token_groups["colors"]["surface"], "#121824")
        self.assertEqual(token_groups["typography"]["font_family_base"], "Georgia, serif")
        self.assertEqual(token_groups["spacing"]["md"], "1.1rem")
        self.assertEqual(token_groups["radius"]["md"], "0.25rem")

        # Unmodified base tokens verification
        self.assertEqual(tokens.COLORS["primary"], "#3B82F6")
        self.assertEqual(tokens.SPACING["md"], "1rem")

    def test_layout_lock_and_no_arbitrary_css(self):
        """Verifies architectural layout lock and absence of arbitrary CSS escape hatches on DesignDNA."""
        dna = DesignDNA(
            id="test-layout-lock-dna",
            display_name="Layout Lock Verification DNA"
        )
        # Ensure DesignDNA dataclass fields do not contain layout engine or custom CSS attributes
        field_names = set(dna.__dataclass_fields__.keys())
        self.assertNotIn("sidebar_position", field_names)
        self.assertNotIn("layout_mode", field_names)
        self.assertNotIn("custom_css", field_names)
        self.assertNotIn("css_blob", field_names)

    def test_s6_2_proof_dna_definitions_and_bootstrap(self):
        """Tests registration, mapping, idempotence, and differentiation of S6.2 real Design DNA proofs."""
        from ui.dna.bootstrap import ensure_proof_dna_and_themes_registered
        from ui.dna import get_registry as get_dna_registry
        from ui.themes import list_themes, get_theme, generate_theme_css

        # Run bootstrap
        ensure_proof_dna_and_themes_registered()

        dna_reg = get_dna_registry()
        registered_theme_map = {t.id: t for t in list_themes()}

        proof_ids = ["japan-print-ink", "chainsaw-man-inspired", "mushishi-inspired"]

        for pid in proof_ids:
            # 1. Registered in DNARegistry
            dna = dna_reg.get_dna(pid)
            self.assertIsNotNone(dna, f"DesignDNA '{pid}' not found in DNARegistry.")
            self.assertIn(dna.category, ("cultural", "anime"))
            self.assertEqual(dna.materials, [], f"DesignDNA '{pid}' must be asset-free.")

            # 2. Registered in ThemeRegistry (verified using public list_themes list)
            self.assertIn(pid, registered_theme_map, f"Theme '{pid}' not found in public list_themes().")
            theme = get_theme(pid)
            self.assertEqual(theme.id, pid)

            # 3. CSS generation works
            css = generate_theme_css(pid)
            self.assertTrue(len(css) > 500)
            self.assertIn("--mm-font-base:", css)
            self.assertIn("--mm-color-primary:", css)

        # 4. Semantic Differentiation Verification
        dna_a = dna_reg.get_dna("japan-print-ink")
        dna_b = dna_reg.get_dna("chainsaw-man-inspired")
        dna_c = dna_reg.get_dna("mushishi-inspired")

        # Backgrounds differ
        self.assertNotEqual(dna_a.colors["background"], dna_b.colors["background"])
        self.assertNotEqual(dna_b.colors["background"], dna_c.colors["background"])
        self.assertNotEqual(dna_a.colors["background"], dna_c.colors["background"])

        # Radii differ (0px vs 2px vs 8px)
        self.assertEqual(dna_b.radius["md"], "0px")
        self.assertEqual(dna_a.radius["md"], "2px")
        self.assertEqual(dna_c.radius["md"], "8px")

        # Typography hierarchy font families differ
        self.assertIn("Georgia", dna_a.typography["font_family_base"])
        self.assertIn("Impact", dna_b.typography["font_family_base"])

        # 5. Idempotence verification (repeated call produces no errors or duplicate crashes)
        ensure_proof_dna_and_themes_registered()

    def test_s6_2_unmapped_dna_field_mutation_conflict_detection(self):
        """Verifies that mutating a non-theme-mapped DNA field (e.g. visual_character) triggers conflict detection."""
        from ui.dna.bootstrap import ensure_proof_dna_and_themes_registered
        from ui.dna import get_registry as get_dna_registry

        ensure_proof_dna_and_themes_registered()

        dna_reg = get_dna_registry()
        registered_dna = dna_reg.get_dna("chainsaw-man-inspired")
        self.assertIsNotNone(registered_dna)

        # Mutate an unmapped DNA descriptive field on the registered instance
        original_val = registered_dna.visual_character
        registered_dna.visual_character = "MUTATED_UNMAPPED_FIELD_VALUE"

        try:
            with self.assertRaises(ValueError):
                ensure_proof_dna_and_themes_registered()
        finally:
            # Restore original value to prevent state contamination
            registered_dna.visual_character = original_val


if __name__ == "__main__":
    unittest.main()
