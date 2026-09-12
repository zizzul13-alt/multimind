import json
from core.conversation_state import ConversationStateService
from core.operating_model import crystallize_task_state,retrieve_relevant_chats,select_auto_identities,select_work_mode

def test_manual_work_mode_overrides_auto_inference():
    result=select_work_mode("implement this repository fix","research","manual")
    assert result["selected"]=="research" and result["reason"]=="manual_override"

def test_auto_work_mode_is_deterministic_and_authority_free():
    assert select_work_mode("implement code and run pytest","thinking","auto")["selected"]=="coding"
    assert select_work_mode("research latest benchmark sources","coding","auto")["selected"]=="research"

def test_task_crystallization_requires_explicit_execution_intent_and_preserves_authority():
    assert crystallize_task_state("could this maybe work?",None,"act") is None
    task=crystallize_task_state("gas implement bounded fix",None,"think")
    assert task["status"]=="active" and task["authority"]=="think"

def test_auto_ai_selects_only_available_identities():
    selected=select_auto_identities("thinking",["gemini","qwen"],count=2)
    assert selected==["gemini","qwen"]
    assert "claude" not in selected

def test_retrieval_prefers_relevant_history():
    rows=[{"prompt":"music discovery","final_answer":"track list"},{"prompt":"MultiMind memory architecture","final_answer":"SQLite retrieval"}]
    result=retrieve_relevant_chats(rows,"memory SQLite MultiMind",limit=1)
    assert result[0]["prompt"]=="MultiMind memory architecture"

class FakeDb:
    def __init__(self):
        self.sessions=[{"id":"s1"},{"id":"s2"}]
        self.rows={"s1":[{"session_id":"s1","prompt":"old unrelated","final_answer":"x","debate_data":"{}"}],"s2":[{"session_id":"s2","prompt":"MultiMind provider routing","final_answer":"identity truth","debate_data":"{}"}]}
    def get_sessions(self): return self.sessions
    def get_session_chats(self,session_id,limit=50): return list(self.rows[session_id])[:limit]

def test_cross_session_retrieval_uses_existing_user_scoped_database_contract():
    service=ConversationStateService(FakeDb())
    rows=service.retrieve("s1","provider identity routing",limit=2)
    assert rows and rows[0]["session_id"]=="s2"

def test_task_checkpoint_reads_last_persisted_product_semantics():
    db=FakeDb(); task={"objective":"ship it","authority":"think","status":"active"}; db.rows["s1"].append({"session_id":"s1","prompt":"gas","final_answer":"done","debate_data":json.dumps({"product_semantics":{"task_state":task}})})
    assert ConversationStateService(db).task_state("s1")==task
