"""
Unified Agent - 1 class handle semua provider
Dengan auto-failover canggih + rate limit handler + monitoring
"""
import time
from agents.gemini import GeminiAgent
from agents.groq import GroqAgent
from agents.cloudflare import CloudflareAgent
from agents.openrouter import OpenRouterAgent
from agents.huggingface import HuggingFaceAgent
from agents.deepseek import DeepSeekAgent
from providers.base import BaseProvider
from agents.router import TERMINAL_PROVIDER_FAILURE_TEXT, _log_provider_failure

class UnifiedAgent:
    """Handle semua AI provider dalam 1 class"""

    def __init__(self, api_keys):
        self.providers = []
        self.stats = {}  # Monitoring stats
        
        # Register providers (urut prioritas)
        if api_keys.get("cloudflare_key"):
            self.providers.append({
                "name": "☁️ Cloudflare",
                "agent": CloudflareAgent(api_keys["cloudflare_key"], api_keys.get("cloudflare_account_id", ""))
            })
        
        if api_keys.get("groq_key"):
            self.providers.append({
                "name": "⚡ Groq",
                "agent": GroqAgent(api_keys["groq_key"])
            })
        
        if api_keys.get("openrouter_key"):
            self.providers.append({
                "name": "🌐 OpenRouter",
                "agent": OpenRouterAgent(api_keys["openrouter_key"])
            })
        
        if api_keys.get("huggingface_key"):
            self.providers.append({
                "name": "🤗 HuggingFace",
                "agent": HuggingFaceAgent(api_keys["huggingface_key"])
            })
        
        if api_keys.get("deepseek_key"):
            self.providers.append({
                "name": "🐳 DeepSeek",
                "agent": DeepSeekAgent(api_keys["deepseek_key"])
            })
        
        if api_keys.get("gemini_key"):
            self.providers.append({
                "name": "🔍 Gemini",
                "agent": GeminiAgent(api_keys["gemini_key"])
            })
        
        # Init stats
        for p in self.providers:
            self.stats[p["name"]] = {
                "success": 0,
                "error": 0,
                "rate_limited": False,
                "last_error": ""
            }

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096):
        """Generate response - auto-failover + rate limit handling"""
        
        for provider in self.providers:
            name = provider["name"]
            
            # Skip kalau lagi rate limited
            if self.stats[name]["rate_limited"]:
                continue
            
            try:
                # Panggil agent sesuai tipe
                if name == "☁️ Cloudflare":
                    response = provider["agent"].generate(prompt, system_prompt, mode, max_tokens)
                elif name == "🌐 OpenRouter":
                    response = provider["agent"].generate(prompt, system_prompt, mode, max_tokens)
                elif name == "🤗 HuggingFace":
                    response = provider["agent"].generate(prompt, system_prompt, mode, max_tokens)
                else:
                    response = provider["agent"].generate(prompt, system_prompt, max_tokens)
                
                # Cek rate limit
                if response.get("status") == "error":
                    error_text = response.get("text", "")
                    failure_category = response.get("failure_category", "provider_error")
                    
                    # Deteksi rate limit (429)
                    if "429" in error_text or "rate" in error_text.lower():
                        self.stats[name]["rate_limited"] = True
                        self.stats[name]["last_error"] = "Rate limited"
                        _log_provider_failure(name, response)
                        continue  # Skip ke provider berikutnya
                    
                    # Error biasa → skip
                    self.stats[name]["error"] += 1
                    self.stats[name]["last_error"] = failure_category
                    _log_provider_failure(name, response)
                    continue
                
                # Sukses!
                if BaseProvider.has_usable_response(response):
                    self.stats[name]["success"] += 1
                    response["agent"] = name
                    return response

                self.stats[name]["error"] += 1
                self.stats[name]["last_error"] = "Empty or malformed response"
                _log_provider_failure(name, {"failure_category": "empty_response"})
                continue
                    
            except Exception as e:
                self.stats[name]["error"] += 1
                self.stats[name]["last_error"] = type(e).__name__
                _log_provider_failure(name, exception_type=type(e).__name__)
                continue
        
        # Reset rate limit flags setelah semua gagal
        for name in self.stats:
            self.stats[name]["rate_limited"] = False
        
        return {
            "status": "error",
            "text": TERMINAL_PROVIDER_FAILURE_TEXT,
            "agent": "Unified",
            "tokens": 0,
            "cost": 0
        }

    def get_stats(self):
        """Return monitoring stats"""
        return self.stats

    def get_available_providers(self):
        """List provider yang tersedia (tidak rate limited)"""
        available = []
        for p in self.providers:
            name = p["name"]
            if not self.stats.get(name, {}).get("rate_limited", False):
                available.append(name)
        return available

    def reset_rate_limits(self):
        """Reset semua rate limit flags"""
        for name in self.stats:
            self.stats[name]["rate_limited"] = False
