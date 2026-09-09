from openai import OpenAI
from providers.base import BaseProvider
from providers.model_registry import resolve_model
from utils.config import Config


class OpenRouterProvider(BaseProvider):
    """OpenRouter adapter using its free dynamic router, not stale per-mode IDs."""

    def __init__(self, api_key: str):
        super().__init__("OpenRouter")
        if not api_key:
            self.client = None
            self.model_name = "OpenRouter (not configured)"
            self.set_availability(False, "API key not configured")
            return
        try:
            self.client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1", timeout=Config.API_TIMEOUT, max_retries=0)
            self.model_name = "OpenRouter (dynamic FREE router)"
            self.set_availability(True)
        except Exception as e:
            self.client = None
            self.model_name = "OpenRouter (error)"
            self.set_availability(False, type(e).__name__)

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 4096, **kwargs) -> dict:
        if not self.client:
            return self.failure_response("not_configured")
        # openrouter/free is itself a provider-side live model resolver. We do not
        # make a second catalogue request on every user call; the concrete model
        # returned by OpenRouter is persisted below as actual_model.
        resolution = resolve_model("openrouter", mode)
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
            actual_model = getattr(response, "model", None) or resolution.model_id
            self.model_name = f"OpenRouter ({actual_model})"
            self.set_availability(True)
            return {"status": "success", "text": text, "agent": self.model_name, "tokens": response.usage.total_tokens if response.usage else len(text.split()), "cost": 0.0, "resolved_model": resolution.model_id, "actual_model": actual_model, "model_resolution_source": "provider_dynamic_router", "model_family": resolution.family}
        except Exception as e:
            self.set_availability(False, type(e).__name__)
            return self.failure_response("network_or_sdk_exception", exception_type=type(e).__name__)
