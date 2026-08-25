"""
MultiMind AI - S8.2 Production Design DNA Deepening Test Suite
Explicit unit tests for T01 through T27 covering Design DNA deepening contracts,
canonical profiles, invalid semantic rejection, composition resolution, machine readability,
Theme Studio integration, Material Pipeline integrity, and no-branch generic invariants.
"""
import unittest
import copy
import streamlit as st

from ui.dna.models import (
    DesignDNA,
    MaterialReference,
    PresentationPolicy,
    DesignComposition,
    ComposedProjection,
    VALID_VISUAL_ENERGY,
    VALID_SPATIAL_DENSITY,
    VALID_COMPOSITION_BALANCE,
    VALID_HIERARCHY_STRENGTH,
    VALID_SURFACE_CHARACTER,
    VALID_SHAPE_CHARACTER,
    VALID_ORNAMENT_EMPHASIS,
    VALID_INTERACTION_INTENSITY,
    VALID_RESPONSIVE_IDENTITY_PRIORITY,
)
from ui.dna.proofs import (
    RINPA_DECORATIVE_SPATIAL_DNA,
    JAPAN_PRINT_INK_DNA,
    CHAINSAW_MAN_INSPIRED_DNA,
    MUSHISHI_INSPIRED_DNA,
    JAPAN_HIGH_DENSITY_INFO_DNA,
    PROOFS,
)
from ui.dna.registry import DNARegistry, get_registry
from ui.dna.bootstrap import ensure_proof_dna_and_themes_registered
from ui.dna.mapper import dna_to_theme
from ui.dna.resolver import resolve_composition, resolve_material
from ui.theme_studio.state import (
    ThemeStudioDraft,
    init_draft_from_composition,
    apply_draft_to_active_theme,
    reset_draft_to_base,
    SESSION_DRAFT_KEY,
)


class TestProductionDesignDNADeepening(unittest.TestCase):
    """Execution Specification S8.2 Test Suite (T01 - T27)."""

    def setUp(self):
        st.session_state.clear()
        ensure_proof_dna_and_themes_registered()

    def test_T01_all_four_canonical_identity_dnas_validate(self):
        """T01: All four canonical Identity DNAs validate successfully."""
        for dna in (
            RINPA_DECORATIVE_SPATIAL_DNA,
            JAPAN_PRINT_INK_DNA,
            CHAINSAW_MAN_INSPIRED_DNA,
            MUSHISHI_INSPIRED_DNA,
        ):
            self.assertEqual(dna.role, "identity")
            dna.validate()

    def test_T02_japan_high_density_info_validates_with_role_web_information(self):
        """T02: japan-high-density-info validates with role web_information."""
        dna = JAPAN_HIGH_DENSITY_INFO_DNA
        self.assertEqual(dna.role, "web_information")
        self.assertIsInstance(dna.presentation_policy, PresentationPolicy)
        dna.validate()

    def test_T03_invalid_visual_energy_is_rejected(self):
        """T03: Invalid visual_energy is rejected by DesignDNA.validate()."""
        dna = DesignDNA(id="invalid-ve", display_name="Invalid VE", visual_energy="SUPER_HIGH_ENERGY")
        with self.assertRaises(ValueError):
            dna.validate()

    def test_T04_invalid_spatial_density_is_rejected(self):
        """T04: Invalid spatial_density is rejected by DesignDNA.validate()."""
        dna = DesignDNA(id="invalid-sd", display_name="Invalid SD", spatial_density="huge")
        with self.assertRaises(ValueError):
            dna.validate()

    def test_T05_invalid_composition_balance_is_rejected(self):
        """T05: Invalid composition_balance is rejected by DesignDNA.validate()."""
        dna = DesignDNA(id="invalid-cb", display_name="Invalid CB", composition_balance="tilted")
        with self.assertRaises(ValueError):
            dna.validate()

    def test_T06_invalid_hierarchy_strength_is_rejected(self):
        """T06: Invalid hierarchy_strength is rejected by DesignDNA.validate()."""
        dna = DesignDNA(id="invalid-hs", display_name="Invalid HS", hierarchy_strength="extreme")
        with self.assertRaises(ValueError):
            dna.validate()

    def test_T07_invalid_surface_character_is_rejected(self):
        """T07: Invalid surface_character is rejected by DesignDNA.validate()."""
        dna = DesignDNA(id="invalid-sc", display_name="Invalid SC", surface_character="glassmorphic")
        with self.assertRaises(ValueError):
            dna.validate()

    def test_T08_invalid_shape_character_is_rejected(self):
        """T08: Invalid shape_character is rejected by DesignDNA.validate()."""
        dna = DesignDNA(id="invalid-shc", display_name="Invalid SHC", shape_character="rounded_corners")
        with self.assertRaises(ValueError):
            dna.validate()

    def test_T09_invalid_ornament_emphasis_is_rejected(self):
        """T09: Invalid ornament_emphasis is rejected by DesignDNA.validate()."""
        dna = DesignDNA(id="invalid-oe", display_name="Invalid OE", ornament_emphasis="heavy")
        with self.assertRaises(ValueError):
            dna.validate()

    def test_T10_invalid_interaction_intensity_is_rejected(self):
        """T10: Invalid interaction_intensity is rejected by DesignDNA.validate()."""
        dna = DesignDNA(id="invalid-ii", display_name="Invalid II", interaction_intensity="super_fast")
        with self.assertRaises(ValueError):
            dna.validate()

    def test_T11_invalid_responsive_identity_priority_is_rejected(self):
        """T11: Invalid responsive_identity_priority is rejected by DesignDNA.validate()."""
        dna = DesignDNA(id="invalid-rip", display_name="Invalid RIP", responsive_identity_priority="breakpoint_mobile")
        with self.assertRaises(ValueError):
            dna.validate()

    def test_T12_dna_to_theme_remains_deterministic(self):
        """T12: dna_to_theme produces deterministic Theme instances without mutating source DNA."""
        dna = RINPA_DECORATIVE_SPATIAL_DNA
        t1 = dna_to_theme(dna)
        t2 = dna_to_theme(dna)

        self.assertEqual(t1.id, t2.id)
        self.assertEqual(t1.colors, t2.colors)
        self.assertEqual(t1.typography, t2.typography)
        self.assertEqual(t1.spacing, t2.spacing)
        self.assertEqual(t1.radius, t2.radius)
        # Source DNA remains unchanged
        self.assertEqual(dna.id, "rinpa-decorative-spatial")

    def test_T13_rinpa_production_semantic_profile_matches_section_6a(self):
        """T13: Rinpa production semantic profile matches Section 6A contract profile."""
        dna = RINPA_DECORATIVE_SPATIAL_DNA
        self.assertEqual(dna.visual_energy, "expressive")
        self.assertEqual(dna.spatial_density, "spacious")
        self.assertEqual(dna.composition_balance, "asymmetric")
        self.assertEqual(dna.hierarchy_strength, "strong")
        self.assertEqual(dna.surface_character, "layered")
        self.assertEqual(dna.shape_character, "organic")
        self.assertEqual(dna.ornament_emphasis, "selective")
        self.assertEqual(dna.interaction_intensity, "deliberate")
        self.assertEqual(dna.responsive_identity_priority, "preserve_strong")

    def test_T14_japan_print_ink_production_semantic_profile_matches_section_6b(self):
        """T14: Japan Print / Ink production semantic profile matches Section 6B contract profile."""
        dna = JAPAN_PRINT_INK_DNA
        self.assertEqual(dna.visual_energy, "balanced")
        self.assertEqual(dna.spatial_density, "balanced")
        self.assertEqual(dna.composition_balance, "regular")
        self.assertEqual(dna.hierarchy_strength, "strong")
        self.assertEqual(dna.surface_character, "paper")
        self.assertEqual(dna.shape_character, "restrained")
        self.assertEqual(dna.ornament_emphasis, "subtle")
        self.assertEqual(dna.interaction_intensity, "deliberate")
        self.assertEqual(dna.responsive_identity_priority, "preserve_core")

    def test_T15_chainsaw_inspired_production_semantic_profile_matches_section_6c(self):
        """T15: Chainsaw-inspired production semantic profile matches Section 6C contract profile."""
        dna = CHAINSAW_MAN_INSPIRED_DNA
        self.assertEqual(dna.visual_energy, "aggressive")
        self.assertEqual(dna.spatial_density, "dense")
        self.assertEqual(dna.composition_balance, "asymmetric")
        self.assertEqual(dna.hierarchy_strength, "dramatic")
        self.assertEqual(dna.surface_character, "poster")
        self.assertEqual(dna.shape_character, "sharp")
        self.assertEqual(dna.ornament_emphasis, "prominent")
        self.assertEqual(dna.interaction_intensity, "assertive")
        self.assertEqual(dna.responsive_identity_priority, "preserve_strong")

    def test_T16_mushishi_inspired_production_semantic_profile_matches_section_6d(self):
        """T16: Mushishi-inspired production semantic profile matches Section 6D contract profile."""
        dna = MUSHISHI_INSPIRED_DNA
        self.assertEqual(dna.visual_energy, "quiet")
        self.assertEqual(dna.spatial_density, "spacious")
        self.assertEqual(dna.composition_balance, "organic")
        self.assertEqual(dna.hierarchy_strength, "soft")
        self.assertEqual(dna.surface_character, "atmospheric")
        self.assertEqual(dna.shape_character, "organic")
        self.assertEqual(dna.ornament_emphasis, "subtle")
        self.assertEqual(dna.interaction_intensity, "gentle")
        self.assertEqual(dna.responsive_identity_priority, "preserve_core")

    def test_T17_four_canonical_identity_dna_semantic_profiles_are_machine_readably_distinct(self):
        """T17: The four canonical Identity DNA semantic profiles are machine-readably distinct beyond palette/font/radius/material."""
        dnas = [
            RINPA_DECORATIVE_SPATIAL_DNA,
            JAPAN_PRINT_INK_DNA,
            CHAINSAW_MAN_INSPIRED_DNA,
            MUSHISHI_INSPIRED_DNA,
        ]

        def get_profile_tuple(dna: DesignDNA):
            return (
                dna.visual_energy,
                dna.spatial_density,
                dna.composition_balance,
                dna.hierarchy_strength,
                dna.surface_character,
                dna.shape_character,
                dna.ornament_emphasis,
                dna.interaction_intensity,
                dna.responsive_identity_priority,
            )

        profiles = [get_profile_tuple(d) for d in dnas]
        # Unique count must equal 4
        self.assertEqual(len(set(profiles)), 4, "All 4 Identity DNAs must have unique machine-readable semantic profiles.")

    def test_T18_no_web_information_dna_can_overwrite_identity_theme_ownership(self):
        """T18: No Web/Information DNA can overwrite Identity Theme primary visual token ownership."""
        comp = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info",
        )
        projection = resolve_composition(comp)
        self.assertEqual(projection.theme.id, "rinpa-decorative-spatial")
        self.assertEqual(projection.theme.colors["primary"], "#B8860B")
        self.assertEqual(projection.theme.colors["background"], "#F2ECE1")

    def test_T19_rinpa_japan_high_density_chat_first_resolves(self):
        """T19: Rinpa + Japan High-Density + chat_first resolves successfully."""
        comp = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info",
            archetype_id="chat_first",
        )
        projection = resolve_composition(comp)
        self.assertEqual(projection.theme.id, "rinpa-decorative-spatial")
        self.assertEqual(projection.presentation_policy.metadata_prominence, "high")
        self.assertEqual(projection.archetype_id, "chat_first")

    def test_T20_theme_studio_exposes_all_canonical_identity_dnas(self):
        """T20: Theme Studio exposes all canonical Identity DNAs via list_dna()."""
        reg_dna = get_registry().list_dna()
        identity_ids = {d.id for d in reg_dna if d.role == "identity"}
        expected_ids = {
            "rinpa-decorative-spatial",
            "japan-print-ink",
            "chainsaw-man-inspired",
            "mushishi-inspired",
        }
        self.assertTrue(expected_ids.issubset(identity_ids))

    def test_T21_theme_studio_exposes_japan_high_density_as_web_information_dna(self):
        """T21: Theme Studio exposes Japan High-Density as Web/Information DNA."""
        reg_dna = get_registry().list_dna()
        web_dnas = [d for d in reg_dna if d.role == "web_information"]
        web_ids = {d.id for d in web_dnas}
        self.assertIn("japan-high-density-info", web_ids)

    def test_T22_apply_state_isolation_remains_valid(self):
        """T22: Apply state isolation remains valid when promoting compositions in Theme Studio."""
        draft = init_draft_from_composition(
            identity_dna_id="chainsaw-man-inspired",
            web_information_dna_id="japan-high-density-info",
            archetype_id="command_center",
        )
        applied_theme = apply_draft_to_active_theme(draft)
        self.assertTrue(st.session_state.active_theme.startswith("custom-chainsaw-man-inspired-"))
        self.assertEqual(st.session_state.active_archetype, "command_center")

    def test_T23_discard_reset_composition_preservation_remains_valid(self):
        """T23: Discard/Reset composition preservation remains valid."""
        draft = init_draft_from_composition(
            identity_dna_id="mushishi-inspired",
            web_information_dna_id="japan-high-density-info",
            archetype_id="ai_workspace",
        )
        st.session_state[SESSION_DRAFT_KEY] = draft
        draft.colors["primary"] = "#FF00FF"

        reset_draft = reset_draft_to_base(draft.identity_dna_id, "composition")
        self.assertEqual(reset_draft.identity_dna_id, "mushishi-inspired")
        self.assertEqual(reset_draft.web_information_dna_id, "japan-high-density-info")
        self.assertEqual(reset_draft.archetype_id, "ai_workspace")
        self.assertNotEqual(reset_draft.colors["primary"], "#FF00FF")

    def test_T24_all_canonical_material_references_validate_using_existing_material_pipeline(self):
        """T24: All canonical material references validate using existing Material Pipeline."""
        for dna in PROOFS:
            for mat in dna.materials:
                mat.validate()
                res = resolve_material(dna.id, material_type=mat.material_type)
                self.assertTrue(res.is_resolved, f"Material '{mat.id}' in DNA '{dna.id}' failed material resolution.")

    def test_T25_responsive_identity_semantics_contain_no_pixel_layout_definitions(self):
        """T25: Responsive identity semantics contain no pixel/layout definitions."""
        for dna in (
            RINPA_DECORATIVE_SPATIAL_DNA,
            JAPAN_PRINT_INK_DNA,
            CHAINSAW_MAN_INSPIRED_DNA,
            MUSHISHI_INSPIRED_DNA,
        ):
            val = dna.responsive_identity_priority
            self.assertIn(val, VALID_RESPONSIVE_IDENTITY_PRIORITY)
            self.assertNotIn("px", str(val))
            self.assertNotIn("width", str(val))
            self.assertNotIn("breakpoint", str(val))

    def test_T26_synthetic_future_identity_dna_resolves_without_dna_id_branch_in_resolver(self):
        """T26: Synthetic future Identity DNA resolves without adding a DNA-ID branch to generic resolver logic."""
        reg = DNARegistry()

        synth_dna = DesignDNA(
            id="future-neo-cyber-identity",
            display_name="Future Neo-Cyber Identity",
            role="identity",
            category="futuristic",
            visual_energy="expressive",
            spatial_density="compact",
            composition_balance="asymmetric",
            hierarchy_strength="dramatic",
            surface_character="layered",
            shape_character="sharp",
            ornament_emphasis="prominent",
            interaction_intensity="assertive",
            responsive_identity_priority="preserve_strong",
            colors={"primary": "#00FFCC", "background": "#05050A"},
        )
        reg.register_dna(synth_dna)

        comp = DesignComposition(identity_dna_id="future-neo-cyber-identity", archetype_id="terminal_hacker")
        projection = resolve_composition(comp, dna_registry=reg)

        self.assertEqual(projection.theme.id, "future-neo-cyber-identity")
        self.assertEqual(projection.theme.colors["primary"], "#00FFCC")
        self.assertEqual(projection.archetype_id, "terminal_hacker")

    def test_T27_existing_legacy_minimal_dna_compatibility_remains_valid(self):
        """T27: Existing legacy/minimal DNA compatibility remains valid (all 9 semantic fields optional)."""
        minimal_dna = DesignDNA(
            id="minimal-legacy-dna",
            display_name="Minimal Legacy DNA",
            role="identity",
        )
        # Must validate without needing any of the 9 semantic fields populated
        minimal_dna.validate()
        self.assertIsNone(minimal_dna.visual_energy)
        self.assertIsNone(minimal_dna.spatial_density)


if __name__ == "__main__":
    unittest.main()
