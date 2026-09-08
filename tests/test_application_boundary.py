"""Focused regression coverage for the plain-Python application boundary."""
import inspect
import json
import pytest
from core.application import ChatRequest, MultiMindApplication
from core.memory import SessionMemory, persist_chat_and_update_memory

class RecordingAgent:
    def __init__(self, response=None):
        self.response = response or {"status":"success","text":"usable answer","tokens":7,"cost":0.2}
        self.requests=[]
    def generate(self, **kwargs): self.requests.append(kwargs); return self.response

class RecordingDatabase:
    def __init__(self): self.saved=[]; self.sessions=[]
    def save_chat(self, session_id, chat_data): self.saved.append((session_id,chat_data)); return True
    def create_session(self, session_id, name, mode): self.sessions.append((session_id,name,mode)); return True
    def get_session_chats_for_memory(self,_session_id): return []

class UploadHandler:
    @staticmethod
    def handle(_uploads,_gemini): return {"files":[{"filename":"notes.txt","content":"upload marker"}]}

@pytest.mark.parametrize("route", ["unified","remote"])
def test_plain_python_chat_normalizes_direct_runtime_prompt_without_importing_streamlit(route):
    assert "streamlit" not in inspect.getsource(MultiMindApplication).lower()
    agent=RecordingAgent(); application=MultiMindApplication(agents={route:agent},file_handler=UploadHandler)
    result=application.execute_chat(ChatRequest(original_prompt="original",uploads=[object()],context_mode="standalone",active_agents=[route],session_mode="research"))
    assert result.status=="success"
    request=agent.requests[0]
    assert request["mode"]=="research" and request["system_prompt"] is None
    assert request["prompt"].count("upload marker")==1
    assert "TASK MODE: RESEARCH" in request["prompt"]
    assert request["prompt"].endswith("USER TASK (preserve intent and literal constraints):\n\noriginal")


def test_direct_execution_persists_raw_and_semantic_metadata_before_memory_mutation():
    agent=RecordingAgent(); database=RecordingDatabase(); memories={"s1":SessionMemory()}; observed=[]
    def persist(db,session_id,runtime_memories,chat_data):
        observed.append(list(runtime_memories[session_id].short_term)); return persist_chat_and_update_memory(db,session_id,runtime_memories,chat_data)
    application=MultiMindApplication(agents={"unified":agent,"gemini":object()},runtime_memories=memories,db=database,file_handler=UploadHandler,persist_chat=persist,compressor=type("Compressor",(),{"compress":staticmethod(lambda _prompt,_agent:{"compressed":"compressed"})}))
    result=application.execute_chat(ChatRequest(original_prompt="original",uploads=[object()],context_mode="standalone",session_id="s1",compressor_enabled=True,active_agents=["unified"]))
    assert result.status=="success" and result.persisted is True and observed==[[]]
    saved=database.saved[0][1]
    assert saved["prompt"]=="original"
    metadata=json.loads(saved["prompt_compressed"])
    assert metadata["effective"]=="compressed" and metadata["mode"]=="coding"
    assert result.debate_data["product_semantics"]["raw_prompt"]=="original"
    assert [e["prompt"] for e in memories["s1"].short_term]==["original"]
    assert agent.requests[0]["prompt"].endswith("TASK:\ncompressed")


def test_debate_receives_normalized_prompt_and_bounded_context_without_direct_composition():
    captured={}
    class Orchestrator:
        def __init__(self,**_agents): pass
        def debate(self,**kwargs): captured.update(kwargs); return {"status":"success","final_answer":"answer","total_tokens":1,"total_cost":0}
    memory=SessionMemory(); memory.add_chat("history","answer"); database=RecordingDatabase(); at_persist=[]
    def persist(db,session_id,runtime_memories,chat_data):
        at_persist.append([e["prompt"] for e in runtime_memories[session_id].short_term]); return persist_chat_and_update_memory(db,session_id,runtime_memories,chat_data)
    application=MultiMindApplication(agents={"cloudflare":object()},runtime_memories={"s1":memory},db=database,debate_factory=Orchestrator,file_handler=UploadHandler,persist_chat=persist)
    result=application.execute_chat(ChatRequest(original_prompt="original",uploads=[object()],context_mode="continue",session_id="s1",active_agents=["cloudflare"],debate_rounds=3,selected_skill="default"))
    assert result.status=="success"
    assert captured["prompt"].startswith("MULTIMIND COMMON TASK SPECIFICATION")
    assert captured["prompt"].endswith("USER TASK (preserve intent and literal constraints):\n\noriginal")
    assert captured["context"].count("upload marker")==1 and "CONTEXT:" not in captured["prompt"]
    assert captured["rounds"]==3 and captured["skill"] is None
    assert at_persist==[["history"]] and database.saved[0][0]=="s1"
    assert [e["prompt"] for e in memory.short_term]==["history","original"]


def test_terminal_failure_does_not_persist_or_mutate_memory():
    database=RecordingDatabase(); memory=SessionMemory(); memory.add_chat("saved","answer")
    application=MultiMindApplication(agents={"unified":RecordingAgent({"status":"error","text":"private","tokens":0,"cost":0})},runtime_memories={"s1":memory},db=database)
    result=application.execute_chat(ChatRequest("unsaved",session_id="s1",active_agents=["unified"]))
    assert result.status=="error" and database.saved==[] and [e["prompt"] for e in memory.short_term]==["saved"]


def test_session_lifecycle_is_plain_python():
    database=RecordingDatabase(); application=MultiMindApplication(db=database)
    session_id=application.create_session("Plan","thinking"); selected=application.select_session({"id":session_id,"name":"Plan"})
    assert database.sessions==[(session_id,"Plan","thinking")] and selected["id"]==session_id and session_id in application.runtime_memories
