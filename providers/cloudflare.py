import requests
from providers.base import BaseProvider
from providers.model_registry import resolve_model
from utils.token_counter import TokenCounter
from utils.config import Config

class CloudflareProvider(BaseProvider):
    def __init__(self,api_key:str,account_id:str=None):
        super().__init__("Cloudflare")
        if not api_key or not account_id:
            self.api_key=None; self.account_id=""; self.model_name="Cloudflare (not configured)"; self.set_availability(False,"API key or account ID not configured"); return
        self.api_key=api_key; self.account_id=account_id; self.base_url="https://api.cloudflare.com/client/v4/accounts"; self.model_name="Cloudflare (dynamic model)"; self.set_availability(True)
    def generate(self,prompt:str,system_prompt:str=None,mode:str="general",max_tokens:int=2000,**kwargs)->dict:
        if not self.api_key: return self.failure_response("not_configured")
        resolution=resolve_model("cloudflare",mode)
        if resolution is None: return self.failure_response("no_eligible_model")
        try:
            messages=[]
            if system_prompt: messages.append({"role":"system","content":system_prompt})
            messages.append({"role":"user","content":prompt})
            payload={"messages":messages,"max_tokens":max_tokens}; headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"}
            response=requests.post(f"{self.base_url}/{self.account_id}/ai/run/{resolution.model_id}",json=payload,headers=headers,timeout=Config.API_TIMEOUT)
            if not response.ok:
                self.set_availability(False,f"HTTP {response.status_code}"); return self.failure_response("http_status",status_code=response.status_code)
            try: data=response.json()
            except ValueError: self.set_availability(False,"Malformed response"); return self.failure_response("malformed_response")
            result=data.get("result",{}) if isinstance(data,dict) and data.get("success") else {}; text=result.get("response") if isinstance(result,dict) else None
            if not isinstance(text,str) or not text.strip(): self.set_availability(False,"Empty response"); return self.failure_response("empty_response")
            self.model_name=f"Cloudflare ({resolution.model_id})"; self.set_availability(True)
            return {"status":"success","text":text,"agent":self.model_name,"tokens":TokenCounter.count((system_prompt or "")+prompt+text),"cost":0.0,"resolved_model":resolution.model_id,"actual_model":resolution.model_id,"model_resolution_source":resolution.source,"model_family":resolution.family}
        except Exception as e:
            self.set_availability(False,type(e).__name__); return self.failure_response("network_or_sdk_exception",exception_type=type(e).__name__)
