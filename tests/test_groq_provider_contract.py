from providers.groq import GroqProvider
from providers.model_registry import resolve_model


def test_groq_provider_owns_protocol_not_permanent_model_choice(monkeypatch):
    captured={}
    class FakeClient:
        def __init__(self,**kwargs): captured.update(kwargs)
    monkeypatch.setattr("providers.groq.OpenAI",FakeClient)
    provider=GroqProvider("sentinel-not-a-real-key")
    assert captured["base_url"]=="https://api.groq.com/openai/v1"
    assert captured["max_retries"]==0
    assert provider.model_name=="Groq (dynamic model)"
    assert not hasattr(GroqProvider,"MODEL")
    fallback=resolve_model("groq","coding")
    assert fallback.provider=="groq"
    assert fallback.model_id=="openai/gpt-oss-20b"
    assert fallback.source=="registry_fallback"
