from types import SimpleNamespace
from unittest.mock import Mock
import json
import pytest
import app

UPLOAD_CONTENT="uploaded context marker"

class RecordingAgent:
    def __init__(self): self.requests=[]
    def generate(self,**kwargs): self.requests.append(kwargs); return {"status":"success","text":"usable response","agent":"Test","tokens":1,"cost":0.0}

def _state(active_agents,*,compressor_enabled=False):
    class SessionState(SimpleNamespace):
        def get(self,key,default=None): return getattr(self,key,default)
    return SessionState(user_id="test-user",compressor_enabled=compressor_enabled,current_session={"id":"session-1","mode":"coding"},active_agents=active_agents,debate_rounds=1,selected_skill="default",memories={})

def _agents(**overrides):
    agents={name:None for name in ("unified","remote","gemini","deepseek","groq","cloudflare","openrouter","huggingface")}; agents.update(overrides); return agents

def _configure_process_chat(monkeypatch,active_agents,agents,*,compressor_enabled=False):
    ui=SimpleNamespace(session_state=_state(active_agents,compressor_enabled=compressor_enabled),error=Mock(),success=Mock(),warning=Mock(),rerun=Mock())
    persist=Mock(); monkeypatch.setattr(app,"st",ui); monkeypatch.setattr(app,"get_agents",lambda _user_id:agents)
    monkeypatch.setattr(app.FileHandler,"handle",lambda _files,_gemini:{"files":[{"filename":"notes.txt","content":UPLOAD_CONTENT}]})
    monkeypatch.setattr(app,"get_db_manager",Mock()); monkeypatch.setattr(app,"persist_chat_and_update_memory",persist); return persist

@pytest.mark.parametrize("route",["unified","remote"])
def test_uploaded_content_reaches_normalized_direct_route_once(monkeypatch,route):
    agent=RecordingAgent(); _configure_process_chat(monkeypatch,[route],_agents(**{route:agent}))
    app.process_chat("original user prompt",[object()],"standalone")
    prompt=agent.requests[0]["prompt"]
    assert prompt.count(UPLOAD_CONTENT)==1
    assert "MULTIMIND COMMON TASK SPECIFICATION" in prompt
    assert prompt.endswith("USER TASK (preserve intent and literal constraints):\n\noriginal user prompt")


def test_direct_route_preserves_original_prompt_and_semantic_metadata(monkeypatch):
    unified=RecordingAgent(); persist=_configure_process_chat(monkeypatch,["unified"],_agents(unified=unified,gemini=object()),compressor_enabled=True)
    monkeypatch.setattr(app.PromptCompressor,"compress",lambda _prompt,_agent:{"compressed":"compressed runtime prompt"})
    app.process_chat("original user prompt",[object()],"standalone")
    assert unified.requests[0]["prompt"].endswith("TASK:\ncompressed runtime prompt")
    saved=persist.call_args.args[3]
    assert saved["prompt"]=="original user prompt"
    metadata=json.loads(saved["prompt_compressed"])
    assert metadata["effective"]=="compressed runtime prompt" and metadata["mode"]=="coding"


def test_debate_route_receives_upload_context_and_common_task(monkeypatch):
    captured={}
    class RecordingOrchestrator:
        def __init__(self,**_kwargs): pass
        def debate(self,**kwargs): captured.update(kwargs); return {"status":"success","final_answer":"usable response","responses":[],"total_tokens":1,"total_cost":0.0}
    _configure_process_chat(monkeypatch,["cloudflare"],_agents()); monkeypatch.setattr(app,"DebateOrchestrator",RecordingOrchestrator)
    app.process_chat("original user prompt",[object()],"standalone")
    assert captured["prompt"].startswith("MULTIMIND COMMON TASK SPECIFICATION")
    assert captured["prompt"].endswith("USER TASK (preserve intent and literal constraints):\n\noriginal user prompt")
    assert captured["context"].count(UPLOAD_CONTENT)==1 and "CONTEXT:" not in captured["prompt"]
