"""AI-identity-first routing over built-in and discovered provider resources."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
from providers.base import BaseProvider

@dataclass(frozen=True)
class AiIdentitySpec:
    identity_id:str; display_name:str; families:tuple[str,...]; route_order:tuple[str,...]; execution_slot:str

AI_IDENTITIES={
 "gemini":AiIdentitySpec("gemini","Gemini",("gemini",),("gemini",),"gemini"),
 "gpt-oss":AiIdentitySpec("gpt-oss","GPT-OSS",("gpt-oss",),("groq","huggingface"),"groq"),
 "llama":AiIdentitySpec("llama","Llama",("llama",),("cloudflare",),"cloudflare"),
 "deepseek":AiIdentitySpec("deepseek","DeepSeek",("deepseek",),("deepseek",),"deepseek"),
 "claude":AiIdentitySpec("claude","Claude",("claude",),(),"openrouter"),
 "gpt":AiIdentitySpec("gpt","GPT",("gpt",),(),"huggingface"),
 "qwen":AiIdentitySpec("qwen","Qwen",("qwen",),(),"cloudflare"),
 "kimi":AiIdentitySpec("kimi","Kimi",("kimi",),(),"deepseek"),
 "grok":AiIdentitySpec("grok","Grok",("grok",),(),"gemini"),
}
# Preserve the closed primary-catalogue contract. The broader presentation list is
# explicitly separate and represents identities that can become available through discovery.
AI_IDENTITY_OPTIONS=("gemini","gpt-oss","llama","deepseek")
DISCOVERABLE_AI_IDENTITY_OPTIONS=tuple(AI_IDENTITIES)
AI_IDENTITY_LABELS={key:spec.display_name for key,spec in AI_IDENTITIES.items()}
_MODEL_IDENTITY_CHECKS=((("gemini",),"gemini"),(("gpt-oss",),"gpt-oss"),(("llama","meta/llama","meta-llama"),"llama"),(("deepseek",),"deepseek"),(("claude","anthropic/"),"claude"),(("qwen",),"qwen"),(("kimi","moonshot"),"kimi"),(("grok","x-ai/","xai/"),"grok"),(("gpt-","openai/gpt-"),"gpt"))
_FAMILY_ALIASES={"gemini":"gemini","gpt-oss":"gpt-oss","llama":"llama","deepseek":"deepseek","claude":"claude","qwen":"qwen","kimi":"kimi","moonshot":"kimi","grok":"grok","gpt":"gpt"}

def infer_ai_identity(*,model_id=None,family=None):
 model=str(model_id or "").strip().lower()
 if model:
  for needles,identity in _MODEL_IDENTITY_CHECKS:
   if any(needle in model for needle in needles): return identity
 return _FAMILY_ALIASES.get(str(family or "").strip().lower())

def _model_from_response(response,provider): return str(response.get("actual_model") or response.get("resolved_model") or getattr(provider,"model_name","") or "")

def runtime_identity_specs(agents):
 configured=agents or {}; route_map={key:list(spec.route_order) for key,spec in AI_IDENTITIES.items()}
 for route_id,provider in configured.items():
  if not str(route_id).startswith("resource:") or provider is None: continue
  identity_id=infer_ai_identity(model_id=getattr(provider,"model_name",None))
  if identity_id in route_map: route_map[identity_id].append(str(route_id))
 return {key:AiIdentitySpec(base.identity_id,base.display_name,base.families,tuple(dict.fromkeys(route_map[key])),base.execution_slot) for key,base in AI_IDENTITIES.items()}

class IdentityRoutedProvider(BaseProvider):
 def __init__(self,spec,routes): super().__init__(spec.display_name); self.spec=spec; self.routes=list(routes); self.model_name=spec.display_name
 def generate(self,prompt,system_prompt=None,mode="coding",max_tokens=4096,**kwargs):
  attempts=[]
  for route_index,(route_id,provider) in enumerate(self.routes):
   try: response=provider.generate(prompt=prompt,system_prompt=system_prompt,mode=mode,max_tokens=max_tokens,**kwargs)
   except Exception as exc: attempts.append({"route":route_id,"status":"error","reason":type(exc).__name__}); continue
   if not BaseProvider.has_usable_response(response): attempts.append({"route":route_id,"status":"error","reason":str(response.get("failure_category") or "provider_error") if isinstance(response,dict) else "provider_error"}); continue
   model_id=_model_from_response(response,provider); effective_identity=infer_ai_identity(model_id=model_id,family=response.get("model_family") if isinstance(response,dict) else None)
   if effective_identity!=self.spec.identity_id: attempts.append({"route":route_id,"status":"rejected","reason":"identity_mismatch"}); continue
   result=dict(response); result.update({"requested_identity":self.spec.identity_id,"effective_identity":effective_identity,"route_provider":route_id,"actual_model":model_id or response.get("actual_model"),"identity_route_fallback":route_index>0,"identity_fallback_reason":"same_identity_route_failure" if route_index>0 else None,"route_attempts":attempts+[{"route":route_id,"status":"success","reason":""}],"identity_provenance":response.get("identity_provenance","provider_model_provenance")}); result["agent"]=route_id; self.model_name=model_id or self.spec.display_name; self.set_availability(True); return result
  self.set_availability(False,"No truthful route available"); return {"status":"error","text":"Provider temporarily unavailable. Trying another provider.","agent":self.spec.display_name,"tokens":0,"cost":0.0,"failure_category":"identity_unavailable","requested_identity":self.spec.identity_id,"effective_identity":None,"route_provider":None,"identity_route_fallback":False,"identity_fallback_reason":"all_same_identity_routes_failed","route_attempts":attempts}

def build_identity_providers(agents):
 configured=agents or {}; identities={}
 for identity_id,spec in runtime_identity_specs(configured).items():
  routes=[(route_id,configured[route_id]) for route_id in spec.route_order if configured.get(route_id) is not None]
  if routes: identities[identity_id]=IdentityRoutedProvider(spec,routes)
 return identities

def available_identity_options(agents): return list(build_identity_providers(agents))
