from pathlib import Path

import reflex as rx

from core.application import ChatRequest, MultiMindApplication
from multimind_reflex.bridge import (
    BufferedUpload,
    build_host_application,
    environment_secrets_source,
)
from utils.config import Config


def test_reflex_version_is_locked_to_proven_baseline():
    requirements = Path("requirements.txt").read_text(encoding="utf-8")
    assert "reflex==0.8.22" in requirements.splitlines()


def test_environment_secrets_source_uses_deployment_mapping_without_streamlit(monkeypatch):
    source = environment_secrets_source(
        {
            "MULTIMIND_GEMINI_KEY": "g-key",
            "GROQ_API_KEY": "groq-key",
            "MULTIMIND_REMOTE_URL": "http://remote.invalid",
        }
    )
    assert source["default"]["gemini_key"] == "g-key"
    assert source["default"]["groq_key"] == "groq-key"
    assert source["default"]["remote_url"] == "http://remote.invalid"
    bridge_source = Path("multimind_reflex/bridge.py").read_text(encoding="utf-8")
    assert "streamlit" not in bridge_source.lower()


def test_reflex_bridge_executes_real_application_session_and_upload_path(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "DB_DIR", str(tmp_path / "data"))

    class FakeUnifiedAgent:
        def __init__(self):
            self.prompts = []

        def generate(self, prompt, system_prompt=None, mode="coding"):
            self.prompts.append(prompt)
            return {
                "status": "success",
                "text": "host-ok",
                "tokens": 7,
                "cost": 0.0,
            }

    agent = FakeUnifiedAgent()
    memories = {}
    application = build_host_application(
        "alice",
        memories,
        agents={"unified": agent},
    )
    assert isinstance(application, MultiMindApplication)

    session_id = application.create_session("RJ2", "coding")
    sessions = application.list_sessions()
    selected = next(session for session in sessions if session["id"] == session_id)
    application.select_session(selected)

    result = application.execute_chat(
        ChatRequest(
            original_prompt="Use the staged file",
            uploads=[BufferedUpload("note.txt", b"reflex upload context")],
            context_mode="continue",
            session_id=session_id,
            session_mode="coding",
            active_agents=["unified"],
        )
    )

    assert result.status == "success"
    assert result.persisted is True
    assert result.final_answer == "host-ok"
    assert agent.prompts
    assert "FILE: note.txt" in agent.prompts[-1]
    assert "reflex upload context" in agent.prompts[-1]
    chats = application.get_session_chats(session_id)
    assert len(chats) == 1
    assert chats[0]["final_answer"] == "host-ok"


def test_reflex_state_contract_uses_supported_background_and_duplicate_guard():
    source = Path("multimind_reflex/state.py").read_text(encoding="utf-8")
    run_start = source.index("@rx.event(background=True)")
    run_source = source[run_start:]

    assert "async def run_chat" in run_source
    assert "async with self" in run_source
    assert "if self.busy:" in run_source
    assert "self.busy = True" in run_source
    assert run_source.index("if self.busy:") < run_source.index("self.busy = True")
    assert "asyncio.to_thread" in run_source
    assert "application.execute_chat" in run_source
    assert "rx.UploadFile" not in run_source


def test_uploadfile_is_consumed_before_background_execution():
    source = Path("multimind_reflex/state.py").read_text(encoding="utf-8")
    stage_start = source.index("async def stage_uploads")
    run_start = source.index("@rx.event(background=True)")
    stage_source = source[stage_start:run_start]
    assert "list[rx.UploadFile]" in stage_source
    assert "await upload.read()" in stage_source
    assert "BufferedUpload" in source[run_start:]


def test_reflex_host_has_no_rest_glue_or_custom_javascript():
    package_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path("multimind_reflex").glob("*.py")
    )
    lowered = package_source.lower()
    assert "fastapi" not in lowered
    assert "flask" not in lowered
    assert "javascript" not in lowered
    assert "requests." not in lowered


def test_reflex_surface_constructs_with_real_reflex_components():
    from multimind_reflex.multimind_reflex import app, index

    assert isinstance(app, rx.App)
    assert index() is not None
