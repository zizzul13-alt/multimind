"""Conversation retrieval and durable task checkpoints using existing DB contracts."""
from __future__ import annotations
import json
from core.operating_model import crystallize_task_state,format_retrieved_context,retrieve_relevant_chats
class ConversationStateService:
    def __init__(self,database): self.db=database
    def _session(self,session_id): return next((row for row in self.db.get_sessions() if row.get("id")==session_id),None)
    def retrieve(self,session_id,query,limit=6):
        rows=[]
        for session in self.db.get_sessions():
            for row in self.db.get_session_chats(session.get("id"),limit=50):
                item=dict(row); item.setdefault("session_id",session.get("id")); rows.append(item)
        return retrieve_relevant_chats(rows,query,limit=limit)
    def context(self,session_id,query,limit=6): return format_retrieved_context(self.retrieve(session_id,query,limit))
    def operating_state(self,session_id):
        session=self._session(session_id)
        if not session: return {}
        try: config=json.loads(session.get("config") or "{}")
        except (TypeError,ValueError): return {}
        return dict(config.get("operating_state") or {})
    def task_state(self,session_id): return dict(self.operating_state(session_id).get("task") or {})
    def crystallize(self,session_id,prompt,authority="think"):
        previous=self.task_state(session_id); task=crystallize_task_state(prompt,previous,authority)
        if task is previous or task is None: return previous
        updater=getattr(self.db,"update_session_config",None)
        if not callable(updater): return task
        session=self._session(session_id)
        try: config=json.loads((session or {}).get("config") or "{}")
        except (TypeError,ValueError): config={}
        state=dict(config.get("operating_state") or {}); state["task"]=task; config["operating_state"]=state; updater(session_id,config); return task
