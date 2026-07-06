"""
Cloudflare Workers AI wrapper - GRATIS 10,000 req/bulan!
"""
import requests
from utils.token_counter import TokenCounter


class CloudflareAgent:
    """Cloudflare Workers AI agent (FREE)"""

    def __init__(self, api_key, account_id=None):
        if not api_key or api_key == "":
            self.client = None
            self.name = "Cloudflare (not configured)"
            return

        self.api_key = api_key
        if account_id:
            self.account_id = account_id
        else:
            self.account_id = ""

        self.base_url = "https://api.cloudflare.com/client/v4/accounts"
        self.model_map = {
            "coding": "@cf/deepseek-ai/deepseek-coder-6.7b-base",
            "research": "@cf/meta/llama-3.1-8b-instruct",
            "thinking": "@cf/meta/llama-3.1-8b-instruct",
            "general": "@cf/meta/llama-3.1-8b-instruct"
        }
        self.name = "Cloudflare (Workers AI)"

    def generate(self, prompt, system_prompt=None, max_tokens=2000, mode="general"):
        """Generate response"""
        if not self.api_key:
            return {
                "status": "error",
                "text": "Cloudflare API not configured.",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }

        try:
            model = self.model_map.get(mode, self.model_map["general"])

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            payload = {
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "max_tokens": max_tokens
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            url = f"{self.base_url}/{self.account_id}/ai/run/{model}"
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            data = response.json()

            if data.get("success"):
                result = data.get("result", {})
                if isinstance(result, dict):
                    text = result.get("response", "")
                else:
                    text = str(result)

                return {
                    "status": "success",
                    "text": text,
                    "agent": self.name,
                    "tokens": TokenCounter.count(full_prompt + text),
                    "cost": 0
                }
            else:
                errors = data.get("errors", [{}])
                error_msg = errors[0].get("message", "Unknown error") if errors else "Unknown error"
                return {
                    "status": "error",
                    "text": f"Cloudflare error: {error_msg}",
                    "agent": self.name,
                    "tokens": 0,
                    "cost": 0
                }

        except Exception as e:
            return {
                "status": "error",
                "text": f"Cloudflare error: {str(e)[:200]}",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }
