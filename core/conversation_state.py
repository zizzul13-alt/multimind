"""Conversation retrieval and task checkpoints using existing database contracts."""
from __future__ import annotations
import json
from core.operating_model import crystallize_task_state,format_retrieved_context,retrieve_relevant_chats
class ConversationStateService:
    def __init__(self,database): self.db=database
    def retrieve(self,session_id,query,limit=6):
        rows=[]
        for session in self.db.get_sessions():
            sid=session.get("id")
            for row in self.db.get_session_chats(sid,limit=50):
                item=dict(row); item.setdefault("session_id",sid); rows.append(item)
        return retrieve_relevant_chats(rows,query,limit=limit)
    def context(self,session_id,query,limit=6): return format_retrieved_context(self.retrieve(session_id,query,limit))
    def task_state(self,session_id):
        rows=self.db.get_session_chats(session_id,limit=50)
        for row in reversed(rows):
            raw=row.get("debate_data") or "{}"
            try: data=json.loads(raw) if isinstance(raw,str) else dict(raw)
            except (TypeError,ValueError): continue
            task=((data.get("product_semantics") or {}).get("task_state"))
            if isinstance(task,dict) and task: return dict(task)
        return {}
    def crystallize(self,session_id,prompt,authority="think"):
        return crystallize_task_state(prompt,self.task_state(session_id),authority) or {}
