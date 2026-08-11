from openai import OpenAI
from providers.base import BaseProvider
from utils.token_counter import TokenCounter

class OpenRouterProvider(BaseProvider):
    """OpenRouter API Provider (Access free models)"""

    def __init__(self, api_key: str):
        super().__init__("OpenRouter")
        if not api_key or api_key == "":
            self.client = None
            self.model_name = "OpenRouter (not configured)"
            self.set_availability(False, "API key not configured")
            return

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            self.models = {
                "coding": "qwen/qwen3-coder:free",
                "research": "meta-llama/llama-3.3-70b-instruct:free",
                "thinking": "nousresearch/hermes-3-llama-3.1-405b:free",
                "quick": "meta-llama/llama-3.2-3b-instruct:free"
            }
            self.model_name = "OpenRouter (Multi-Model FREE)"
            self.set_availability(True)
        except Exception as e:
            self.client = None
            self.model_name = "OpenRouter (error)"
            self.set_availability(False, str(e))

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 4096, **kwargs) -> dict:
        if not self.client:
            return {
                "status": "error",
                "text": "OpenRouter not configured.",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
            }

        model = self.models.get(mode, self.models["quick"])

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                extra_headers={
                    "HTTP-Referer": "https://multimind.streamlit.app",
                    "X-Title": "MultiMind AI"
                }
            )

            text = response.choices[0].message.content
            self.set_availability(True)

            return {
                "status": "success",
                "text": text,
                "agent": f"OpenRouter ({model})",
                "tokens": response.usage.total_tokens if response.usage else len(text.split()),
                "cost": 0.0
            }

        except Exception as e:
            error_msg = str(e)
            self.set_availability(False, error_msg)
            return {
                "status": "error",
                "text": f"OpenRouter error: {error_msg[:150]}",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
            }
