import time
import requests
from providers.base import BaseProvider
from utils.config import Config


class HuggingFaceProvider(BaseProvider):
    """Hugging Face Inference Providers chat-completion adapter."""

    ENDPOINT = "https://router.huggingface.co/v1/chat/completions"
    # Let HF select the cheapest currently available provider for this supported
    # chat model. This avoids binding MultiMind to a legacy serverless endpoint.
    MODEL = "openai/gpt-oss-20b:cheapest"

    def __init__(self, api_key: str):
        super().__init__("HuggingFace")
        if not api_key:
            self.api_key = None
            self.model_name = "HuggingFace (not configured)"
            self.set_availability(False, "API key not configured")
            return
        self.api_key = api_key
        self.model_name = "HuggingFace (Inference Providers)"
        self.set_availability(True)

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 2048, **kwargs) -> dict:
        if not self.api_key:
            return self.failure_response("not_configured")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": self.MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        for attempt in range(3):
            try:
                response = requests.post(self.ENDPOINT, headers=headers, json=payload, timeout=Config.API_TIMEOUT)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        text = data["choices"][0]["message"]["content"]
                    except (ValueError, KeyError, IndexError, TypeError):
                        self.set_availability(False, "Malformed response")
                        return self.failure_response("malformed_response")
                    if not isinstance(text, str) or not text.strip():
                        self.set_availability(False, "Empty response")
                        return self.failure_response("empty_response")
                    usage = data.get("usage", {}) if isinstance(data, dict) else {}
                    self.set_availability(True)
                    return {"status": "success", "text": text, "agent": f"HuggingFace ({self.MODEL})", "tokens": usage.get("total_tokens", 0), "cost": 0.0}
                if response.status_code in {429, 500, 502, 503, 504}:
                    if attempt < 2:
                        time.sleep(2)
                        continue
                    self.set_availability(False, f"HTTP {response.status_code}")
                    return self.failure_response("retry_exhausted", status_code=response.status_code)
                self.set_availability(False, f"HTTP {response.status_code}")
                return self.failure_response("http_status", status_code=response.status_code)
            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                    continue
                self.set_availability(False, type(e).__name__)
                return self.failure_response("network_or_sdk_exception", exception_type=type(e).__name__)
        return self.failure_response("retry_exhausted")
