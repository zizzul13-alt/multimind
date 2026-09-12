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
            self.error_message = "No active deliberation result to judge."
            return
        application = build_host_application(self.username)
        try:
            application.set_user_verdict(
                self.current_session_id,
                self.current_chat_id,
                participant_id,
            )
        except Exception as exc:
            self.error_message = str(exc)
            return
        self.current_user_verdict = participant_id
        self.history = history_snapshots(application.get_session_history(self.current_session_id))
        self.success_message = "Your independent winner was saved."
        self.error_message = ""

    @rx.event
    def clear_current_user_verdict(self):
        if self.busy:
            self.error_message = "Finish the active run before clearing a verdict."
            return
        if not self.current_session_id or not self.current_chat_id:
            self.error_message = "No active deliberation result to judge."
            return
        application = build_host_application(self.username)
        try:
            application.set_user_verdict(
                self.current_session_id,
                self.current_chat_id,
                None,
            )
        except Exception as exc:
            self.error_message = str(exc)
            return
        self.current_user_verdict = ""
        self.history = history_snapshots(application.get_session_history(self.current_session_id))
        self.success_message = "Your independent winner was cleared."
        self.error_message = ""

    @rx.event(background=True)
    async def run_chat(self):
        async with self:
            if self.busy:
                return
            if not self.current_session_id:
                self.error_message = "Select a session first."
                return
            if not self.prompt.strip():
                self.error_message = "Prompt is required."
                return
            self.busy = True
            self.error_message = ""
            self.success_message = ""
            self.status_message = "Preparing request..."
            self.warnings = []
            self._clear_deliberation_projection()
            username = self.username
            session_id = self.current_session_id
            context_mode = self.context_mode
            agents = list(self.active_agents)
            prompt = self.prompt
            rounds = self.debate_rounds
            compressor_enabled = self.compressor_enabled
            attachments = [BufferedUpload(item.name, item.data) for item in self.staged_uploads]
            template_name = self.selected_template or None
            template_variables_json = self.template_variables_json
            selected_skill = self.selected_skill or None

        application = build_host_application(username)
        request = ChatRequest(
            session_id=session_id,
            prompt=prompt,
            context_mode=context_mode,
            agents=agents,
            debate_rounds=rounds,
            compressor_enabled=compressor_enabled,
            attachments=attachments,
            template_name=template_name,
            template_variables_json=template_variables_json,
            selected_skill=selected_skill,
        )

        try:
            result = await asyncio.to_thread(application.run_chat, request)
        except Exception as exc:
            async with self:
                self.busy = False
                self.status_message = ""
                self.error_message = str(exc)
            return

        async with self:
            self.busy = False
            self.status_message = "Done"
            self.warnings = list(result.warnings)
            self.final_answer = result.final_answer
            self._set_deliberation_projection(result.debate_data)
            self.current_chat_id = result.chat_id
            self.history = history_snapshots(application.get_session_history(session_id))
            self.prompt = ""
            self.staged_uploads = []
            self.success_message = "Run completed."


__all__ = ["VerdictHostState"]
