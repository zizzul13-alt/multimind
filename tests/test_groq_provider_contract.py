from providers.groq import GroqProvider


def test_groq_provider_uses_current_production_smoke_model(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr("providers.groq.OpenAI", FakeClient)

    provider = GroqProvider("sentinel-not-a-real-key")

    assert captured["base_url"] == "https://api.groq.com/openai/v1"
    assert captured["max_retries"] == 0
    assert provider.model == "openai/gpt-oss-20b"
    assert provider.model_name == "Groq (GPT-OSS 20B)"
