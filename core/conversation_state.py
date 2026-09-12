"""Conversation retrieval and task checkpoints using existing database contracts."""
from __future__ import annotations

import json

from core.operating_model import (
    crystallize_task_state,
    format_retrieved_context,
    retrieve_relevant_chats,
)


class ConversationStateService:
    def __init__(self, database):
        self.db = database

    def _sessions(self):
        getter = getattr(self.db, "get_sessions", None)
        if not callable(getter):
            return []
        try:
            rows = getter()
        except Exception:
            return []
        return rows if isinstance(rows, (list, tuple)) else []

    def _chat_rows(self, session_id, limit=50):
        getter = getattr(self.db, "get_session_chats", None)
        if not callable(getter):
            return []
        try:
            rows = getter(session_id, limit=limit)
        except Exception:
            return []
        return list(rows) if isinstance(rows, (list, tuple)) else []

    def retrieve(self, session_id, query, limit=6):
        rows = []
        for session in self._sessions():
            if not isinstance(session, dict):
                continue
            sid = session.get("id")
            if not sid:
                continue
            for row in self._chat_rows(sid, limit=50):
                if not isinstance(row, dict):
                    continue
                item = dict(row)
                item.setdefault("session_id", sid)
                rows.append(item)
        return retrieve_relevant_chats(rows, query, limit=limit)

    def context(self, session_id, query, limit=6):
        return format_retrieved_context(self.retrieve(session_id, query, limit))

    def task_state(self, session_id):
        rows = self._chat_rows(session_id, limit=50)
        for row in reversed(rows):
            if not isinstance(row, dict):
                continue
            raw = row.get("debate_data") or "{}"
            try:
                data = json.loads(raw) if isinstance(raw, str) else dict(raw)
            except (TypeError, ValueError):
                continue
            task = (data.get("product_semantics") or {}).get("task_state")
            if isinstance(task, dict) and task:
                return dict(task)
        return {}

    def crystallize(self, session_id, prompt, authority="think"):
        return crystallize_task_state(
            prompt,
            self.task_state(session_id),
            authority,
        ) or {}

    def persist_checkpoint(self, session_id, chat_id, debate_data):
        """Persist and read back one operating-model checkpoint.

        Persistence success means more than issuing an UPDATE: the exact
        session-scoped chat must be readable afterwards and contain the same
        product-semantics checkpoint. This stays inside the existing durable
        chat JSON contract, so backup/restore and user isolation remain owned by
        the existing database adapter.
        """
        updater = getattr(self.db, "update_chat_debate_data", None)
        getter = getattr(self.db, "get_chat", None)
        if not callable(updater) or not callable(getter):
            return False
        try:
            encoded = json.dumps(debate_data)
            if updater(session_id, chat_id, encoded) is not True:
                return False
            row = getter(session_id, chat_id)
            if not isinstance(row, dict):
                return False
            raw = row.get("debate_data") or "{}"
            persisted = json.loads(raw) if isinstance(raw, str) else dict(raw)
        except (TypeError, ValueError, OSError):
            return False
        expected = (debate_data.get("product_semantics") or {})
        actual = (persisted.get("product_semantics") or {})
        return bool(expected) and actual == expected
