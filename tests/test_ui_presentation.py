"""
Unit and regression tests for Semantic Presentation Seam (ui/presentation module).
Proves snapshot construction, deterministic field mapping, collection immutability,
non-mutation, defensive numeric normalization, and malformed debate error behavior.
"""
import unittest
import copy
import json
from ui.presentation import (
    build_presentation_snapshot,
    PresentationSnapshot,
    SessionMetadataSnapshot,
    MemorySummarySnapshot,
    ChatMessageSnapshot,
    DebateDetailSnapshot,
    DebateResponseSnapshot,
)


class MockMemory:
    """Mock memory object with get_stats method."""
    def __init__(self, context_tokens=500, short_term_chats=3, free_percent=85):
        self._stats = {
            "context_tokens": context_tokens,
            "short_term_chats": short_term_chats,
            "free_percent": free_percent,
        }

    def get_stats(self):
        return self._stats


class TestUIPresentation(unittest.TestCase):

    def setUp(self):
        self.sample_session = {
            "id": "sess-123",
            "name": "Project Refactor Debate",
            "mode": "coding",
            "created_at": "2025-02-18 10:00:00",
        }

        self.sample_debate_dict = {
            "gate_score": 9,
            "responses": [
                {"agent": "gemini", "text": "Gemini answer code", "status": "success"},
                {"agent": "deepseek", "text": "", "status": "error"},
            ],
            "total_tokens": 1500,
            "total_cost": 0.002,
        }

        self.sample_chats = [
            {
                "id": "chat-001",
                "prompt": "How to optimize Python loop?",
                "mode": "continue",
                "final_answer": "Use list comprehensions or built-in functions.",
                "debate_data": json.dumps(self.sample_debate_dict),
                "tokens_used": 1500,
                "cost": 0.002,
            },
            {
                "id": "chat-002",
                "prompt": "Explain GIL in detail.",
                "mode": "standalone",
                "final_answer": "GIL stands for Global Interpreter Lock.",
                "debate_data": "",
                "tokens_used": 800,
                "cost": 0.001,
            },
        ]

        self.sample_memory = MockMemory(context_tokens=1200, short_term_chats=2, free_percent=75)

    def test_full_presentation_snapshot_construction(self):
        """Test snapshot creation with valid session, chats, and memory data."""
        snapshot = build_presentation_snapshot(
            self.sample_session, self.sample_chats, self.sample_memory
        )

        self.assertIsInstance(snapshot, PresentationSnapshot)

        # Session Metadata
        self.assertEqual(snapshot.session.id, "sess-123")
        self.assertEqual(snapshot.session.name, "Project Refactor Debate")
        self.assertEqual(snapshot.session.mode, "coding")
        self.assertEqual(snapshot.session.created_at, "2025-02-18 10:00:00")

        # Memory Summary
        self.assertIsNotNone(snapshot.memory)
        self.assertEqual(snapshot.memory.context_tokens, 1200)
        self.assertEqual(snapshot.memory.short_term_chats, 2)
        self.assertEqual(snapshot.memory.free_percent, 75)

        # Chat Feed
        self.assertEqual(len(snapshot.chats), 2)
        self.assertIsInstance(snapshot.chats, tuple)

        # Chat 1 (with debate data)
        c1 = snapshot.chats[0]
        self.assertEqual(c1.id, "chat-001")
        self.assertEqual(c1.prompt, "How to optimize Python loop?")
        self.assertEqual(c1.mode, "continue")
        self.assertEqual(c1.tokens_used, 1500)
        self.assertEqual(c1.cost, 0.002)
        self.assertTrue(c1.has_debate_data)

        # Debate Details in Chat 1
        d1 = c1.debate_detail
        self.assertIsNotNone(d1)
        self.assertEqual(d1.gate_score, 9)
        self.assertFalse(d1.has_error)
        self.assertEqual(len(d1.responses), 2)
        self.assertIsInstance(d1.responses, tuple)

        r1 = d1.responses[0]
        self.assertEqual(r1.round_index, 1)
        self.assertEqual(r1.agent, "gemini")
        self.assertEqual(r1.text, "Gemini answer code")
        self.assertEqual(r1.status, "success")

        r2 = d1.responses[1]
        self.assertEqual(r2.round_index, 2)
        self.assertEqual(r2.agent, "deepseek")
        self.assertEqual(r2.text, "")
        self.assertEqual(r2.status, "error")

        # Chat 2 (standalone without debate data)
        c2 = snapshot.chats[1]
        self.assertEqual(c2.id, "chat-002")
        self.assertEqual(c2.mode, "standalone")
        self.assertFalse(c2.has_debate_data)
        self.assertIsNone(c2.debate_detail)

    def test_non_mutation_of_source_data(self):
        """Test that snapshot building does not alter source application state dicts/objects."""
        session_copy = copy.deepcopy(self.sample_session)
        chats_copy = copy.deepcopy(self.sample_chats)

        build_presentation_snapshot(self.sample_session, self.sample_chats, self.sample_memory)

        self.assertEqual(self.sample_session, session_copy)
        self.assertEqual(self.sample_chats, chats_copy)

    def test_collection_and_snapshot_immutability(self):
        """Test that snapshot objects and internal tuple collections are immutable."""
        snapshot = build_presentation_snapshot(self.sample_session, self.sample_chats, self.sample_memory)

        # Root snapshot immutability
        with self.assertRaises(AttributeError):
            snapshot.session = None  # type: ignore

        # Tuple collections immutability
        with self.assertRaises(AttributeError):
            snapshot.chats.append(None)  # type: ignore

        with self.assertRaises(AttributeError):
            snapshot.chats[0].debate_detail.responses.append(None)  # type: ignore

    def test_defensive_numeric_normalization(self):
        """Test that numeric fields gracefully degrade on malformed string/None/invalid values."""
        malformed_chats = [
            {
                "id": "c-num-1",
                "prompt": "Test num",
                "mode": "continue",
                "final_answer": "Ans",
                "tokens_used": "invalid_int",
                "cost": None,
            }
        ]

        class MalformedMemory:
            def get_stats(self):
                return {
                    "context_tokens": "500_bad",
                    "short_term_chats": None,
                    "free_percent": "90%",
                }

        snapshot = build_presentation_snapshot(self.sample_session, malformed_chats, MalformedMemory())

        self.assertEqual(snapshot.chats[0].tokens_used, 0)
        self.assertEqual(snapshot.chats[0].cost, 0.0)

        self.assertEqual(snapshot.memory.context_tokens, 0)
        self.assertEqual(snapshot.memory.short_term_chats, 0)
        self.assertEqual(snapshot.memory.free_percent, 0)

    def test_malformed_debate_data_preserves_error_flag(self):
        """Test that truthy but corrupt debate_data sets has_error=True on DebateDetailSnapshot."""
        corrupt_chats = [
            {
                "id": "c-bad-json",
                "prompt": "Test bad json",
                "mode": "continue",
                "final_answer": "Result",
                "debate_data": "{invalid json string",
            }
        ]

        snapshot = build_presentation_snapshot(self.sample_session, corrupt_chats, None)

        chat = snapshot.chats[0]
        self.assertTrue(chat.has_debate_data)
        self.assertIsNotNone(chat.debate_detail)
        self.assertTrue(chat.debate_detail.has_error)


if __name__ == "__main__":
    unittest.main()
