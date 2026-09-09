"""Gemini compatibility adapter."""
from providers.gemini import GeminiProvider
from providers.model_registry import resolve_model

class GeminiAgent(GeminiProvider):
    def __init__(self,api_key:str):
        super().__init__(api_key); self._model_resolution=None
        if self.client:
            self._model_resolution=resolve_model("gemini","general")
            if self._model_resolution is None:
                self.client=None; self.model_name="Gemini (no eligible model)"; self.set_availability(False,"No eligible model")
            else:
                self.model_name=self._model_resolution.model_id
    def generate(self,prompt,system_prompt=None,max_tokens=2000,**kwargs):
        result=super().generate(prompt=prompt,system_prompt=system_prompt,max_tokens=max_tokens,**kwargs)
        if isinstance(result,dict) and result.get("status")=="success" and self._model_resolution:
            result["resolved_model"]=self._model_resolution.model_id
            result["actual_model"]=None
            result["model_resolution_source"]="provider_latest_alias"
            result["model_family"]=self._model_resolution.family
        return result
