from openai import OpenAI
from providers.base import BaseProvider
from utils.token_counter import TokenCounter

class DeepSeekProvider(BaseProvider):
    """DeepSeek API Provider"""

    def __init__(self, api_key: str):
        super().__init__("DeepSeek")
        if not api_key or api_key == "":
            self.client = None
            self.model_name = "DeepSeek (not configured)"
            self.set_availability(False, "API key not configured")
            return

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            self.model_name = "DeepSeek"
            self.set_availability(True)
        except Exception as e:
            self.client = None
            self.model_name = "DeepSeek (error)"
            self.set_availability(False, str(e))

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 2000, **kwargs) -> dict:
        if not self.client:
            return {
                "status": "error",
                "text": "DeepSeek API not configured.",
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
                model="deepseek-chat",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )

            text = response.choices[0].message.content

            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            cost = (input_tokens * 0.14 + output_tokens * 0.28) / 1_000_000
            self.set_availability(True)

            return {
                "status": "success",
                "text": text,
                "agent": self.model_name,
                "tokens": input_tokens + output_tokens,
                "cost": cost
            }

        except Exception as e:
            error_msg = str(e)
            self.set_availability(False, error_msg)
            return {
                "status": "error",
                "text": f"[DeepSeek unavailable: {error_msg[:100]}]",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
            }
