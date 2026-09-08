"""Application-level AI product semantics.

This module owns task-mode capability/readiness and common prompt normalization.
It deliberately does not own provider routing or presentation state.
"""
from __future__ import annotations

from dataclasses import dataclass

from core.skills_manager import SkillsManager


MODE_INSTRUCTIONS = {
    "coding": (
        "Produce implementation-focused work. Make requirements explicit; cover interfaces, "
        "data/persistence where relevant, failure handling, security implications, migration, "
        "tests, and concrete code or pseudocode when useful."
    ),
    "research": (
        "Produce evidence-oriented research. Separate observations from inference, identify "
        "uncertainty, cross-check material claims, surface contradictions, and preserve source "
        "or evidence requirements from the task."
    ),
    "thinking": (
        "Produce careful reasoning/planning. Define the problem and constraints, compare viable "
        "options and trade-offs, test assumptions, and end with an actionable recommendation."
    ),
}

DEFAULT_PROVIDER_CAPABILITIES = {
    "gemini": {"coding", "research", "thinking"},
    "groq": {"coding", "research", "thinking"},
    "cloudflare": {"coding", "thinking"},
    "openrouter": {"coding", "research", "thinking"},
    "huggingface": {"coding", "thinking"},
    "deepseek": {"coding", "research", "thinking"},
    "coze": {"research", "thinking"},
}

# Stable ordering is a recommendation policy, not a fallback route.
RECOMMENDATION_ORDER = {
    "coding": ("groq", "openrouter", "gemini", "deepseek", "cloudflare", "huggingface"),
    "research": ("gemini", "openrouter", "groq", "deepseek", "coze"),
    "thinking": ("gemini", "groq", "openrouter", "cloudflare", "deepseek", "huggingface", "coze"),
}


@dataclass(frozen=True)
class CapabilityState:
    participant_id: str
    mode: str
    configured: bool
    capable: bool
    ready: bool
    reason: str

    def as_dict(self):
        return {
            "participant_id": self.participant_id,
            "mode": self.mode,
            "configured": self.configured,
            "capable": self.capable,
            "ready": self.ready,
            "reason": self.reason,
        }


class CapabilityRegistry:
    """Deterministic capability/readiness registry for configured participants."""

    def __init__(self, capabilities=None, recommendation_order=None):
        self.capabilities = {
            key: set(value) for key, value in (capabilities or DEFAULT_PROVIDER_CAPABILITIES).items()
        }
        self.recommendation_order = recommendation_order or RECOMMENDATION_ORDER

    @staticmethod
    def normalize_mode(mode):
        normalized = str(mode or "thinking").strip().lower()
        return normalized if normalized in MODE_INSTRUCTIONS else "thinking"

    def evaluate(self, mode, configured_agents):
        mode = self.normalize_mode(mode)
        configured_agents = configured_agents or {}
        names = list(dict.fromkeys(list(self.capabilities) + list(configured_agents)))
        states = []
        for name in names:
            configured = configured_agents.get(name) is not None
            capable = mode in self.capabilities.get(name, set())
            ready = configured and capable
            reason = "ready" if ready else ("not_configured" if not configured else "mode_not_supported")
            states.append(CapabilityState(name, mode, configured, capable, ready, reason))
        return states

    def recommended(self, mode, configured_agents):
        mode = self.normalize_mode(mode)
        ready = {state.participant_id for state in self.evaluate(mode, configured_agents) if state.ready}
        return [name for name in self.recommendation_order.get(mode, ()) if name in ready]


class PromptNormalizer:
    """Build one common task specification shared by every participant."""

    def __init__(self, skills_manager=None):
        self.skills_manager = skills_manager or SkillsManager()

    def normalize(self, raw_prompt, mode, prompt_style="default"):
        raw_prompt = str(raw_prompt or "")
        mode = CapabilityRegistry.normalize_mode(mode)
        style = str(prompt_style or "default").strip() or "default"
        skill_text = self.skills_manager.get_skill(style) if style != "default" else ""

        sections = [
            "MULTIMIND COMMON TASK SPECIFICATION",
            f"TASK MODE: {mode.upper()}",
            f"MODE CONTRACT: {MODE_INSTRUCTIONS[mode]}",
        ]
        if skill_text:
            sections.extend([f"PROMPT STYLE: {style}", skill_text.strip()])
        else:
            sections.append("PROMPT STYLE: default")
        sections.extend([
            "USER TASK (preserve intent and literal constraints):",
            raw_prompt,
        ])
        return {
            "raw_prompt": raw_prompt,
            "normalized_prompt": "\n\n".join(sections),
            "mode": mode,
            "prompt_style": style,
            "style_applied": bool(skill_text),
        }
