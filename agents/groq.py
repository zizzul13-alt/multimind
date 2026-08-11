"""
Groq API wrapper - Compatibility Adapter
"""
from providers.groq import GroqProvider

class GroqAgent(GroqProvider):
    """Compatibility adapter for GroqAgent, inheriting from GroqProvider"""
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def generate(self, prompt, system_prompt=None, max_tokens=4096, **kwargs):
        """Maintains legacy signature with positional matching and kwargs support"""
        return super().generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            **kwargs
        )
