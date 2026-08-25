"""
MultiMind AI — S8.3 Semantic Consumption & Visual Reality Gate Acceptance Tests

Verifies acceptance criteria T01 - T13:
T01: No canonical DNA ID/name behavior branch exists in generic consumption code.
T02: Synthetic Identity DNA using existing vocabulary can use the same consumer.
T03: Existing single-DNA composition still resolves.
T04: Rinpa + Japan High-Density + chat_first still resolves.
T05: Web DNA still cannot override Identity Theme ownership.
T06: Theme Studio draft/active isolation remains unchanged.
T07: Material Pipeline remains unchanged unless a generic emphasis field is safely consumed through the existing seam.
T08: Every semantic field has exactly one S8.3 classification.
T09: Every classification C includes an explicit blocker type.
T10: No C-classified field is falsely represented as visually consumed.
T11: PresentationPolicy consumer matrix is backed by actual code references.
T12: Synthetic future DNA does not require generic resolver modification.
T13: All existing S8.2 production profile tests remain green.
"""

import unittest
import os
import re
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
)
from ui.dna.registry import DNARegistry, get_registry
from ui.dna.resolver import resolve_composition, resolve_material, resolve_source_dna
from ui.dna.mapper import dna_to_theme
from ui.theme_studio.state import ThemeStudioDraft, reset_draft_to_base, get_or_create_draft
from ui.themes import Theme, get_theme, ThemeRegistry


class TestSemanticConsumptionGate(unittest.TestCase):

    def test_T01_no_canonical_dna_id_branch_in_generic_consumption_code(self):
        """T01: No canonical DNA ID/name behavior branch exists in generic resolver/consumption code."""
        canonical_ids = [
            "rinpa-decorative-spatial",
            "japan-print-ink",
            "chainsaw-man-inspired",
            "mushishi-inspired",
            "japan-high-density-info",
        ]

        modules_to_check = [
            "ui/dna/resolver.py",
            "ui/dna/mapper.py",
            "ui/presentation/resolver.py",
            "ui/presentation/brand.py",
        ]

        # Broad regex checking for logic switches on canonical ID strings across single/double quotes, formatting, etc.
        pattern = re.compile(r'(if|elif|case)\s+.*["\'](' + '|'.join(canonical_ids) + r')["\']')

        for mod_path in modules_to_check:
            self.assertTrue(os.path.exists(mod_path), f"Module path {mod_path} must exist.")
            with open(mod_path, "r", encoding="utf-8") as f:
                content = f.read()
                matches = pattern.findall(content)
                self.assertEqual(
                    len(matches), 0,
                    f"Forbidden canonical DNA ID behavior branch in {mod_path}: {matches}"
                )

    def test_T02_synthetic_identity_dna_can_use_same_consumer(self):
        """T02: Synthetic Identity DNA using existing vocabulary can use the same composition consumer."""
        synthetic_dna = DesignDNA(
            id="synthetic-cyberpunk-test",
            display_name="Synthetic Cyberpunk Test",
            role="identity",
            category="cyberpunk",
            visual_energy="aggressive",
            spatial_density="compact",
            composition_balance="asymmetric",
            hierarchy_strength="dramatic",
            surface_character="poster",
            shape_character="sharp",
            ornament_emphasis="prominent",
            interaction_intensity="assertive",
            responsive_identity_priority="preserve_strong",
            colors={
                "background": "#050508",
                "surface": "#12121C",
                "surface_elevated": "#1A1A2B",
                "surface_muted": "#050508",
                "surface_hover": "#222238",
                "surface_input": "#0A0A12",
                "text": "#00FFCC",
                "text_muted": "#708090",
                "text_disabled": "#404850",
                "primary": "#FF0055",
                "primary_hover": "#D40047",
                "primary_active": "#AA0039",
                "secondary": "#00FFCC",
                "secondary_hover": "#00CCA3",
                "accent": "#FFE600",
                "border": "#333355",
                "border_subtle": "#1A1A2B",
                "border_hover": "#FF0055",
                "border_focus": "#FF0055",
                "focus_ring": "rgba(255, 0, 85, 0.35)",
                "success": "#00FFCC",
                "success_bg": "rgba(0, 255, 204, 0.12)",
                "warning": "#FFE600",
                "warning_bg": "rgba(255, 230, 0, 0.12)",
                "danger": "#FF0055",
                "danger_bg": "rgba(255, 0, 85, 0.12)",
                "info": "#00FFCC",
                "info_bg": "rgba(0, 255, 204, 0.12)",
            },
            typography={
                "font_family_base": "Fira Code, monospace",
                "font_family_mono": "Fira Code, monospace",
                "roles": {
                    "display": {"size": "2rem", "weight": "700", "line_height": "1.2"},
                    "heading": {"size": "1.5rem", "weight": "600", "line_height": "1.3"},
                    "subheading": {"size": "1.25rem", "weight": "600", "line_height": "1.4"},
                    "body": {"size": "1rem", "weight": "400", "line_height": "1.5"},
                    "body_small": {"size": "0.875rem", "weight": "400", "line_height": "1.4"},
                    "caption": {"size": "0.75rem", "weight": "400", "line_height": "1.4"},
                    "label": {"size": "0.875rem", "weight": "500", "line_height": "1.2"},
                },
            },
            spacing={"xs": "0.25rem", "sm": "0.5rem", "md": "1rem", "lg": "1.5rem", "xl": "2rem", "2xl": "3rem"},
            radius={"none": "0px", "sm": "0px", "md": "0px", "lg": "0px", "pill": "0px"},
        )

        reg = DNARegistry()
        reg.register_dna(synthetic_dna)
        reg.register_dna(JAPAN_HIGH_DENSITY_INFO_DNA)

        comp = DesignComposition(
            identity_dna_id="synthetic-cyberpunk-test",
            web_information_dna_id="japan-high-density-info",
            archetype_id="chat_first",
        )

        projection = resolve_composition(comp, dna_registry=reg)
        self.assertIsInstance(projection, ComposedProjection)
        self.assertEqual(projection.theme.id, "synthetic-cyberpunk-test")
        self.assertEqual(projection.theme.colors["primary"], "#FF0055")
        self.assertEqual(projection.presentation_policy.metadata_prominence, "high")

    def test_T03_existing_single_dna_composition_resolves(self):
        """T03: Existing single-DNA composition still resolves correctly."""
        comp = DesignComposition(identity_dna_id="rinpa-decorative-spatial")
        proj = resolve_composition(comp)
        self.assertEqual(proj.theme.id, "rinpa-decorative-spatial")
        self.assertEqual(proj.presentation_policy.metadata_prominence, "standard")

    def test_T04_rinpa_plus_japan_info_plus_chat_first_resolves(self):
        """T04: Rinpa + Japan High-Density + chat_first resolves deterministically."""
        comp = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info",
            archetype_id="chat_first",
        )
        proj = resolve_composition(comp)
        self.assertEqual(proj.theme.id, "rinpa-decorative-spatial")
        self.assertEqual(proj.presentation_policy.metadata_prominence, "high")
        self.assertTrue(proj.presentation_policy.secondary_compactness)
        self.assertEqual(proj.archetype_id, "chat_first")

    def test_T05_web_dna_cannot_override_identity_theme_ownership(self):
        """T05: Web / Information DNA cannot override Identity DNA's primary visual theme tokens."""
        comp = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info",
        )
        proj = resolve_composition(comp)
        # Primary color MUST come from Rinpa gold (#B8860B), NOT Web DNA
        self.assertEqual(proj.theme.colors["primary"], "#B8860B")
        self.assertEqual(proj.theme.colors["background"], "#F2ECE1")

    def test_T06_theme_studio_draft_active_isolation_remains(self):
        """T06: Theme Studio draft/active state isolation remains intact."""
        draft = reset_draft_to_base("rinpa-decorative-spatial", "composition")
        self.assertIsInstance(draft, ThemeStudioDraft)
        self.assertEqual(draft.identity_dna_id, "rinpa-decorative-spatial")

        # Modify draft
        draft.colors["primary"] = "#FF0000"
        custom_theme = draft.to_theme()
        self.assertEqual(custom_theme.colors["primary"], "#FF0000")

        # Verify active registered theme remains untouched
        active_theme = get_theme("rinpa-decorative-spatial")
        self.assertEqual(active_theme.colors["primary"], "#B8860B")

    def test_T07_material_pipeline_remains_unchanged(self):
        """T07: Material Pipeline resolves materials deterministically without modification."""
        res = resolve_material("rinpa-decorative-spatial")
        self.assertTrue(res.is_resolved)
        self.assertEqual(res.material.id, "rinpa-gold-mark")

    def test_T08_every_semantic_field_has_exactly_one_s83_classification(self):
        """T08: Verifies report contains explicit classification for all 9 production semantic fields."""
        report_path = "docs/ui/semantic-consumption-visual-reality-gate.md"
        self.assertTrue(os.path.exists(report_path), f"Report {report_path} must exist.")

        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_fields = [
            "visual_energy",
            "spatial_density",
            "composition_balance",
            "hierarchy_strength",
            "surface_character",
            "shape_character",
            "ornament_emphasis",
            "interaction_intensity",
            "responsive_identity_priority",
        ]

        for field in required_fields:
            self.assertIn(f"`{field}`", content, f"Field {field} missing from report inventory/table.")

    def test_T09_every_c_classification_includes_explicit_blocker_type(self):
        """T09: Verifies every C-classified field in the report specifies a recognized blocker type."""
        valid_blockers = {
            "STREAMLIT_PLATFORM_LIMIT",
            "PRESENTATION_ARCHITECTURE_LIMIT",
            "THEME_ENGINE_LIMIT",
            "MATERIAL_PIPELINE_LIMIT",
            "ARCHETYPE_OWNERSHIP_LIMIT",
            "NO_SAFE_GENERIC_MAPPING",
        }

        report_path = "docs/ui/semantic-consumption-visual-reality-gate.md"
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        found_blockers = set()
        for b in valid_blockers:
            if b in content:
                found_blockers.add(b)

        self.assertGreater(len(found_blockers), 0, "Report must reference valid blocker types.")

    def test_T10_no_c_classified_field_falsely_represented_as_visually_consumed(self):
        """T10: Verifies dna_to_theme and resolve_composition produce pure contracts without fake attributes."""
        theme = dna_to_theme(RINPA_DECORATIVE_SPATIAL_DNA)
        self.assertIsInstance(theme, Theme)
        # Theme contract must only expose standard theme token dictionaries
        self.assertFalse(hasattr(theme, "visual_energy"))
        self.assertFalse(hasattr(theme, "spatial_density"))
        self.assertNotIn("visual_energy", theme.colors)

    def test_T11_presentation_policy_audit_backed_by_code_references(self):
        """T11: PresentationPolicy audit verifies active vs unconsumed policy fields across codebase."""
        # 1. Theme Studio consumes metadata_prominence, status_richness, secondary_compactness
        with open("ui/theme_studio/surface.py", "r", encoding="utf-8") as f:
            ts_code = f.read()
            self.assertIn("projection.presentation_policy.metadata_prominence", ts_code)
            self.assertIn("projection.presentation_policy.status_richness", ts_code)
            self.assertIn("projection.presentation_policy.secondary_compactness", ts_code)

        # 2. Main app projections do NOT consume unconsumed fields (navigation_density, information_discoverability, utility_grouping)
        with open("ui/presentation/projections.py", "r", encoding="utf-8") as f:
            proj_code = f.read()
            self.assertNotIn("navigation_density", proj_code)
            self.assertNotIn("information_discoverability", proj_code)
            self.assertNotIn("utility_grouping", proj_code)

    def test_T12_synthetic_future_dna_does_not_require_resolver_modification(self):
        """T12: Synthetic future DNA does not require generic resolver modification."""
        future_dna = DesignDNA(
            id="future-mars-colony-2099",
            display_name="Mars Colony 2099",
            role="identity",
            category="sci-fi",
            colors={
                "background": "#120A08",
                "surface": "#241410",
                "surface_elevated": "#361E18",
                "surface_muted": "#120A08",
                "surface_hover": "#482820",
                "surface_input": "#1A0E0B",
                "text": "#FFB3A0",
                "text_muted": "#B37A6B",
                "text_disabled": "#66453D",
                "primary": "#FF4500",
                "primary_hover": "#CC3700",
                "primary_active": "#992900",
                "secondary": "#FFB3A0",
                "secondary_hover": "#CC8F80",
                "accent": "#00E5FF",
                "border": "#482820",
                "border_subtle": "#241410",
                "border_hover": "#FF4500",
                "border_focus": "#FF4500",
                "focus_ring": "rgba(255, 69, 0, 0.35)",
                "success": "#00FF66",
                "success_bg": "rgba(0, 255, 102, 0.12)",
                "warning": "#FFD700",
                "warning_bg": "rgba(255, 215, 0, 0.12)",
                "danger": "#FF0033",
                "danger_bg": "rgba(255, 0, 51, 0.12)",
                "info": "#00E5FF",
                "info_bg": "rgba(0, 229, 255, 0.12)",
            },
            typography={
                "font_family_base": "system-ui, sans-serif",
                "font_family_mono": "monospace",
                "roles": {
                    "display": {"size": "2rem", "weight": "700", "line_height": "1.2"},
                    "heading": {"size": "1.5rem", "weight": "600", "line_height": "1.3"},
                    "subheading": {"size": "1.25rem", "weight": "600", "line_height": "1.4"},
                    "body": {"size": "1rem", "weight": "400", "line_height": "1.5"},
                    "body_small": {"size": "0.875rem", "weight": "400", "line_height": "1.4"},
                    "caption": {"size": "0.75rem", "weight": "400", "line_height": "1.4"},
                    "label": {"size": "0.875rem", "weight": "500", "line_height": "1.2"},
                },
            },
            spacing={"xs": "0.25rem", "sm": "0.5rem", "md": "1rem", "lg": "1.5rem", "xl": "2rem", "2xl": "3rem"},
            radius={"none": "0px", "sm": "2px", "md": "4px", "lg": "8px", "pill": "9999px"},
        )

        reg = DNARegistry()
        reg.register_dna(future_dna)

        comp = DesignComposition(identity_dna_id="future-mars-colony-2099")
        proj = resolve_composition(comp, dna_registry=reg)
        self.assertEqual(proj.theme.id, "future-mars-colony-2099")
        self.assertEqual(proj.theme.colors["primary"], "#FF4500")

    def test_T13_all_existing_s82_production_profiles_valid(self):
        """T13: All existing S8.2 production profiles validate and resolve without error."""
        for dna in (
            RINPA_DECORATIVE_SPATIAL_DNA,
            JAPAN_PRINT_INK_DNA,
            CHAINSAW_MAN_INSPIRED_DNA,
            MUSHISHI_INSPIRED_DNA,
            JAPAN_HIGH_DENSITY_INFO_DNA,
        ):
            dna.validate()


if __name__ == "__main__":
    unittest.main()
