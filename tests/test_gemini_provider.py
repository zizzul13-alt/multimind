"""Gemini SDK and vision adapter behavior."""
from io import BytesIO
from types import SimpleNamespace

from providers.gemini import GeminiProvider


class Upload(BytesIO):
    def __init__(self, name, data):
        super().__init__(data)
        self.name = name


def _provider_with_response(response):
    provider = GeminiProvider("")
    provider.model_name = "gemini-test"
    provider.client = SimpleNamespace(
        models=SimpleNamespace(generate_content=lambda **_kwargs: response)
    )
    return provider


def test_provider_constructs_google_genai_client_with_injected_key(monkeypatch):
    captured = {}

    class Client:
        def __init__(self, *, api_key):
            captured["api_key"] = api_key

    monkeypatch.setattr("providers.gemini.genai.Client", Client)

    provider = GeminiProvider("injected-key")

    assert captured == {"api_key": "injected-key"}
    assert provider.client is not None


def test_analyze_image_uses_provider_client_and_preserves_file_position():
    captured = {}
    provider = _provider_with_response(SimpleNamespace(text="visible text"))
    provider.client.models.generate_content = lambda **kwargs: captured.update(kwargs) or SimpleNamespace(text="visible text")
    upload = Upload("photo.png", b"png bytes")
    upload.seek(2)

    result = provider.analyze_image(upload)

    assert result["status"] == "success"
    assert result["text"] == "visible text"
    assert upload.tell() == 2
    assert captured["model"] == "gemini-test"
    assert captured["contents"][1].inline_data.mime_type == "image/png"


def test_analyze_image_normalizes_sdk_failure_without_leaking_details():
    provider = _provider_with_response(SimpleNamespace(text=""))

    result = provider.analyze_image(Upload("photo.png", b"png bytes"))

    assert result["status"] == "error"
    assert result["failure_category"] == "empty_response"


def test_analyze_image_sanitizes_sdk_exception():
    provider = _provider_with_response(SimpleNamespace(text="unused"))
    provider.client.models.generate_content = lambda **_kwargs: (_ for _ in ()).throw(
        RuntimeError("provider internal path /secret")
    )

    result = provider.analyze_image(Upload("photo.png", b"png bytes"))

    assert result["status"] == "error"
    assert result["failure_category"] == "network_or_sdk_exception"
    assert "secret" not in result["text"]
