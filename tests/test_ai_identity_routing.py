from providers.base import BaseProvider
from core.application import ChatRequest
from core.identity_application import IdentityFirstApplication
from core.ai_identity import AI_IDENTITY_OPTIONS, infer_ai_identity


class FakeProvider(BaseProvider):
    def __init__(self, name, *, model, family, status="success"):
        super().__init__(name)
        self.model_name = model
        self.model = model
        self.family = family
        self.status = status
        self.calls = 0

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096, **kwargs):
        self.calls += 1
        if self.status != "success":
            return self.failure_response("forced_failure")
        return {
            "status": "success",
            "text": f"answer from {self.name}",
            "agent": self.name,
            "tokens": 10,
            "cost": 0.0,
            "actual_model": self.model,
            "resolved_model": self.model,
            "model_family": self.family,
        }


def _app(**agents):
    return IdentityFirstApplication(agents=agents)


def _run(app, identities, rounds=1):
    return app.execute_chat(
        ChatRequest(
            original_prompt="test task",
            session_mode="thinking",
            active_agents=list(identities),
            debate_rounds=rounds,
        )
    )


def test_primary_identity_route_preserves_ai_and_route_truth():
    app = _app(gemini=FakeProvider("google-route", model="gemini-2.5-flash", family="gemini"))
    result = _run(app, ["gemini"])

    assert result.status == "success"
    participant = result.debate_data["participants"][0]
    assert participant["requested_identity"] == "gemini"
    assert participant["effective_identity"] == "gemini"
    assert participant["route_provider"] == "gemini"
    assert participant["identity_route_fallback"] is False
    assert "google-route" not in participant["effective_identity"]


def test_same_identity_route_fallback_keeps_identity_and_records_actual_route():
    groq = FakeProvider("groq-route", model="openai/gpt-oss-20b", family="gpt-oss", status="error")
    hf = FakeProvider("hf-route", model="openai/gpt-oss-20b:cheapest", family="gpt-oss")
    app = _app(groq=groq, huggingface=hf)

    result = _run(app, ["gpt-oss"])
    participant = result.debate_data["participants"][0]

    assert result.status == "success"
    assert participant["requested_identity"] == "gpt-oss"
    assert participant["effective_identity"] == "gpt-oss"
    assert participant["route_provider"] == "huggingface"
    assert participant["identity_route_fallback"] is True
    assert participant["identity_fallback_reason"] == "same_identity_route_failure"
    assert groq.calls >= 1
    assert hf.calls >= 1


def test_identity_mismatch_is_rejected_instead_of_cosplay():
    impostor = FakeProvider("groq-route", model="anthropic/claude-sonnet", family="claude")
    app = _app(groq=impostor)

    result = _run(app, ["gpt-oss"])
    participant = result.debate_data["participants"][0]

    assert result.status == "error"
    assert participant["status"] == "error"
    assert participant["requested_identity"] == "gpt-oss"
    assert participant["effective_identity"] == ""
    assert participant["failure_category"] == "identity_unavailable"


def test_cross_identity_fallback_is_disabled_by_current_deliberation_policy():
    failed_gpt = FakeProvider("groq-route", model="openai/gpt-oss-20b", family="gpt-oss", status="error")
    available_gemini = FakeProvider("google-route", model="gemini-2.5-flash", family="gemini")
    app = _app(groq=failed_gpt, gemini=available_gemini)

    result = _run(app, ["gpt-oss"])

    assert result.status == "error"
    assert available_gemini.calls == 0
    assert result.debate_data["identity_routing"]["cross_identity_fallback"] == "disabled"


def test_multi_ai_debate_preserves_each_identity_separately_from_route():
    app = _app(
        gemini=FakeProvider("google-route", model="gemini-2.5-flash", family="gemini"),
        groq=FakeProvider("groq-route", model="openai/gpt-oss-20b", family="gpt-oss"),
        cloudflare=FakeProvider("cf-route", model="@cf/meta/llama-3.1-8b-instruct-fp8", family="llama"),
    )

    result = _run(app, ["gemini", "gpt-oss", "llama"])
    participants = result.debate_data["participants"]

    assert result.status == "success"
    assert [item["requested_identity"] for item in participants] == ["gemini", "gpt-oss", "llama"]
    assert [item["effective_identity"] for item in participants] == ["gemini", "gpt-oss", "llama"]
    assert [item["route_provider"] for item in participants] == ["gemini", "groq", "cloudflare"]


def test_primary_identity_catalog_contains_no_gateway_brands():
    assert set(AI_IDENTITY_OPTIONS) == {"gemini", "gpt-oss", "llama", "deepseek"}
    assert "openrouter" not in AI_IDENTITY_OPTIONS
    assert "cloudflare" not in AI_IDENTITY_OPTIONS
    assert "groq" not in AI_IDENTITY_OPTIONS
    assert "huggingface" not in AI_IDENTITY_OPTIONS


def test_future_identity_inference_is_truthful_but_does_not_imply_route_support():
    assert infer_ai_identity(model_id="anthropic/claude-sonnet-4") == "claude"
    assert infer_ai_identity(model_id="qwen/qwen3-32b") == "qwen"
    assert infer_ai_identity(model_id="moonshot/kimi-k2") == "kimi"
    assert infer_ai_identity(model_id="unknown/router-random") is None
