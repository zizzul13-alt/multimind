"""Gemini compatibility adapter."""
from providers.gemini import GeminiProvider
from providers.model_registry import resolve_model

class GeminiAgent(GeminiProvider):
    def __init__(self,api_key:str):
        super().__init__(api_key)
        if self.client:
            resolution=resolve_model("gemini","general")
            if resolution is None:
                self.client=None; self.model_name="Gemini (no eligible model)"; self.set_availability(False,"No eligible model")
            else:
                self.model_name=resolution.model_id
    def generate(self,prompt,system_prompt=None,max_tokens=2000,**kwargs):
        return super().generate(prompt=prompt,system_prompt=system_prompt,max_tokens=max_tokens,**kwargs)
