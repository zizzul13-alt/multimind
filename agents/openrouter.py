"""
OpenRouter API wrapper - Compatibility Adapter
"""
from providers.openrouter import OpenRouterProvider

class OpenRouterAgent(OpenRouterProvider):
    """Compatibility adapter for OpenRouterAgent, inheriting from OpenRouterProvider"""
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096, **kwargs):
        """Maintains legacy signature with positional matching and kwargs support"""
        return super().generate(
            prompt=prompt,
            system_prompt=system_prompt,
            mode=mode,
            max_tokens=max_tokens,
            **kwargs
        )
