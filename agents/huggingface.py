"""
HuggingFace Inference API - Compatibility Adapter
"""
from providers.huggingface import HuggingFaceProvider

class HuggingFaceAgent(HuggingFaceProvider):
    """Compatibility adapter for HuggingFaceAgent, inheriting from HuggingFaceProvider"""
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=2048, **kwargs):
        """Maintains legacy signature with positional matching and kwargs support"""
        return super().generate(
            prompt=prompt,
            system_prompt=system_prompt,
            mode=mode,
            max_tokens=max_tokens,
            **kwargs
        )
