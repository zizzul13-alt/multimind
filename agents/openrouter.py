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
                "coding": "qwen/qwen3-coder:free",
                "research": "meta-llama/llama-3.3-70b-instruct:free",
                "thinking": "nousresearch/hermes-3-llama-3.1-405b:free",
                "quick": "meta-llama/llama-3.2-3b-instruct:free"
            }
            self.name = "OpenRouter (Multi-Model FREE)"
        except Exception as e:
            print(f"OpenRouter init error: {e}")
            self.client = None
            self.name = "OpenRouter (error)"

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096):
        """Generate response - auto-pilih model gratis sesuai mode"""
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
            error_msg = str(e)[:150]
            print(f"OpenRouter error: {error_msg}")
            return {
                "status": "error",
                "text": f"OpenRouter error: {error_msg}",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }