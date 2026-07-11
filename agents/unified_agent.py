"""
Unified Agent - 1 class handle semua provider
Dengan auto-failover & rate limit handling
"""
from agents.gemini import GeminiAgent
from agents.groq import GroqAgent
from agents.cloudflare import CloudflareAgent
from agents.openrouter import OpenRouterAgent
from agents.huggingface import HuggingFaceAgent
from agents.deepseek import DeepSeekAgent

class UnifiedAgent:
    """Handle semua AI provider dalam 1 class"""

    def __init__(self, api_keys):
        self.providers = []
        
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

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096):
        """Generate response - auto-failover ke provider berikutnya"""
        
        for provider in self.providers:
            try:
                if provider["name"] == "☁️ Cloudflare":
                    response = provider["agent"].generate(prompt, system_prompt, mode, max_tokens)
                elif provider["name"] == "🌐 OpenRouter":
                    response = provider["agent"].generate(prompt, system_prompt, mode, max_tokens)
                else:
                    response = provider["agent"].generate(prompt, system_prompt, max_tokens)
                
                if response.get("status") == "success":
                    response["agent"] = provider["name"]
                    return response
                    
            except Exception as e:
                continue
        
        return {
            "status": "error",
            "text": "❌ Semua provider gagal",
            "agent": "Unified",
            "tokens": 0,
            "cost": 0
        }

    def get_available_providers(self):
        """List provider yang tersedia"""
        return [p["name"] for p in self.providers]
