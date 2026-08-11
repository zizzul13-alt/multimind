"""
Coze API wrapper - Compatibility Adapter
"""
from providers.coze import CozeProvider

class CozeAgent(CozeProvider):
    """Compatibility adapter for CozeAgent, inheriting from CozeProvider"""
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def generate(self, prompt, system_prompt=None, complexity=1, max_tokens=2048, **kwargs):
        """Maintains the exact original signature for backward compatibility"""
        return super().generate(
            prompt=prompt,
            system_prompt=system_prompt,
            complexity=complexity,
            max_tokens=max_tokens,
            **kwargs
        )
