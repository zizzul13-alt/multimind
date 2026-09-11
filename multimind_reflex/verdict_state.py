"""Reflex projection/actions for persistent human deliberation verdicts.

This state adds no business truth. It delegates validation and persistence to
``MultiMindApplication.set_user_verdict`` and then refreshes the persisted history.
"""
from __future__ import annotations

import reflex as rx

from multimind_reflex.deliberation_projection import run_summary
from multimind_reflex.workspace_dna_state import WorkspaceDnaState


class VerdictHostState(WorkspaceDnaState):
    """Small presentation extension for the independent user-winner signal."""

    current_user_verdict: str = ""

    def _clear_deliberation_projection(self):
        super()._clear_deliberation_projection()
        self.current_user_verdict = ""

    def _set_deliberation_projection(self, debate_data):
        super()._set_deliberation_projection(debate_data)
        self.current_user_verdict = run_summary(debate_data)["user_verdict"]

    @rx.event
    def set_current_user_verdict(self, participant_id: str):
        if self.busy:
            self.error_message = "Finish the active run before recording a verdict."
            return
        if not self.current_session_id or not self.history:
            self.error_message = "No persisted deliberation is available for a verdict."
            return

        latest = self.history[-1]
        chat_id = str(latest.get("id", ""))
        if not chat_id:
            self.error_message = "The latest persisted chat could not be identified."
            return

        result = self._application().set_user_verdict(
            self.current_session_id,
            chat_id,
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
