"""Adversarial resource-boundary checks for deliberation utility routing."""

from core.debate import DebateOrchestrator
from providers.base import BaseProvider


class RecordingProvider(BaseProvider):
    def __init__(self, name, text):
        super().__init__(name)
        self.model_name = f"{name}-model"
        self.text = text
        self.calls = []

    def generate(self, prompt, system_prompt=None, mode="thinking", max_tokens=4096, **kwargs):
        self.calls.append(prompt)
        return {
            "status": "success",
            "text": self.text,
            "agent": self.model_name,
            "tokens": 5,
            "cost": 0.0,
        }


def test_unselected_configured_provider_is_never_used_by_judge_fallback():
    selected = RecordingProvider(
        "groq",
        "Groq candidate with enough useful detail to remain a valid fallback answer.",
    )
    unselected_paid = RecordingProvider(
        "deepseek",
        "This configured paid provider must never be called when it was not selected.",
    )

    log = DebateOrchestrator(
        gemini_agent=None,
        groq_agent=selected,
        deepseek_agent=unselected_paid,
    ).debate(
        "Analyze this resource boundary",
        agents=["groq"],
        mode="thinking",
        rounds=1,
    )

    assert log["status"] == "success"
    assert log["judge"]["eligible_providers"] == ["groq"]
    assert unselected_paid.calls == []
    # Groq is called once as participant and once as judge utility because it was
    # explicitly selected and successfully participated.
    assert len(selected.calls) == 2


def test_selected_gemini_can_be_preferred_for_judge_without_hidden_provider_use():
    groq = RecordingProvider("groq", "Groq participant answer with useful detail.")
    gemini = RecordingProvider(
        "gemini",
        "WINNER: participant-1-groq\nFINAL:\nGemini judge synthesis over the explicitly selected panel.",
    )
    hidden = RecordingProvider("deepseek", "must not run")

    log = DebateOrchestrator(
        gemini_agent=gemini,
        groq_agent=groq,
        deepseek_agent=hidden,
    ).debate(
        "Analyze",
        agents=["groq", "gemini"],
        mode="thinking",
        rounds=1,
    )

    assert log["judge"]["eligible_providers"] == ["gemini", "groq"]
    assert "gemini" in log["judge"]["actual_provider"].lower()
    assert hidden.calls == []
