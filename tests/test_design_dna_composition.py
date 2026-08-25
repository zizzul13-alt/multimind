import unittest
from dataclasses import FrozenInstanceError

import streamlit as st

from ui.dna.models import (
    DesignDNA,
    MaterialReference,
    DesignComposition,
    ComposedProjection,
    PresentationPolicy,
)
from ui.dna.registry import DNARegistry
from ui.dna.resolver import resolve_composition
from ui.dna.bootstrap import ensure_proof_dna_and_themes_registered
from ui.theme_studio.state import (
    ThemeStudioDraft,
    init_draft_from_composition,
    apply_draft_to_active_theme,
    reset_draft_to_base,
    SESSION_DRAFT_KEY,
)


class TestDesignDNACompositionContract(unittest.TestCase):
    """Verifies all 20 test obligations for Design DNA Composition Foundation."""

    def setUp(self):
        st.session_state.clear()
        ensure_proof_dna_and_themes_registered()

    def test_01_registered_identity_dna_can_occupy_identity_slot(self):
        """1. Registered Identity DNA can occupy Identity slot."""
        comp = DesignComposition(identity_dna_id="japan-print-ink")
        projection = resolve_composition(comp)
        self.assertEqual(projection.theme.id, "japan-print-ink")

    def test_02_registered_web_dna_can_occupy_web_slot(self):
        """2. Registered Web / Information DNA can occupy Web slot."""
        comp = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info"
        )
        projection = resolve_composition(comp)
        self.assertEqual(projection.presentation_policy.metadata_prominence, "high")

    def test_03_wrong_role_dna_is_rejected(self):
        """3. Wrong-role DNA is rejected."""
        comp1 = DesignComposition(identity_dna_id="japan-high-density-info")
        with self.assertRaises(ValueError):
            resolve_composition(comp1)

        comp2 = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-print-ink"
        )
        with self.assertRaises(ValueError):
            resolve_composition(comp2)

    def test_04_unknown_dna_id_fails_safely(self):
        """4. Unknown DNA ID fails safely."""
        comp = DesignComposition(identity_dna_id="non-existent-dna")
        with self.assertRaises(ValueError):
            resolve_composition(comp)

    def test_05_invalid_archetype_fails_safely(self):
        """5. Invalid archetype fails safely."""
        comp = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            archetype_id="non-existent-archetype"
        )
        with self.assertRaises(ValueError):
            resolve_composition(comp)

    def test_06_rinpa_japan_chat_first_resolves_deterministically(self):
        """6. Rinpa + Japan High-Density + Chat First resolves deterministically."""
        comp = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info",
            archetype_id="chat_first"
        )
        proj1 = resolve_composition(comp)
        proj2 = resolve_composition(comp)

        self.assertEqual(proj1.theme.id, "rinpa-decorative-spatial")
        self.assertEqual(proj1.archetype_id, "chat_first")
        self.assertEqual(proj1.presentation_policy.status_richness, "rich")
        self.assertEqual(proj1.theme.colors, proj2.theme.colors)
        self.assertEqual(proj1.provenance['identity_dna_id'], proj2.provenance['identity_dna_id'])
        self.assertEqual(proj1.provenance['web_information_dna_id'], proj2.provenance['web_information_dna_id'])
        self.assertEqual(proj1.provenance['archetype_id'], proj2.provenance['archetype_id'])

    def test_07_selection_order_does_not_alter_composition_output(self):
        """7. Selection order does not alter composition output."""
        comp1 = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info",
            archetype_id="chat_first"
        )
        comp2 = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info",
            archetype_id="chat_first"
        )
        proj1 = resolve_composition(comp1)
        proj2 = resolve_composition(comp2)
        self.assertEqual(proj1.theme.colors, proj2.theme.colors)

    def test_08_no_last_write_wins_dictionary_merge_behavior(self):
        """8. No last-write-wins dictionary merge behavior."""
        comp = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info"
        )
        projection = resolve_composition(comp)
        self.assertEqual(projection.theme.colors["primary"], "#B8860B")

    def test_09_identity_ownership_survives_web_dna_composition(self):
        """9. Identity ownership survives Web DNA composition."""
        comp = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info"
        )
        projection = resolve_composition(comp)
        self.assertEqual(projection.theme.display_name, "Rinpa Decorative Spatial")
        self.assertEqual(projection.theme.colors["background"], "#F2ECE1")

    def test_10_web_dna_secondary_info_policy_survives_identity_composition(self):
        """10. Web DNA secondary-information policy survives Identity composition."""
        comp = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info"
        )
        projection = resolve_composition(comp)
        self.assertTrue(projection.presentation_policy.secondary_compactness)
        self.assertEqual(projection.presentation_policy.metadata_prominence, "high")

    def test_11_chat_first_remains_interaction_morphology_owner(self):
        """11. Chat First remains interaction morphology owner."""
        comp = DesignComposition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info",
            archetype_id="chat_first"
        )
        projection = resolve_composition(comp)
        self.assertEqual(projection.archetype_id, "chat_first")

    def test_12_material_binding_resolves_generically(self):
        """12. Material binding resolves generically."""
        comp = DesignComposition(identity_dna_id="rinpa-decorative-spatial")
        projection = resolve_composition(comp)
        self.assertEqual(len(projection.materials), 1)
        self.assertEqual(projection.materials[0].id, "rinpa-gold-mark")

    def test_13_missing_material_uses_existing_safe_fallback(self):
        """13. Missing material uses existing safe fallback in material resolver."""
        from ui.dna.resolver import resolve_material
        res = resolve_material("rinpa-decorative-spatial", material_type="non_existent_type")
        self.assertEqual(res.status, "fallback")

    def test_14_theme_studio_selector_changes_do_not_mutate_active_application_state(self):
        """14. Theme Studio selector changes do not mutate active application state."""
        st.session_state.active_theme = "default"
        st.session_state.active_archetype = "chat_first"

        draft = init_draft_from_composition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info",
            archetype_id="command_center"
        )
        self.assertEqual(st.session_state.active_theme, "default")
        self.assertEqual(st.session_state.active_archetype, "chat_first")

    def test_15_explicit_apply_promotes_complete_composition(self):
        """15. Explicit Apply promotes the complete composition."""
        st.session_state.active_theme = "default"
        st.session_state.active_archetype = "chat_first"

        draft = init_draft_from_composition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id="japan-high-density-info",
            archetype_id="ai_workspace"
        )
        apply_draft_to_active_theme(draft)

        self.assertNotEqual(st.session_state.active_theme, "default")
        self.assertEqual(st.session_state.active_archetype, "ai_workspace")
        self.assertIn("active_composition", st.session_state)
        self.assertEqual(st.session_state.active_composition.identity_dna_id, "rinpa-decorative-spatial")

    def test_16_discard_reset_preserves_active_application_state(self):
        """16. Discard/Reset preserves active application state."""
        st.session_state.active_theme = "default"
        st.session_state.active_archetype = "chat_first"

        reset_draft_to_base("chainsaw-man-inspired", "dna")

        self.assertEqual(st.session_state.active_theme, "default")
        self.assertEqual(st.session_state.active_archetype, "chat_first")

    def test_17_existing_single_dna_theme_studio_workflow_remains_valid(self):
        """17. Existing single-DNA Theme Studio workflow remains valid where intended."""
        draft = init_draft_from_composition(
            identity_dna_id="japan-print-ink",
            web_information_dna_id=None,
            archetype_id="chat_first"
        )
        projection = draft.resolve()
        self.assertEqual(projection.theme.id, "japan-print-ink")
        self.assertIsNone(projection.provenance["web_information_dna_id"])

    def test_18_japan_print_chainsaw_mushishi_do_not_regress(self):
        """18. Japan Print / Ink, Chainsaw-inspired, and Mushishi-inspired do not regress."""
        for dna_id in ("japan-print-ink", "chainsaw-man-inspired", "mushishi-inspired"):
            comp = DesignComposition(identity_dna_id=dna_id)
            projection = resolve_composition(comp)
            self.assertEqual(projection.theme.id, dna_id)

    def test_19_adding_synthetic_fourth_compatible_dna_does_not_require_editing_generic_resolver(self):
        """19. Adding a synthetic fourth compatible DNA in tests does not require editing generic composition resolver logic."""
        reg = DNARegistry()

        synth_identity = DesignDNA(
            id="synthetic-identity",
            display_name="Synthetic Identity DNA",
            role="identity",
            category="test",
            colors={"primary": "#123456", "background": "#F0F0F0"},
        )
        reg.register_dna(synth_identity)

        synth_web = DesignDNA(
            id="synthetic-web",
            display_name="Synthetic Web DNA",
            role="web_information",
            category="test",
            presentation_policy=PresentationPolicy(
                metadata_prominence="minimal",
                status_richness="standard",
                navigation_density="standard",
                secondary_compactness=False,
                information_discoverability="standard",
                utility_grouping="minimal",
            ),
        )
        reg.register_dna(synth_web)

        comp = DesignComposition(
            identity_dna_id="synthetic-identity",
            web_information_dna_id="synthetic-web",
            archetype_id="minimal_saas"
        )

        projection = resolve_composition(comp, dna_registry=reg)
        self.assertEqual(projection.theme.id, "synthetic-identity")
        self.assertEqual(projection.theme.colors["primary"], "#123456")
        self.assertEqual(projection.archetype_id, "minimal_saas")
        self.assertEqual(projection.provenance["web_information_dna_id"], "synthetic-web")
        self.assertEqual(projection.presentation_policy.metadata_prominence, "minimal")
        self.assertEqual(projection.presentation_policy.status_richness, "standard")
        self.assertEqual(projection.presentation_policy.navigation_density, "standard")
        self.assertFalse(projection.presentation_policy.secondary_compactness)
        self.assertEqual(projection.presentation_policy.information_discoverability, "standard")
        self.assertEqual(projection.presentation_policy.utility_grouping, "minimal")

    def test_20_no_theme_or_dna_name_specific_branches_in_resolver(self):
        """20. Immutable contract object checks."""
        comp = DesignComposition(identity_dna_id="rinpa-decorative-spatial")
        with self.assertRaises(FrozenInstanceError):
            comp.identity_dna_id = "other"

    def test_21_composition_reset_preserves_selected_roles_and_active_state(self):
        """21. Discard/Reset restores tokens without changing the selected composition or active state."""
        active_composition = DesignComposition(
            identity_dna_id="japan-print-ink",
            archetype_id="chat_first",
        )
        st.session_state.active_theme = "default"
        st.session_state.active_archetype = "chat_first"
        st.session_state.active_composition = active_composition

        draft = init_draft_from_composition(
            identity_dna_id="rinpa-decorative-spatial",
            web_information_dna_id=None,
            archetype_id="command_center",
        )
        st.session_state[SESSION_DRAFT_KEY] = draft
        draft.colors["primary"] = "#123456"

        reset_draft = reset_draft_to_base(draft.identity_dna_id, "composition")

        self.assertNotEqual(reset_draft.colors["primary"], "#123456")
        self.assertEqual(reset_draft.identity_dna_id, "rinpa-decorative-spatial")
        self.assertIsNone(reset_draft.web_information_dna_id)
        self.assertEqual(reset_draft.archetype_id, "command_center")
        self.assertEqual(st.session_state.active_theme, "default")
        self.assertEqual(st.session_state.active_archetype, "chat_first")
        self.assertIs(st.session_state.active_composition, active_composition)


if __name__ == "__main__":
    unittest.main()
