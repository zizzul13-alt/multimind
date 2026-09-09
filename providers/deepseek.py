from openai import OpenAI
from providers.base import BaseProvider
from providers.model_registry import openai_catalog, resolve_model
from utils.config import Config


class DeepSeekProvider(BaseProvider):
    """DeepSeek adapter. Paid-optional models require explicit provider selection."""

    def __init__(self, api_key: str):
        super().__init__("DeepSeek")
        if not api_key:
            self.client = None
            self.model_name = "DeepSeek (not configured)"
            self.set_availability(False, "API key not configured")
            return
        try:
            self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com", timeout=Config.API_TIMEOUT, max_retries=0)
            self.model_name = "DeepSeek (dynamic model)"
            self.set_availability(True)
        except Exception as e:
            self.client = None
            self.model_name = "DeepSeek (error)"
            self.set_availability(False, type(e).__name__)

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 2000, **kwargs) -> dict:
        if not self.client:
            return self.failure_response("not_configured")
        resolution = resolve_model("deepseek", mode, discover=lambda: openai_catalog(self.client), allow_paid=True)
        if resolution is None:
            return self.failure_response("no_eligible_model")
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = self.client.chat.completions.create(model=resolution.model_id, messages=messages, max_tokens=max_tokens, temperature=0.7)
            try:
                text = response.choices[0].message.content
            except (AttributeError, IndexError, TypeError):
                self.set_availability(False, "Malformed response")
                return self.failure_response("malformed_response")
            if not isinstance(text, str) or not text.strip():
                self.set_availability(False, "Empty response")
                return self.failure_response("empty_response")
            usage = getattr(response, "usage", None)
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            actual_model = getattr(response, "model", None) or resolution.model_id
            self.model_name = f"DeepSeek ({actual_model})"
            self.set_availability(True)
            return {"status": "success", "text": text, "agent": self.model_name, "tokens": input_tokens + output_tokens, "cost": 0.0, "resolved_model": resolution.model_id, "actual_model": actual_model, "model_resolution_source": resolution.source, "model_family": resolution.family}
        except Exception as e:
            self.set_availability(False, type(e).__name__)
            return self.failure_response("network_or_sdk_exception", exception_type=type(e).__name__)
