import time
import requests
from providers.base import BaseProvider
from providers.model_registry import resolve_model
from utils.config import Config

class HuggingFaceProvider(BaseProvider):
    ENDPOINT="https://router.huggingface.co/v1/chat/completions"
    def __init__(self,api_key:str):
        super().__init__("HuggingFace")
        if not api_key:
            self.api_key=None; self.model_name="HuggingFace (not configured)"; self.set_availability(False,"API key not configured"); return
        self.api_key=api_key; self.model_name="HuggingFace (dynamic model)"; self.set_availability(True)
    @staticmethod
    def _extract_text(data):
        if isinstance(data,dict):
            try: return data["choices"][0]["message"]["content"]
            except (KeyError,IndexError,TypeError): return None
        if isinstance(data,list) and data and isinstance(data[0],dict): return data[0].get("generated_text")
        return None
    def generate(self,prompt:str,system_prompt:str=None,mode:str="coding",max_tokens:int=2048,**kwargs)->dict:
        if not self.api_key: return self.failure_response("not_configured")
        resolution=resolve_model("huggingface",mode)
        if resolution is None: return self.failure_response("no_eligible_model")
        messages=[]
        if system_prompt: messages.append({"role":"system","content":system_prompt})
        messages.append({"role":"user","content":prompt})
        payload={"model":resolution.model_id,"messages":messages,"max_tokens":max_tokens,"temperature":0.7}; headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"}
        for attempt in range(3):
            try:
                response=requests.post(self.ENDPOINT,headers=headers,json=payload,timeout=Config.API_TIMEOUT)
                if response.status_code==200:
                    try: data=response.json()
                    except ValueError: self.set_availability(False,"Malformed response"); return self.failure_response("malformed_response")
                    text=self._extract_text(data)
                    if not isinstance(text,str) or not text.strip(): self.set_availability(False,"Empty response"); return self.failure_response("empty_response")
                    usage=data.get("usage",{}) if isinstance(data,dict) else {}; actual_model=data.get("model") if isinstance(data,dict) else None; actual_model=actual_model or resolution.model_id
                    self.model_name=f"HuggingFace ({actual_model})"; self.set_availability(True)
                    return {"status":"success","text":text,"agent":self.model_name,"tokens":usage.get("total_tokens",0),"cost":0.0,"resolved_model":resolution.model_id,"actual_model":actual_model,"model_resolution_source":resolution.source,"model_family":resolution.family}
                if response.status_code in {429,500,502,503,504}:
                    if attempt<2: time.sleep(2); continue
                    self.set_availability(False,f"HTTP {response.status_code}"); return self.failure_response("retry_exhausted",status_code=response.status_code)
                self.set_availability(False,f"HTTP {response.status_code}"); return self.failure_response("http_status",status_code=response.status_code)
            except Exception as e:
                if attempt<2: time.sleep(2); continue
                self.set_availability(False,type(e).__name__); return self.failure_response("network_or_sdk_exception",exception_type=type(e).__name__)
        return self.failure_response("retry_exhausted")
