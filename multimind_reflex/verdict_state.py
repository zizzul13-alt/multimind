"""Reflex projection/actions for persistent human deliberation verdicts.

This state adds no business truth. It delegates validation and persistence to
``MultiMindApplication.set_user_verdict`` and then refreshes persisted history.
The active verdict target is the exact ``ChatResult.chat_id`` returned by the
application, never an inferred "latest" history row.
"""
from __future__ import annotations

import asyncio

import reflex as rx

from core.application import ChatRequest
from multimind_reflex.bridge import BufferedUpload, build_host_application
from multimind_reflex.deliberation_projection import history_snapshots, run_summary
from multimind_reflex.workspace_signature_state import WorkspaceSignatureState


class VerdictHostState(WorkspaceSignatureState):
    """Presentation extension for independent, persisted human judgment."""

    current_user_verdict: str = ""
    current_chat_id: str = ""

    def _clear_deliberation_projection(self):
        super()._clear_deliberation_projection()
        self.current_user_verdict = ""
        self.current_chat_id = ""

    def _set_deliberation_projection(self, debate_data):
        super()._set_deliberation_projection(debate_data)
        self.current_user_verdict = run_summary(debate_data)["user_verdict"]

    @rx.event
    def set_current_user_verdict(self, participant_id: str):
        if self.busy:
            self.error_message = "Finish the active run before recording a verdict."
            return
        if not self.current_session_id or not self.current_chat_id:
            self.error_message = "No persisted deliberation is available for a verdict."
            return

        result = self._application().set_user_verdict(
            self.current_session_id,
            self.current_chat_id,
            participant_id,
        )
        if result.status != "success":
            messages = {
                "invalid_participant": "Only a successful participant can be selected as your winner.",
                "chat_not_found": "The persisted chat could not be found.",
                "invalid_debate_data": "The saved deliberation record is invalid.",
                "persistence_failed": "Your verdict could not be saved. Please try again.",
            }
            self.error_message = messages.get(result.status, "Your verdict could not be saved.")
            return

        self.current_user_verdict = result.user_verdict
        self.error_message = ""
        self.success_message = (
            f"Your winner: {result.user_verdict}"
            if result.user_verdict
            else "Your winner selection was cleared."
        )
        self._refresh_history()

    @rx.event
    def clear_current_user_verdict(self):
        self.set_current_user_verdict("")

    @rx.event(background=True)
    async def run_chat(self):
        """Run the accepted app path while retaining the exact persisted chat id."""
        async with self:
            if self.busy:
                return
            if not self.logged_in:
                self.error_message = "Login required."
                return
            if not self.current_session_id:
                self.error_message = "Select or create a session first."
                return
            prompt = self.prompt.strip()
            if not prompt and not self._pending_uploads:
                self.error_message = "Enter a prompt or stage at least one file."
                return
            if not self.active_agents:
                self.error_message = "Select at least one agent."
                return

            self.busy = True
            self.status_message = "Running…"
            self.error_message = ""
            self.success_message = ""
            self.final_answer = ""
            self._clear_deliberation_projection()
            self.warnings = []

            user_id = self.user_id
            session_id = self.current_session_id
            session_mode = self.current_session_mode
            runtime_memories = self._runtime_memories
            staged_uploads = [dict(item) for item in self._pending_uploads]
            request = ChatRequest(
                original_prompt=prompt,
                uploads=[BufferedUpload(item["name"], item["data"]) for item in staged_uploads],
                context_mode=self.context_mode,
                session_id=session_id,
                session_mode=session_mode,
                compressor_enabled=self.compressor_enabled,
                active_agents=list(self.active_agents),
                debate_rounds=self.debate_rounds,
                selected_skill=self.selected_skill,
            )

        try:
            application = build_host_application(user_id, runtime_memories)
            result = await asyncio.to_thread(application.execute_chat, request)
            history = await asyncio.to_thread(application.get_session_chats, session_id, 50)
        except Exception:
            result = None
            history = None

        async with self:
            self.busy = False
            self.status_message = ""
            if result is None:
                self.error_message = "Chat execution failed. Please try again."
                return

            self.warnings = list(result.warnings)
            self._set_deliberation_projection(result.debate_data)
            if result.status != "success":
                self.error_message = "No usable provider response was returned."
                return

            if not result.persisted or not result.chat_id:
                self.error_message = "The response was not durably persisted; no verdict target is available."
                self.current_chat_id = ""
                return

            self.current_chat_id = result.chat_id
            self.final_answer = result.final_answer
            self.history = history_snapshots(history or [])
            self.prompt = ""
            self._pending_uploads = []
            self.upload_names = []
            self.success_message = "Response saved to session history."
            self._refresh_estimate()
