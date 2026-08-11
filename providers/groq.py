from openai import OpenAI
from providers.base import BaseProvider
from utils.token_counter import TokenCounter

class GroqProvider(BaseProvider):
    """Groq API Provider"""

    def __init__(self, api_key: str):
        super().__init__("Groq")
        if not api_key or api_key == "":
            self.client = None
            self.model_name = "Groq (not configured)"
            self.set_availability(False, "API key not configured")
            return

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
            self.model_name = "Groq (Llama 4 Scout)"
            self.set_availability(True)
        except Exception as e:
            self.client = None
            self.model_name = "Groq (error)"
            self.set_availability(False, str(e))

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 4096, **kwargs) -> dict:
        if not self.client:
            return {
                "status": "error",
                "text": "Groq API not configured.",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
            }

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )

            text = response.choices[0].message.content
            self.set_availability(True)

            return {
                "status": "success",
                "text": text,
                "agent": self.model_name,
                "tokens": response.usage.total_tokens if response.usage else len(text.split()),
                "cost": 0.0
            }

        except Exception as e:
            error_msg = str(e)
            self.set_availability(False, error_msg)
            return {
                "status": "error",
                "text": f"[Groq unavailable: {error_msg[:100]}]",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
            }
