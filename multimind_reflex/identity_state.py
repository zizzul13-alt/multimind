"""Reflex state extension that exposes AI identities instead of provider brands."""
from __future__ import annotations

import reflex as rx

from core.ai_identity import AI_IDENTITIES
from multimind_reflex.verdict_state import VerdictHostState


class IdentityVerdictHostState(VerdictHostState):
    """Keep provider routing behind the application boundary."""

    active_agents: list[str] = ["gemini"]

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
