from pathlib import Path

from agents.router import ModelRouter
from agents.unified_agent import UnifiedAgent
from providers.base import BaseProvider
from providers.cloudflare import CloudflareProvider
from providers.huggingface import HuggingFaceProvider
from providers.model_registry import REGISTRY


def test_current_provider_registry_does_not_use_known_retired_ids():
    all_ids={item.model_id for candidates in REGISTRY.values() for item in candidates}
    assert "deepseek-chat" not in all_ids
    assert "deepseek-reasoner" not in all_ids
    assert "qwen/qwen3-coder:free" not in all_ids
    assert "nousresearch/hermes-3-llama-3.1-405b:free" not in all_ids
    assert "openrouter/free" in all_ids
    assert HuggingFaceProvider.ENDPOINT=="https://router.huggingface.co/v1/chat/completions"
    assert "api-inference.huggingface.co" not in HuggingFaceProvider.ENDPOINT


def test_openrouter_adapter_is_presentation_host_neutral():
    source=Path("providers/openrouter.py").read_text(encoding="utf-8")
    assert "multimind.streamlit.app" not in source
    assert "HTTP-Referer" not in source
    assert "qwen/qwen3-coder:free" not in source
    assert "llama-3.3-70b-instruct:free" not in source


def test_cloudflare_requires_account_id_as_well_as_key():
    provider=CloudflareProvider("key","")
    assert provider.is_available is False
    assert provider.generate("prompt")["failure_category"]=="not_configured"


def test_router_uses_sanitized_status_code_for_rate_limit_and_falls_back():
    class Limited(BaseProvider):
        def __init__(self): super().__init__("Limited")
        def generate(self,**_kwargs): return self.failure_response("http_status",status_code=429)
    class Healthy(BaseProvider):
        def __init__(self): super().__init__("Healthy")
        def generate(self,**_kwargs): return {"status":"success","text":"ok","agent":"Healthy","tokens":1,"cost":0.0}
    limited=Limited(); result=ModelRouter([limited,Healthy()]).generate("prompt")
    assert result["status"]=="success"; assert result["agent"]=="Healthy"; assert limited.is_available is False


def test_unified_priority_starts_with_gemini_when_configured(monkeypatch):
    class Stub:
        def __init__(self,*_args,**_kwargs): pass
    monkeypatch.setattr("agents.unified_agent.GeminiAgent",Stub)
    monkeypatch.setattr("agents.unified_agent.GroqAgent",Stub)
    unified=UnifiedAgent({"gemini_key":"g","groq_key":"q"})
    assert [item["name"] for item in unified.providers][:2]==["🔍 Gemini","⚡ Groq"]
