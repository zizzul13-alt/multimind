"""Focused regression coverage for the plain-Python application boundary."""
import inspect

import pytest

from core.application import ChatRequest, MultiMindApplication
from core.memory import SessionMemory, persist_chat_and_update_memory


class RecordingAgent:
    def __init__(self, response=None):
        self.response = response or {
            "status": "success", "text": "usable answer", "tokens": 7, "cost": 0.2,
        }
        self.requests = []

    def generate(self, **kwargs):
        self.requests.append(kwargs)
        return self.response


class RecordingDatabase:
    def __init__(self):
        self.saved = []
        self.sessions = []

    def save_chat(self, session_id, chat_data):
        self.saved.append((session_id, chat_data))
        return True

    def create_session(self, session_id, name, mode):
        self.sessions.append((session_id, name, mode))
        return True

    def get_session_chats_for_memory(self, _session_id):
        return []


class UploadHandler:
    @staticmethod
    def handle(_uploads, _gemini):
        return {"files": [{"filename": "notes.txt", "content": "upload marker"}]}


@pytest.mark.parametrize("route", ["unified", "remote"])
def test_plain_python_chat_does_not_import_streamlit_and_preserves_direct_runtime_prompt(route):
    source = inspect.getsource(MultiMindApplication)
    assert "streamlit" not in source.lower()
    agent = RecordingAgent()
    app = MultiMindApplication(agents={route: agent}, file_handler=UploadHandler)

    result = app.execute_chat(ChatRequest(
        original_prompt="original", uploads=[object()], context_mode="standalone",
        active_agents=[route], session_mode="research",
    ))

    assert result.status == "success"
    assert agent.requests == [{
        # Matches the pre-extraction app.py construction exactly: file content
        # contributes its trailing newline plus context assembly's separator,
        # then the direct runtime template adds its two task separators.
        "prompt": "CONTEXT:\n\n--- FILE: notes.txt ---\nupload marker\n\n\n\nTASK:\noriginal",
        "system_prompt": None, "mode": "research",
    }]


def test_direct_execution_persists_original_prompt_after_success_before_memory_mutation():
    agent = RecordingAgent()
    database = RecordingDatabase()
    memories = {"s1": SessionMemory()}
    observed_memory_at_write = []

    def persist(db, session_id, runtime_memories, chat_data):
        observed_memory_at_write.append(list(runtime_memories[session_id].short_term))
        return persist_chat_and_update_memory(db, session_id, runtime_memories, chat_data)

    app = MultiMindApplication(
        agents={"unified": agent, "gemini": object()}, runtime_memories=memories,
        db=database, file_handler=UploadHandler, persist_chat=persist,
        compressor=type("Compressor", (), {"compress": staticmethod(lambda _prompt, _agent: {"compressed": "compressed"})}),
    )
    result = app.execute_chat(ChatRequest(
        original_prompt="original", uploads=[object()], context_mode="standalone", session_id="s1",
        compressor_enabled=True, active_agents=["unified"],
    ))

    assert result.status == "success" and result.persisted is True
    assert observed_memory_at_write == [[]]
    assert database.saved[0][1]["prompt"] == "original"
    assert database.saved[0][1]["prompt_compressed"] == '{"compressed": "compressed"}'
    assert [entry["prompt"] for entry in memories["s1"].short_term] == ["original"]
    assert agent.requests[0]["prompt"].endswith("TASK:\ncompressed")


def test_debate_receives_final_prompt_and_bounded_context_without_direct_composition():
    captured = {}

    class Orchestrator:
        def __init__(self, **_agents):
            pass

        def debate(self, **kwargs):
            captured.update(kwargs)
            return {"status": "success", "final_answer": "answer", "total_tokens": 1, "total_cost": 0}

    memory = SessionMemory()
    memory.add_chat("history", "answer")
    database = RecordingDatabase()
    memory_at_persist = []

    def persist(db, session_id, runtime_memories, chat_data):
        memory_at_persist.append([entry["prompt"] for entry in runtime_memories[session_id].short_term])
        return persist_chat_and_update_memory(db, session_id, runtime_memories, chat_data)

    app = MultiMindApplication(
        agents={"cloudflare": object()}, runtime_memories={"s1": memory},
        db=database, debate_factory=Orchestrator, file_handler=UploadHandler,
        persist_chat=persist,
    )
    result = app.execute_chat(ChatRequest(
        original_prompt="original", uploads=[object()], context_mode="continue", session_id="s1",
        active_agents=["cloudflare"], debate_rounds=3, selected_skill="default",
    ))

    assert result.status == "success"
    assert captured["prompt"] == "original"
    assert captured["context"].count("upload marker") == 1
    assert "CONTEXT:" not in captured["prompt"]
    assert captured["rounds"] == 3
    assert memory_at_persist == [["history"]]
    assert database.saved[0][0] == "s1"
    assert [entry["prompt"] for entry in memory.short_term] == ["history", "original"]


def test_terminal_failure_does_not_persist_or_mutate_memory():
    database = RecordingDatabase()
    memory = SessionMemory()
    memory.add_chat("saved", "answer")
    app = MultiMindApplication(
        agents={"unified": RecordingAgent({"status": "error", "text": "private", "tokens": 0, "cost": 0})},
        runtime_memories={"s1": memory}, db=database,
    )

    result = app.execute_chat(ChatRequest("unsaved", session_id="s1", active_agents=["unified"]))

    assert result.status == "error"
    assert database.saved == []
    assert [entry["prompt"] for entry in memory.short_term] == ["saved"]


def test_session_lifecycle_is_plain_python():
    database = RecordingDatabase()
    app = MultiMindApplication(db=database)

    session_id = app.create_session("Plan", "thinking")
    selected = app.select_session({"id": session_id, "name": "Plan"})

    assert database.sessions == [(session_id, "Plan", "thinking")]
    assert selected["id"] == session_id
    assert session_id in app.runtime_memories
