from core.application import ChatRequest, MultiMindApplication
from core.compressor import PromptCompressor
from core.product_semantics import CapabilityRegistry, PromptNormalizer


class Agent:
    def __init__(self, name, compressed=None, fail=False):
        self.name = name
        self.compressed = compressed
        self.fail = fail
        self.compress_calls = []

    def compress_prompt(self, prompt):
        self.compress_calls.append(prompt)
        if self.fail:
            raise RuntimeError("compression failed")
        text = self.compressed if self.compressed is not None else prompt
        return {"text": text, "original_tokens": 100, "compressed_tokens": 50}


class CapturingDebate:
    calls = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def debate(self, **kwargs):
        self.__class__.calls.append(kwargs)
        return {
            "status": "success", "final_answer": "ok", "responses": [],
            "participants": [], "total_tokens": 0, "total_cost": 0.0,
        }


def app(agents=None, registry=None):
    CapturingDebate.calls = []
    return MultiMindApplication(
        agents=agents or {}, runtime_memories={}, db=object(),
        debate_factory=CapturingDebate,
        capability_registry=registry,
    )


def test_modes_have_distinct_common_semantics():
    normalizer = PromptNormalizer()
    outputs = {
        mode: normalizer.normalize("build database", mode)["normalized_prompt"]
        for mode in ("coding", "research", "thinking")
    }
    assert len(set(outputs.values())) == 3
    assert "implementation-focused" in outputs["coding"]
    assert "evidence-oriented" in outputs["research"]
    assert "reasoning/planning" in outputs["thinking"]


def test_capability_registry_separates_ready_ineligible_and_unconfigured():
    registry = CapabilityRegistry(
        capabilities={"alpha": {"coding"}, "beta": {"research"}, "gamma": {"coding"}},
        recommendation_order={"coding": ("gamma", "alpha", "beta")},
    )
    agents = {"alpha": object(), "beta": object()}
    states = {s.participant_id: s for s in registry.evaluate("coding", agents)}
    assert states["alpha"].ready is True
    assert states["beta"].reason == "mode_not_supported"
    assert states["gamma"].reason == "not_configured"
    assert registry.recommended("coding", agents) == ["alpha"]


def test_mode_recommendation_never_overrides_explicit_roster():
    registry = CapabilityRegistry(
        capabilities={"alpha": {"coding"}, "beta": {"coding"}},
        recommendation_order={"coding": ("beta", "alpha")},
    )
    application = app({"alpha": object(), "beta": object()}, registry)
    result = application.execute_chat(ChatRequest(original_prompt="x", active_agents=["alpha"], session_mode="coding"))
    assert result.status == "success"
    assert CapturingDebate.calls[-1]["agents"] == ["alpha"]
    semantics = result.debate_data["product_semantics"]
    assert semantics["capability"]["recommended"] == ["beta", "alpha"]
    assert semantics["explicit_participants"] == ["alpha"]


def test_zero_explicit_participants_stays_zero():
    application = app({"gemini": object()})
    result = application.execute_chat(ChatRequest(original_prompt="x", active_agents=[]))
    assert CapturingDebate.calls[-1]["agents"] == []
    assert result.debate_data["product_semantics"]["explicit_participants"] == []


def test_prompt_style_is_common_normalization_not_provider_selection():
    application = app({"gemini": object(), "groq": object()})
    result = application.execute_chat(ChatRequest(
        original_prompt="review this", active_agents=["groq", "gemini"], selected_skill="code-reviewer"
    ))
    call = CapturingDebate.calls[-1]
    assert call["agents"] == ["groq", "gemini"]
    assert call["skill"] is None
    assert "CODE REVIEWER" in call["prompt"]
    assert result.debate_data["product_semantics"]["raw_prompt"] == "review this"


def test_compressor_uses_only_explicit_selected_utility():
    hidden = Agent("hidden", compressed="SHOULD NOT RUN")
    selected = Agent("selected")
    application = app({"gemini": hidden, "groq": selected})
    result = application.execute_chat(ChatRequest(
        original_prompt="word " * 20, active_agents=["groq"], compressor_enabled=True
    ))
    assert hidden.compress_calls == []
    assert len(selected.compress_calls) == 1
    assert result.debate_data["product_semantics"]["compressor"]["utility_provider"] == "groq"


def test_compressor_unavailable_degrades_without_hidden_provider():
    hidden = Agent("hidden")
    application = app({"gemini": hidden, "groq": object()})
    result = application.execute_chat(ChatRequest(
        original_prompt="word " * 20, active_agents=["groq"], compressor_enabled=True
    ))
    semantics = result.debate_data["product_semantics"]
    assert hidden.compress_calls == []
    assert semantics["compressor"]["applied"] is False
    assert semantics["compressor"]["fallback_reason"] == "utility_unavailable"
    assert semantics["effective_prompt"] == semantics["normalized_prompt"]


def test_compressor_failure_degrades_to_normalized_prompt():
    selected = Agent("selected", fail=True)
    application = app({"groq": selected})
    result = application.execute_chat(ChatRequest(
        original_prompt="word " * 20, active_agents=["groq"], compressor_enabled=True
    ))
    semantics = result.debate_data["product_semantics"]
    assert semantics["compressor"]["fallback_reason"] == "utility_failure"
    assert semantics["effective_prompt"] == semantics["normalized_prompt"]


def test_preservation_guard_rejects_loss_of_critical_literals():
    prompt = '''MUST keep src/app.py and error ERROR_TIMEOUT=504.\nUse 42%.\n```python\nraise ValueError("boom")\n```\nSOURCE: report.md'''
    lossy = Agent("utility", compressed="short summary")
    result = PromptCompressor.compress(prompt, lossy)
    assert result["applied"] is False
    assert result["fallback_reason"] == "preservation_guard"
    assert result["compressed"] == prompt


def test_preservation_guard_accepts_candidate_that_keeps_literals():
    prompt = "MUST keep config.yaml at /srv/app/config.yaml and status 503"
    candidate = "Shorter. MUST keep config.yaml at /srv/app/config.yaml and status 503"
    result = PromptCompressor.compress(prompt, Agent("utility", compressed=candidate))
    assert result["fallback_reason"] is None
    assert result["compressed"] == candidate


def test_product_semantics_metadata_attached_even_on_execution_error():
    class FailedDebate(CapturingDebate):
        def debate(self, **kwargs):
            return {"status": "error", "responses": [], "total_tokens": 0, "total_cost": 0}

    application = MultiMindApplication(agents={}, runtime_memories={}, db=object(), debate_factory=FailedDebate)
    result = application.execute_chat(ChatRequest(original_prompt="raw", active_agents=[]))
    assert result.status == "error"
    assert result.debate_data["product_semantics"]["raw_prompt"] == "raw"
