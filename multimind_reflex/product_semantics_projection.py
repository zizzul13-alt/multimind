"""Renderer-neutral projection of application-owned AI product semantics."""
from __future__ import annotations
import json


def project_product_semantics(debate_data):
    if isinstance(debate_data, str):
        try: debate_data=json.loads(debate_data)
        except (TypeError,ValueError,json.JSONDecodeError): debate_data={}
    if not isinstance(debate_data,dict): debate_data={}
    truth=debate_data.get("product_semantics")
    if not isinstance(truth,dict): truth={}
    capability=truth.get("capability") if isinstance(truth.get("capability"),dict) else {}
    compressor=truth.get("compressor") if isinstance(truth.get("compressor"),dict) else {}
    participants=capability.get("participants") if isinstance(capability.get("participants"),list) else []
    return {
        "mode":str(truth.get("mode") or ""),
        "prompt_style":str(truth.get("prompt_style") or "default"),
        "style_applied":bool(truth.get("style_applied",False)),
        "recommended":[str(x) for x in capability.get("recommended",[]) if isinstance(x,str)],
        "capability_participants":[dict(x) for x in participants if isinstance(x,dict)],
        "explicit_participants":[str(x) for x in truth.get("explicit_participants",[]) if isinstance(x,str)],
        "compressor_enabled":bool(compressor.get("enabled",False)),
        "compressor_applied":bool(compressor.get("applied",False)),
        "compressor_utility_provider":compressor.get("utility_provider"),
        "compressor_fallback_reason":compressor.get("fallback_reason"),
    }
