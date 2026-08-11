"""
DeepSeek API wrapper - Compatibility Adapter
"""
from providers.deepseek import DeepSeekProvider

class DeepSeekAgent(DeepSeekProvider):
    """Compatibility adapter for DeepSeekAgent, inheriting from DeepSeekProvider"""
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
