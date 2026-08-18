"""
Unit and regression tests for Archetype Projections (ui/presentation/projections.py).

Proves that:
1. The exact same PresentationSnapshot can be passed to both Chat-first and Command Center projections.
2. Projections execute pure UI rendering with ZERO database access or core state queries.
3. Chat-first preserves conversation-centered mental model and controls.
4. Command Center prioritizes operational state, gate scores, and comparable agent responses.
5. Both projections handle edge cases safely (no chats, no debate data, malformed debate JSON, missing memory).
6. Rendering projections does NOT mutate PresentationSnapshot instances or internal snapshots.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import copy

from ui.presentation import (
    build_presentation_snapshot,
    PresentationSnapshot,
    SessionMetadataSnapshot,
    MemorySummarySnapshot,
    ChatMessageSnapshot,
    DebateDetailSnapshot,
    DebateResponseSnapshot,
)
from ui.presentation.projections import render_chat_first, render_command_center


class MockMemory:
    """Mock memory object with get_stats method."""
    def __init__(self, context_tokens=1500, short_term_chats=4, free_percent=70):
        self._stats = {
            "context_tokens": context_tokens,
            "short_term_chats": short_term_chats,
            "free_percent": free_percent,
        }

    def get_stats(self):
        return self._stats


def create_mock_st():
    """Helper to create a fully configured Streamlit mock that supports columns unpacking."""
    mock_st = MagicMock()
    def columns_side_effect(spec):
        count = spec if isinstance(spec, int) else len(spec)
        return [MagicMock() for _ in range(count)]
    mock_st.columns.side_effect = columns_side_effect
    return mock_st


class TestUIArchetypeProjections(unittest.TestCase):

    def setUp(self):
        self.sample_session = {
            "id": "sess-arch-100",
            "name": "Archetype Architecture Session",
            "mode": "coding",
            "created_at": "2025-02-18 12:00:00",
        }

        self.sample_debate_dict = {
            "gate_score": 9,
            "responses": [
                {"agent": "gemini", "text": "def solve(): return True", "status": "success"},
                {"agent": "groq", "text": "def solve(): return 1", "status": "success"},
                {"agent": "deepseek", "text": "error occurred", "status": "error"},
            ],
            "total_tokens": 2100,
            "total_cost": 0.0035,
        }

        self.sample_chats = [
            {
                "id": "chat-arch-1",
                "prompt": "Write a python function to check prime.",
                "mode": "continue",
                "final_answer": "Here is the python function:\n```python\ndef is_prime(n):\n    return n > 1\n```",
                "debate_data": json.dumps(self.sample_debate_dict),
                "tokens_used": 2100,
                "cost": 0.0035,
            },
            {
                "id": "chat-arch-2",
                "prompt": "Explain prime numbers simply.",
                "mode": "standalone",
                "final_answer": "Prime numbers are numbers greater than 1 that have no positive divisors other than 1 and themselves.",
                "debate_data": "",
                "tokens_used": 450,
                "cost": 0.0005,
            },
        ]

        self.sample_memory = MockMemory(context_tokens=2550, short_term_chats=2, free_percent=68)
        self.snapshot = build_presentation_snapshot(
            self.sample_session, self.sample_chats, self.sample_memory
        )

    @patch("database.manager.DatabaseManager")
    def test_single_snapshot_consumed_by_both_projections_without_db_access(self, mock_db_cls):
        """Test that the same PresentationSnapshot instance is passed to both projections without DB interaction."""
        mock_st = create_mock_st()

        with patch("ui.presentation.projections.st", mock_st):
            # Render Chat-first
            render_chat_first(self.snapshot)
            # Render Command Center with exact same snapshot instance
            render_command_center(self.snapshot)

        # DatabaseManager must NEVER be instantiated or called by projections
        mock_db_cls.assert_not_called()

    def test_chat_first_projection_structure(self):
        """Test Chat-first projection emphasizes conversation feed and prompt display."""
        mock_st = create_mock_st()

        with patch("ui.presentation.projections.st", mock_st):
            render_chat_first(self.snapshot)

        # Verify chat_message context manager invoked for user and assistant
        self.assertEqual(mock_st.chat_message.call_count, 4)  # 2 chats x (1 user + 1 assistant)
        mock_st.chat_message.assert_any_call("user")
        mock_st.chat_message.assert_any_call("assistant")

        # Verify New Chat button key for chat_first
        button_keys = [call.kwargs.get("key") for call in mock_st.button.call_args_list if "key" in call.kwargs]
        self.assertIn("chat_first_new_chat_btn", button_keys)

    def test_command_center_projection_structure(self):
        """Test Command Center projection emphasizes system metrics, gate score, and agent responses."""
        mock_st = create_mock_st()

        with patch("ui.presentation.projections.st", mock_st):
            render_command_center(self.snapshot)

        # Verify metrics called for operational status
        self.assertTrue(mock_st.metric.called)
        metric_labels = [call.args[0] for call in mock_st.metric.call_args_list if call.args]
        self.assertIn("Context Tokens", metric_labels)
        self.assertIn("Total Chats", metric_labels)

        # Verify expander used for structured debate entries
        self.assertTrue(mock_st.expander.called)

        # Verify New Chat button key for command center
        button_keys = [call.kwargs.get("key") for call in mock_st.button.call_args_list if "key" in call.kwargs]
        self.assertIn("cmd_center_new_chat_btn", button_keys)

    def test_projections_empty_state_handling(self):
        """Test both projections handle empty chats and missing memory gracefully without errors."""
        empty_snapshot = build_presentation_snapshot(
            {"id": "empty-1", "name": "Empty Session", "mode": "coding", "created_at": "2025-02-18"},
            [],
            None
        )
        mock_st = create_mock_st()

        with patch("ui.presentation.projections.st", mock_st):
            # Chat-first empty state
            render_chat_first(empty_snapshot)
            mock_st.info.assert_called_with("No messages in this session yet. Start a conversation below.")

            mock_st.reset_mock()
            mock_st.columns.side_effect = lambda spec: [MagicMock() for _ in range(spec if isinstance(spec, int) else len(spec))]

            # Command Center empty state
            render_command_center(empty_snapshot)
            info_messages = [call.args[0] for call in mock_st.info.call_args_list if call.args]
            self.assertIn("Memory status snapshot unavailable.", info_messages)
            self.assertIn("No execution/debate data logged in this session yet.", info_messages)

    def test_projections_malformed_debate_error_state_handling(self):
        """Test projections handle malformed debate data represented by has_error=True gracefully."""
        corrupt_chats = [
            {
                "id": "c-bad",
                "prompt": "Test bad debate",
                "mode": "continue",
                "final_answer": "Response text",
                "debate_data": "{corrupt_json: true",
                "tokens_used": 100,
                "cost": 0.0001,
            }
        ]
        corrupt_snapshot = build_presentation_snapshot(
            self.sample_session, corrupt_chats, self.sample_memory
        )
        mock_st = create_mock_st()

        with patch("ui.presentation.projections.st", mock_st):
            render_chat_first(corrupt_snapshot)
            render_command_center(corrupt_snapshot)

        # Verify error call in Command Center for malformed debate
        mock_st.error.assert_any_call("⚠️ Debate details contain errors or unparseable data.")

    def test_rendering_does_not_mutate_snapshot(self):
        """Test that passing a snapshot to renderers does not mutate any fields or collections."""
        snapshot_before = copy.deepcopy(self.snapshot)

        mock_st = create_mock_st()
        with patch("ui.presentation.projections.st", mock_st):
            render_chat_first(self.snapshot)
            render_command_center(self.snapshot)

        self.assertEqual(self.snapshot, snapshot_before)


    def test_command_center_agent_response_safe_rendering(self):
        """Test that agent response text is rendered via safe markdown primitives and not interpolated into HTML markdown strings."""
        html_payload = "<img src=x onerror=alert(1)> <script>alert(1)</script>"
        raw_chats = [
            {
                "id": "c-html",
                "prompt": "Test XSS payload",
                "mode": "continue",
                "final_answer": "Final output",
                "debate_data": json.dumps({
                    "gate_score": 8,
                    "responses": [
                        {"agent": "agent_x", "text": html_payload, "status": "success"}
                    ]
                }),
                "tokens_used": 100,
                "cost": 0.0001,
            }
        ]
        html_snapshot = build_presentation_snapshot(
            self.sample_session, raw_chats, self.sample_memory
        )

        mock_st = create_mock_st()
        with patch("ui.presentation.projections.st", mock_st):
            render_command_center(html_snapshot)

        # Verify st.markdown was called with raw text payload
        mock_st.markdown.assert_any_call(html_payload)

        # Verify no call to st.markdown with unsafe_allow_html=True contained the raw agent response html_payload
        for call in mock_st.markdown.call_args_list:
            if call.kwargs.get("unsafe_allow_html"):
                markdown_arg = call.args[0] if call.args else ""
                self.assertNotIn(html_payload, markdown_arg, "Agent response text must NOT be interpolated into HTML with unsafe_allow_html=True")

if __name__ == "__main__":
    unittest.main()

    unittest.main()
