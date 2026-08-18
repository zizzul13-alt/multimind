"""
Unit tests for Archetype Registry & Resolver (ui/presentation/resolver.py).

Proves that:
1. Exactly 7 canonical archetypes are registered with unique IDs.
2. list_archetypes() returns exact 7 (id, display_name) pairs in canonical order.
3. resolve_archetype safely falls back to render_chat_first for invalid/unknown/None inputs.
4. get_archetype_definition returns valid metadata for all canonical archetypes.
5. render_archetype successfully invokes the resolved projection renderer.
"""
import unittest
from unittest.mock import patch, MagicMock

from ui.presentation import (
    list_archetypes,
    resolve_archetype,
    get_archetype_definition,
    render_archetype,
    CANONICAL_ARCHETYPE_IDS,
    FALLBACK_ARCHETYPE_ID,
    build_presentation_snapshot,
)
from ui.presentation.projections import render_chat_first


class TestUIArchetypeResolver(unittest.TestCase):

    def test_canonical_archetype_count_and_ids(self):
        """Test that exactly 7 canonical archetypes are registered with unique IDs."""
        self.assertEqual(len(CANONICAL_ARCHETYPE_IDS), 7)
        self.assertEqual(len(set(CANONICAL_ARCHETYPE_IDS)), 7)

        expected_ids = {
            "chat_first",
            "command_center",
            "ai_workspace",
            "ai_research_lab",
            "agent_canvas",
            "terminal_hacker",
            "minimal_saas",
        }
        self.assertEqual(set(CANONICAL_ARCHETYPE_IDS), expected_ids)

    def test_list_archetypes_order_and_format(self):
        """Test list_archetypes returns (id, name) tuples matching CANONICAL_ARCHETYPE_IDS order."""
        options = list_archetypes()
        self.assertEqual(len(options), 7)

        listed_ids = [opt[0] for opt in options]
        self.assertEqual(listed_ids, list(CANONICAL_ARCHETYPE_IDS))

        for arch_id, display_name in options:
            self.assertIsInstance(arch_id, str)
            self.assertIsInstance(display_name, str)
            self.assertTrue(len(display_name) > 0)

    def test_get_archetype_definition_valid(self):
        """Test retrieving metadata definition for each canonical archetype ID."""
        for arch_id in CANONICAL_ARCHETYPE_IDS:
            defn = get_archetype_definition(arch_id)
            self.assertEqual(defn.id, arch_id)
            self.assertIsNotNone(defn.display_name)
            self.assertIsNotNone(defn.description)
            self.assertIsNotNone(defn.primary_object)
            self.assertTrue(callable(defn.renderer))

    def test_resolver_fallback_behavior(self):
        """Test unknown, None, or empty archetype IDs safely resolve to render_chat_first."""
        invalid_inputs = ["unknown_archetype", "custom_invalid_id", "", None, 12345]

        for invalid_id in invalid_inputs:
            renderer = resolve_archetype(invalid_id)
            self.assertEqual(renderer, render_chat_first)

            defn = get_archetype_definition(invalid_id)
            self.assertEqual(defn.id, FALLBACK_ARCHETYPE_ID)

    @patch("ui.presentation.resolver.resolve_archetype")
    def test_render_archetype_delegation(self, mock_resolve):
        """Test render_archetype resolves and invokes the projection renderer with snapshot."""
        mock_renderer = MagicMock()
        mock_resolve.return_value = mock_renderer

        dummy_snapshot = build_presentation_snapshot(
            {"id": "s-1", "name": "Test", "mode": "coding", "created_at": "2025-01-01"},
            [],
            None
        )

        render_archetype("ai_workspace", dummy_snapshot)

        mock_resolve.assert_called_once_with("ai_workspace")
        mock_renderer.assert_called_once_with(dummy_snapshot)


if __name__ == "__main__":
    unittest.main()
