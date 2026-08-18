"""
Unit and regression tests for Archetype Projections (ui/presentation/projections.py).

Proves that:
1. All 7 archetype projections consume the exact same PresentationSnapshot contract.
2. Projections execute pure UI rendering with ZERO database access or core state queries.
3. Rendering projections does NOT mutate PresentationSnapshot instances or internal snapshots.
4. Each projection preserves the "New Chat" action with a unique button key.
5. All 7 projections handle edge cases safely (empty chats, missing memory, malformed debate JSON).
6. Dynamic provider/user text is rendered safely without unsafe HTML string interpolation.
7. Each projection exhibits an observable semantic hierarchy distinction matching its primary mental model.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import copy

from ui.presentation import (
    build_presentation_snapshot,
)
from ui.presentation.projections import (
    render_chat_first,
    render_command_center,
    render_ai_workspace,
    render_ai_research_lab,
    render_agent_canvas,
    render_terminal_hacker,
    render_minimal_saas,
)

ALL_PROJECTIONS = [
    render_chat_first,
    render_command_center,
    render_ai_workspace,
    render_ai_research_lab,
    render_agent_canvas,
    render_terminal_hacker,
    render_minimal_saas,
]

EXPECTED_BUTTON_KEYS = [
    "chat_first_new_chat_btn",
    "cmd_center_new_chat_btn",
    "ai_workspace_new_chat_btn",
    "ai_research_lab_new_chat_btn",
    "agent_canvas_new_chat_btn",
    "terminal_hacker_new_chat_btn",
    "minimal_saas_new_chat_btn",
]


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
    def test_single_snapshot_consumed_by_all_seven_projections_without_db_access(self, mock_db_cls):
        """Test that the same PresentationSnapshot instance is passed to all 7 projections without DB interaction."""
        mock_st = create_mock_st()

        with patch("ui.presentation.projections.st", mock_st):
            for proj_fn in ALL_PROJECTIONS:
                proj_fn(self.snapshot)

        # DatabaseManager must NEVER be instantiated or called by projections
        mock_db_cls.assert_not_called()

    def test_unique_new_chat_button_keys(self):
        """Test that all 7 projections define unique button keys for New Chat action."""
        mock_st = create_mock_st()

        with patch("ui.presentation.projections.st", mock_st):
            for proj_fn in ALL_PROJECTIONS:
                proj_fn(self.snapshot)

        button_keys = [call.kwargs.get("key") for call in mock_st.button.call_args_list if "key" in call.kwargs]
        for expected_key in EXPECTED_BUTTON_KEYS:
            self.assertIn(expected_key, button_keys)
        self.assertEqual(len(set(EXPECTED_BUTTON_KEYS)), 7)

    def test_all_projections_empty_state_handling(self):
        """Test all 7 projections handle empty chats and missing memory gracefully without exceptions."""
        empty_snapshot = build_presentation_snapshot(
            {"id": "empty-1", "name": "Empty Session", "mode": "coding", "created_at": "2025-02-18"},
            [],
            None
        )
        mock_st = create_mock_st()

        with patch("ui.presentation.projections.st", mock_st):
            for proj_fn in ALL_PROJECTIONS:
                proj_fn(empty_snapshot)

        self.assertTrue(mock_st.info.called)

    def test_all_projections_malformed_debate_error_state_handling(self):
        """Test all 7 projections handle malformed debate data represented by has_error=True gracefully."""
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
            for proj_fn in ALL_PROJECTIONS:
                proj_fn(corrupt_snapshot)

    def test_rendering_does_not_mutate_snapshot(self):
        """Test that passing a snapshot to all 7 renderers does not mutate any fields or collections."""
        snapshot_before = copy.deepcopy(self.snapshot)

        mock_st = create_mock_st()
        with patch("ui.presentation.projections.st", mock_st):
            for proj_fn in ALL_PROJECTIONS:
                proj_fn(self.snapshot)

        self.assertEqual(self.snapshot, snapshot_before)

    def test_all_projections_agent_response_safe_rendering(self):
        """Test that dynamic text is rendered via safe Streamlit primitives and not interpolated into HTML strings with unsafe_allow_html=True."""
        html_payload = "<img src=x onerror=alert('xss')>"
        raw_chats = [
            {
                "id": "c-html",
                "prompt": html_payload,
                "mode": "continue",
                "final_answer": html_payload,
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
            for proj_fn in ALL_PROJECTIONS:
                proj_fn(html_snapshot)

        # Check that no unsafe_allow_html=True markdown call contained the raw payload
        for call in mock_st.markdown.call_args_list:
            if call.kwargs.get("unsafe_allow_html"):
                markdown_arg = call.args[0] if call.args else ""
                self.assertNotIn(html_payload, markdown_arg, "Dynamic user/agent content must NOT be interpolated into unsafe HTML strings.")

    # ==================== SEMANTIC HIERARCHY REGRESSION TESTS ====================

    def test_semantic_hierarchy_chat_first(self):
        """Prove Chat-first projection emphasizes conversation feed via chat_message primitives."""
        mock_st = create_mock_st()
        with patch("ui.presentation.projections.st", mock_st):
            render_chat_first(self.snapshot)

        self.assertEqual(mock_st.chat_message.call_count, 4)  # 2 user + 2 assistant
        mock_st.chat_message.assert_any_call("user")
        mock_st.chat_message.assert_any_call("assistant")

    def test_semantic_hierarchy_command_center(self):
        """Prove Command Center emphasizes system operational state and comparative agent output."""
        mock_st = create_mock_st()
        with patch("ui.presentation.projections.st", mock_st):
            render_command_center(self.snapshot)

        # Operational metrics present
        metric_labels = [call.args[0] for call in mock_st.metric.call_args_list if call.args]
        self.assertIn("Total Chats", metric_labels)
        self.assertIn("Context Tokens", metric_labels)
        # Operational expanders present
        self.assertTrue(mock_st.expander.called)

    def test_semantic_hierarchy_ai_workspace(self):
        """Prove AI Workspace emphasizes workspace objects organization."""
        mock_st = create_mock_st()
        with patch("ui.presentation.projections.st", mock_st):
            render_ai_workspace(self.snapshot)

        metric_labels = [call.args[0] for call in mock_st.metric.call_args_list if call.args]
        self.assertIn("Workspace Objects", metric_labels)
        self.assertTrue(mock_st.container.called)

    def test_semantic_hierarchy_ai_research_lab(self):
        """Prove AI Research Lab emphasizes findings, evidence, and synthesized conclusion."""
        mock_st = create_mock_st()
        with patch("ui.presentation.projections.st", mock_st):
            render_ai_research_lab(self.snapshot)

        markdown_calls = [call.args[0] for call in mock_st.markdown.call_args_list if call.args]
        self.assertTrue(any("Synthesized Conclusion" in msg for msg in markdown_calls))
        self.assertTrue(any("Agent Findings & Evidence Analysis" in msg for msg in markdown_calls))

    def test_semantic_hierarchy_agent_canvas(self):
        """Prove Agent Canvas emphasizes agent roles and execution step workflow topology."""
        mock_st = create_mock_st()
        with patch("ui.presentation.projections.st", mock_st):
            render_agent_canvas(self.snapshot)

        markdown_calls = [call.args[0] for call in mock_st.markdown.call_args_list if call.args]
        self.assertTrue(any("Workflow Sequence & Agent Roles Topology" in msg for msg in markdown_calls))
        self.assertTrue(any("Agent Execution Step Flow" in msg for msg in markdown_calls))

    def test_semantic_hierarchy_terminal_hacker(self):
        """Prove Terminal / Hacker AI emphasizes instruction -> execution -> output sequence stream."""
        mock_st = create_mock_st()
        with patch("ui.presentation.projections.st", mock_st):
            render_terminal_hacker(self.snapshot)

        markdown_calls = [call.args[0] for call in mock_st.markdown.call_args_list if call.args]
        text_calls = [call.args[0] for call in mock_st.text.call_args_list if call.args]

        self.assertTrue(any("USER_INSTRUCTION" in msg for msg in markdown_calls))
        self.assertTrue(any("SYSTEM_OUTPUT" in msg for msg in markdown_calls))
        self.assertTrue(any("EXECUTION_SEQUENCE" in msg for msg in text_calls))

    def test_semantic_hierarchy_minimal_saas(self):
        """Prove Minimal SaaS emphasizes primary active task with progressive disclosure for secondary history."""
        mock_st = create_mock_st()
        with patch("ui.presentation.projections.st", mock_st):
            render_minimal_saas(self.snapshot)

        markdown_calls = [call.args[0] for call in mock_st.markdown.call_args_list if call.args]
        self.assertTrue(any("Active Task" in msg for msg in markdown_calls))

        # Secondary history placed inside expander
        expander_labels = [call.args[0] for call in mock_st.expander.call_args_list if call.args]
        self.assertTrue(any("Prior Task History" in label for label in expander_labels))


if __name__ == "__main__":
    unittest.main()
