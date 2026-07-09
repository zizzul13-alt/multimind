"""
OpenRouter API wrapper - akses 50+ model GRATIS!
"""
from openai import OpenAI
from utils.token_counter import TokenCounter

class OpenRouterAgent:
    """OpenRouter agent (FREE models)"""

    def __init__(self, api_key):
        if not api_key or api_key == "":
            self.client = None
            self.name = "OpenRouter (not configured)"
            return

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            self.models = {
                "coding": "deepseek/deepseek-chat",
                "research": "meta-llama/llama-3.1-8b-instruct",
                "thinking": "meta-llama/llama-3.1-8b-instruct",
                "quick": "deepseek/deepseek-chat"
            }
            self.name = "OpenRouter (Multi-Model)"
        except Exception as e:
            print(f"OpenRouter init error: {e}")
            self.client = None
            self.name = "OpenRouter (error)"

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=2048):
        """Generate response - auto-pilih model sesuai mode"""
        if not self.client:
            return {
                "status": "error",
                "text": "OpenRouter not configured.",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
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

            return {
                "status": "success",
                "text": text,
                "agent": f"OpenRouter ({model})",
                "tokens": response.usage.total_tokens if response.usage else len(text.split()),
                "cost": 0
            }

        except Exception as e:
            return {
                "status": "error",
                "text": f"OpenRouter error: {str(e)[:150]}",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }
