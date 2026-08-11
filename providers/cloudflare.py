import requests
from providers.base import BaseProvider
from utils.token_counter import TokenCounter

class CloudflareProvider(BaseProvider):
    """Cloudflare Workers AI Provider"""

    def __init__(self, api_key: str, account_id: str = None):
        super().__init__("Cloudflare")
        if not api_key or api_key == "":
            self.api_key = None
            self.model_name = "Cloudflare (not configured)"
            self.set_availability(False, "API key not configured")
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
        self.model_name = "Cloudflare (Workers AI)"
        self.set_availability(True)

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "general", max_tokens: int = 2000, **kwargs) -> dict:
        if not self.api_key:
            return {
                "status": "error",
                "text": "Cloudflare API not configured.",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
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

                self.set_availability(True)
                return {
                    "status": "success",
                    "text": text,
                    "agent": self.model_name,
                    "tokens": TokenCounter.count(full_prompt + text),
                    "cost": 0.0
                }
            else:
                errors = data.get("errors", [{}])
                error_msg = errors[0].get("message", "Unknown error") if errors else "Unknown error"
                self.set_availability(False, error_msg)
                return {
                    "status": "error",
                    "text": f"Cloudflare error: {error_msg}",
                    "agent": self.model_name,
                    "tokens": 0,
                    "cost": 0.0
                }

        except Exception as e:
            error_msg = str(e)
            self.set_availability(False, error_msg)
            return {
                "status": "error",
                "text": f"Cloudflare error: {error_msg[:200]}",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
            }
