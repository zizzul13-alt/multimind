"""
Remote Agent - Compatibility Adapter
"""
from providers.remote import RemoteProvider

class RemoteAgent(RemoteProvider):
    """Compatibility adapter for RemoteAgent, inheriting from RemoteProvider"""
    def __init__(self, api_url: str):
        super().__init__(api_url)

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096, **kwargs):
        """Maintains the exact original signature for backward compatibility"""
        return super().generate(
            prompt=prompt,
            system_prompt=system_prompt,
            mode=mode,
            max_tokens=max_tokens,
            **kwargs
        )
