"""Conversation-first application extension over the accepted identity boundary."""
from __future__ import annotations

from dataclasses import dataclass

from core.ai_identity import available_identity_options
from core.application import ChatRequest
from core.conversation_state import ConversationStateService
from core.identity_application import IdentityFirstApplication
from core.operating_model import normalize_authority, select_auto_identities, select_work_mode


@dataclass
class OperatingChatRequest(ChatRequest):
    work_mode_policy: str = "manual"
    ai_selection_policy: str = "manual"
    authority: str = "think"
    auto_ai_count: int = 1


class _RetrievalMemory:
    def __init__(self, base, retrieved):
        self.base = base
        self.retrieved = retrieved

    def add_chat(self, prompt, response):
        if self.base is not None and hasattr(self.base, "add_chat"):
            self.base.add_chat(prompt, response)

    def get_context(self):
        current = (
            self.base.get_context()
            if self.base is not None and hasattr(self.base, "get_context")
            else ""
        )
        parts = [
            part
            for part in (
                current,
                f"RETRIEVED RELEVANT HISTORY:\n{self.retrieved}"
                if self.retrieved
                else "",
            )
            if part
        ]
        return "\n\n".join(parts)


class ConversationFirstApplication(IdentityFirstApplication):
    """Resolve Auto/Manual axes without changing user authority or provider truth."""

    def execute_chat(self, request: ChatRequest):
        # Existing hosts and compatibility seams use the accepted ChatRequest
        # contract. Keep that path behaviour-compatible: conversation retrieval
        # and checkpoints are opt-in through OperatingChatRequest.
        if not isinstance(request, OperatingChatRequest):
            return super().execute_chat(request)

        mode_policy = str(request.work_mode_policy or "manual")
        mode_selection = select_work_mode(
            request.original_prompt,
            request.session_mode,
            mode_policy,
        )
        ai_policy = str(request.ai_selection_policy or "manual").lower()
        authority = normalize_authority(request.authority)
        explicit = list(dict.fromkeys(request.active_agents or []))
        available = available_identity_options(self.agents)

        if ai_policy == "auto":
            count = max(1, min(6, int(request.auto_ai_count or 1)))
            selected = select_auto_identities(
                mode_selection["selected"],
                available,
                count=count,
            )
        else:
            selected = explicit

        routed = ChatRequest(
            original_prompt=request.original_prompt,
            uploads=request.uploads,
            context_mode=request.context_mode,
            session_id=request.session_id,
            session_mode=mode_selection["selected"],
            compressor_enabled=request.compressor_enabled,
            active_agents=selected,
            debate_rounds=request.debate_rounds,
            selected_skill=request.selected_skill,
        )

        database = self._database()
        service = ConversationStateService(database)
        task_state = {}
        retrieved = ""
        original_memory = None
        if request.session_id:
            task_state = service.crystallize(
                request.session_id,
                request.original_prompt,
                authority,
            )
            retrieved = service.context(
                request.session_id,
                request.original_prompt,
                limit=6,
            )
            original_memory = self.runtime_memories.get(request.session_id)
            if request.context_mode == "continue" and retrieved:
                self.runtime_memories[request.session_id] = _RetrievalMemory(
                    original_memory,
                    retrieved,
                )

        try:
            result = super().execute_chat(routed)
        finally:
            if request.session_id and retrieved:
                if original_memory is None:
                    self.runtime_memories.pop(request.session_id, None)
                else:
                    self.runtime_memories[request.session_id] = original_memory

        operating = {
            "work_mode": mode_selection,
            "ai_selection": {
                "policy": "auto" if ai_policy == "auto" else "manual",
                "requested": explicit,
                "available": available,
                "selected": selected,
                "reason": (
                    "eligible_runtime_inventory"
                    if ai_policy == "auto"
                    else "manual_override"
                ),
            },
            "authority": authority,
            "task_state": task_state,
            "retrieval": {
                "applied": bool(retrieved),
                "context_chars": len(retrieved),
            },
        }
        result.debate_data.setdefault("product_semantics", {}).update(operating)

        if result.persisted and result.chat_id and request.session_id:
            if not service.persist_checkpoint(
                request.session_id,
                result.chat_id,
                result.debate_data,
            ):
                result.warnings.append(
                    "Operating-model checkpoint could not be durably verified."
                )
        return result
