from agents.router import ModelRouter
from agents.unified_agent import UnifiedAgent
from providers.base import BaseProvider
from providers.cloudflare import CloudflareProvider
from providers.deepseek import DeepSeekProvider
from providers.groq import GroqProvider
from providers.huggingface import HuggingFaceProvider


def test_current_provider_model_contracts_do_not_use_known_retired_ids():
    assert GroqProvider.MODEL == "openai/gpt-oss-20b"
    assert DeepSeekProvider.MODEL == "deepseek-v4-flash"
    assert CloudflareProvider.MODEL == "@cf/meta/llama-3.1-8b-instruct-fp8"
    assert HuggingFaceProvider.ENDPOINT == "https://router.huggingface.co/v1/chat/completions"
    assert "api-inference.huggingface.co" not in HuggingFaceProvider.ENDPOINT


def test_cloudflare_requires_account_id_as_well_as_key():
    provider = CloudflareProvider("key", "")
    assert provider.is_available is False
    assert provider.generate("prompt")["failure_category"] == "not_configured"


def test_router_uses_sanitized_status_code_for_rate_limit_and_falls_back():
    class Limited(BaseProvider):
        def __init__(self):
            super().__init__("Limited")
        def generate(self, **_kwargs):
            return self.failure_response("http_status", status_code=429)

    class Healthy(BaseProvider):
        def __init__(self):
            super().__init__("Healthy")
        def generate(self, **_kwargs):
            return {"status": "success", "text": "ok", "agent": "Healthy", "tokens": 1, "cost": 0.0}

    limited = Limited()
    result = ModelRouter([limited, Healthy()]).generate("prompt")
    assert result["status"] == "success"
    assert result["agent"] == "Healthy"
    assert limited.is_available is False


def test_unified_priority_starts_with_gemini_when_configured(monkeypatch):
    class Stub:
        def __init__(self, *_args, **_kwargs):
            pass
    monkeypatch.setattr("agents.unified_agent.GeminiAgent", Stub)
    monkeypatch.setattr("agents.unified_agent.GroqAgent", Stub)
    unified = UnifiedAgent({"gemini_key": "g", "groq_key": "q"})
    assert [item["name"] for item in unified.providers][:2] == ["🔍 Gemini", "⚡ Groq"]
