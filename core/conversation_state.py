"""Durable conversation retrieval and task-state service over existing DB seams."""
from __future__ import annotations
from core.operating_model import crystallize_task_state, format_retrieved_context, retrieve_relevant_chats

class ConversationStateService:
    def __init__(self,database): self.db=database
    def retrieve(self,session_id,query,limit=6):
        getter=getattr(self.db,"search_relevant_chats",None)
        rows=getter(query,limit=limit,exclude_session_id=None) if callable(getter) else self.db.get_session_chats_for_memory(session_id)
        return retrieve_relevant_chats(rows,query,limit=limit)
    def context(self,session_id,query,limit=6): return format_retrieved_context(self.retrieve(session_id,query,limit))
    def task_state(self,session_id):
        getter=getattr(self.db,"get_session_operating_state",None); state=getter(session_id) if callable(getter) else {}
        return dict((state or {}).get("task") or {})
    def crystallize(self,session_id,prompt,authority="think"):
        previous=self.task_state(session_id); task=crystallize_task_state(prompt,previous,authority)
        if task is previous or task is None: return previous
        getter=getattr(self.db,"get_session_operating_state",None); current=getter(session_id) if callable(getter) else {}
        state=dict(current or {}); state["task"]=task
        setter=getattr(self.db,"set_session_operating_state",None)
        if callable(setter): setter(session_id,state)
        return task
