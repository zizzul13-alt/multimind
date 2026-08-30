import requests
import time
from providers.base import BaseProvider
from utils.token_counter import TokenCounter
from utils.config import Config

class HuggingFaceProvider(BaseProvider):
    """HuggingFace Inference API Provider"""

    def __init__(self, api_key: str):
        super().__init__("HuggingFace")
        if not api_key or api_key == "":
            self.api_key = None
            self.model_name = "HuggingFace (not configured)"
            self.set_availability(False, "API key not configured")
            return

        self.api_key = api_key
        self.models = {
            "coding": "Qwen/Qwen2.5-Coder-7B-Instruct",
            "research": "meta-llama/Llama-3.1-8B-Instruct",
            "thinking": "Qwen/Qwen3-4B-Thinking-2507",
            "quick": "mistralai/Mistral-7B-Instruct-v0.3"
        }
        self.model_name = "HuggingFace (Multi-Model)"
        self.set_availability(True)

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 2048, **kwargs) -> dict:
        if not self.api_key:
            return {
                "status": "error",
                "text": "HuggingFace not configured.",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
            }

        model = self.models.get(mode, self.models["quick"])

        for attempt in range(3):
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

                payload = {
                    "inputs": full_prompt[:1000],
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                }

                response = requests.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json=payload,
                    timeout=Config.API_TIMEOUT
                )

                if response.status_code == 200:
                    try:
                        result = response.json()
                    except ValueError:
                        self.set_availability(False, "Malformed response")
                        return self.failure_response("malformed_response")
                    text = result[0].get("generated_text") if (
                        isinstance(result, list)
                        and result
                        and isinstance(result[0], dict)
                    ) else None

                    if isinstance(text, str) and text.strip():
                        self.set_availability(True)
                        return {
                            "status": "success",
                            "text": text,
                            "agent": f"HuggingFace ({model})",
                            "tokens": len(text.split()),
                            "cost": 0.0
                        }
                    self.set_availability(False, "Malformed or empty response")
                    return self.failure_response("malformed_response")

                if response.status_code == 503:
                    time.sleep(3)
                    continue

                if response.status_code == 429:
                    time.sleep(5)
                    continue

                if 400 <= response.status_code < 500:
                    self.set_availability(False, f"HTTP {response.status_code}")
                    return self.failure_response("http_status", status_code=response.status_code)

                if 500 <= response.status_code < 600:
                    time.sleep(3)
                    continue

                self.set_availability(False, f"HTTP {response.status_code}")
                return self.failure_response("http_status", status_code=response.status_code)

            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                    continue
                self.set_availability(False, type(e).__name__)
                return self.failure_response("network_or_sdk_exception", exception_type=type(e).__name__)

        self.set_availability(False, "Retryable provider failure")
        return self.failure_response("retry_exhausted")
