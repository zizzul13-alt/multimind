"""Compatibility unified agent over the provider adapters."""
from agents.gemini import GeminiAgent
from agents.groq import GroqAgent
from agents.cloudflare import CloudflareAgent
from agents.openrouter import OpenRouterAgent
from agents.huggingface import HuggingFaceAgent
from agents.deepseek import DeepSeekAgent
from providers.base import BaseProvider
from agents.router import TERMINAL_PROVIDER_FAILURE_TEXT, _is_rate_limited, _log_provider_failure


class UnifiedAgent:
    """Compatibility facade retaining the established unified-provider API."""

    def __init__(self, api_keys):
        self.providers = []
        # Keep one explicit, documented priority. Gemini is the production proving
        # path; remaining providers preserve fallback independence.
        specs = [
            ("gemini_key", "🔍 Gemini", lambda: GeminiAgent(api_keys["gemini_key"])),
            ("groq_key", "⚡ Groq", lambda: GroqAgent(api_keys["groq_key"])),
            ("cloudflare_key", "☁️ Cloudflare", lambda: CloudflareAgent(api_keys["cloudflare_key"], api_keys.get("cloudflare_account_id", ""))),
            ("openrouter_key", "🌐 OpenRouter", lambda: OpenRouterAgent(api_keys["openrouter_key"])),
            ("huggingface_key", "🤗 HuggingFace", lambda: HuggingFaceAgent(api_keys["huggingface_key"])),
            ("deepseek_key", "🐳 DeepSeek", lambda: DeepSeekAgent(api_keys["deepseek_key"])),
        ]
        for key, name, factory in specs:
            if api_keys.get(key):
                self.providers.append({"name": name, "agent": factory()})
        self.stats = {p["name"]: {"success": 0, "error": 0, "rate_limited": False, "last_error": ""} for p in self.providers}

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096):
        for provider in self.providers:
            name = provider["name"]
            if self.stats[name]["rate_limited"]:
                continue
            try:
                response = provider["agent"].generate(prompt=prompt, system_prompt=system_prompt, mode=mode, max_tokens=max_tokens)
                if response.get("status") == "error":
                    failure_category = response.get("failure_category", "provider_error")
                    if _is_rate_limited(response):
                        self.stats[name]["rate_limited"] = True
                        self.stats[name]["last_error"] = "Rate limited"
                    else:
                        self.stats[name]["error"] += 1
                        self.stats[name]["last_error"] = failure_category
                    _log_provider_failure(name, response)
                    continue
                if BaseProvider.has_usable_response(response):
                    self.stats[name]["success"] += 1
                    response["agent"] = name
                    return response
                self.stats[name]["error"] += 1
                self.stats[name]["last_error"] = "Empty or malformed response"
                _log_provider_failure(name, {"failure_category": "empty_response"})
            except Exception as e:
                self.stats[name]["error"] += 1
                self.stats[name]["last_error"] = type(e).__name__
                _log_provider_failure(name, exception_type=type(e).__name__)
        for name in self.stats:
            self.stats[name]["rate_limited"] = False
        return {"status": "error", "text": TERMINAL_PROVIDER_FAILURE_TEXT, "agent": "Unified", "tokens": 0, "cost": 0}

    def get_stats(self):
        return self.stats

    def get_available_providers(self):
        return [p["name"] for p in self.providers if not self.stats.get(p["name"], {}).get("rate_limited", False)]

    def reset_rate_limits(self):
        for name in self.stats:
            self.stats[name]["rate_limited"] = False
