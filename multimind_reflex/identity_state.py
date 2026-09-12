"""Reflex projection for AI identities and independent Auto/Manual selectors."""
from __future__ import annotations

import reflex as rx

from core.ai_identity import AI_IDENTITIES
from multimind_reflex.verdict_state import VerdictHostState


class IdentityVerdictHostState(VerdictHostState):
    """Keep work-mode policy independent from AI/model selection policy."""

    work_mode_policy: str = "manual"
    ai_selection_policy: str = "manual"
    auto_ai_count: int = 1

    @rx.event
    def set_work_mode_policy(self, value: str):
        self.work_mode_policy = (
            "auto" if str(value).lower() in {"auto", "lazy"} else "manual"
        )

    @rx.event
    def set_ai_selection_policy(self, value: str):
        self.ai_selection_policy = "auto" if str(value).lower() == "auto" else "manual"

    @rx.event
    def set_auto_ai_count(self, value: str):
        try:
            self.auto_ai_count = max(1, min(6, int(value)))
        except (TypeError, ValueError):
            self.auto_ai_count = 1

    @rx.event
    def set_agent_enabled(self, agent: str, enabled: bool):
        if agent not in AI_IDENTITIES:
            return
        selected = list(self.active_agents)
        if enabled and agent not in selected:
            selected.append(agent)
        elif not enabled and agent in selected:
            selected.remove(agent)
        self.active_agents = selected or ["gemini"]
        self._refresh_estimate()
