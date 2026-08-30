"""
Gemini API wrapper - Compatibility Adapter
"""
from providers.gemini import GeminiProvider

class GeminiAgent(GeminiProvider):
    """Compatibility adapter for GeminiAgent, inheriting from GeminiProvider"""
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def generate(self, prompt, system_prompt=None, max_tokens=2000, **kwargs):
        """Maintains legacy signature with positional matching and kwargs support"""
        return super().generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            **kwargs
        )
