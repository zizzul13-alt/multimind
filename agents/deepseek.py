"""
DeepSeek API wrapper - dengan error handling
"""
from openai import OpenAI
from utils.token_counter import TokenCounter

class DeepSeekAgent:
    """DeepSeek agent dengan graceful error handling"""

    def __init__(self, api_key):
        if not api_key or api_key == "":
            self.client = None
            self.name = "DeepSeek (not configured)"
            return

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            self.name = "DeepSeek"
        except Exception as e:
            print(f"DeepSeek init error: {e}")
            self.client = None
            self.name = "DeepSeek (error)"

    def generate(self, prompt, system_prompt=None, max_tokens=2000):
        """Generate response - return error dict instead of raising exception"""
        if not self.client:
            return {
                "status": "error",
                "text": "DeepSeek API not configured.",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
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

            return {
                "status": "success",
                "text": text,
                "agent": self.name,
                "tokens": input_tokens + output_tokens,
                "cost": cost
            }

        except Exception as e:
            error_msg = str(e)
            print(f"DeepSeek error: {error_msg}")
            return {
                "status": "error",
                "text": f"[DeepSeek unavailable: {error_msg[:100]}]",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }
