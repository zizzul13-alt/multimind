"""
Cloudflare Workers AI wrapper - Compatibility Adapter
"""
from providers.cloudflare import CloudflareProvider

class CloudflareAgent(CloudflareProvider):
    """Compatibility adapter for CloudflareAgent, inheriting from CloudflareProvider"""
    def __init__(self, api_key: str, account_id: str = None):
        super().__init__(api_key, account_id)

    def generate(self, prompt, system_prompt=None, max_tokens=2000, mode="general", **kwargs):
        """Maintains legacy signature with positional matching and kwargs support"""
        return super().generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            mode=mode,
            **kwargs
        )
