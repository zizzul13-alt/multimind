"""Prompt compression utility with preservation guards."""
from __future__ import annotations
import re

class PromptCompressor:
    """Compress a normalized task without silently changing task-critical literals."""
    CODE_BLOCK=re.compile(r"```[\s\S]*?```",re.MULTILINE)
    NUMBER=re.compile(r"(?<!\w)[+-]?(?:\d+(?:\.\d+)?%?|0x[0-9a-fA-F]+)(?!\w)")
    PATH=re.compile(r"(?:[A-Za-z]:\\[^\s]+|(?:\.?\.?/|/)[\w.\-/\\]+|[\w.-]+\.(?:py|js|ts|tsx|jsx|json|ya?ml|toml|ini|md|txt|csv|sql|db))")
    CONSTRAINT_LINE=re.compile(r"(?im)^.*\b(?:MUST|MUST NOT|DO NOT|NEVER|REQUIRED|ERROR|EXCEPTION|SOURCE|EVIDENCE)\b.*$")
    @staticmethod
    def should_compress(prompt,config): return bool(config.get("enabled",True)) and len(str(prompt or "").split())>=15
    @classmethod
    def critical_fragments(cls,prompt):
        text=str(prompt or ""); fragments=[]
        for pattern in (cls.CODE_BLOCK,cls.CONSTRAINT_LINE,cls.PATH,cls.NUMBER): fragments.extend(m.group(0).strip() for m in pattern.finditer(text))
        return [f for f in dict.fromkeys(fragments) if f]
    @classmethod
    def preserves_critical_content(cls,original,compressed): return all(f in str(compressed or "") for f in cls.critical_fragments(original))
    @staticmethod
    def _generic_compression_prompt(prompt):
        return "Compress the following common task specification to reduce repeated context cost. Do not add new requirements. Preserve every code block, number, filename/path, error/exception, explicit MUST/DO NOT/NEVER/REQUIRED constraint, and SOURCE/EVIDENCE marker verbatim. Return only the compressed specification.\n\n"+prompt
    @classmethod
    def _invoke(cls,prompt,utility_agent):
        if utility_agent is None: return None,"utility_unavailable"
        if hasattr(utility_agent,"compress_prompt"):
            result=utility_agent.compress_prompt(prompt)
            if not isinstance(result,dict) or result.get("status")=="error": return None,"utility_invalid_response"
            return {"text":result.get("text",prompt),"original_tokens":result.get("original_tokens",0),"compressed_tokens":result.get("compressed_tokens",0)},None
        if hasattr(utility_agent,"generate"):
            result=utility_agent.generate(prompt=cls._generic_compression_prompt(prompt),system_prompt=None,mode="thinking")
            if not isinstance(result,dict) or result.get("status")!="success" or not str(result.get("text","")).strip(): return None,"utility_invalid_response"
            return {"text":result["text"],"original_tokens":0,"compressed_tokens":result.get("tokens",0)},None
        return None,"utility_unavailable"
    @classmethod
    def compress(cls,prompt,utility_agent):
        result,reason=cls._invoke(prompt,utility_agent)
        if result is None: return {"original":prompt,"compressed":prompt,"applied":False,"fallback_reason":reason,"original_tokens":0,"compressed_tokens":0,"saved_tokens":0,"saved_percent":0}
        candidate=result.get("text",prompt); original_tokens=result.get("original_tokens",0); compressed_tokens=result.get("compressed_tokens",0); preserved=cls.preserves_critical_content(prompt,candidate)
        if not preserved: candidate=prompt; compressed_tokens=original_tokens
        saved=max(0,original_tokens-compressed_tokens)
        return {"original":prompt,"compressed":candidate,"applied":preserved and candidate!=prompt,"fallback_reason":None if preserved else "preservation_guard","original_tokens":original_tokens,"compressed_tokens":compressed_tokens,"saved_tokens":saved,"saved_percent":round((saved/original_tokens)*100,1) if original_tokens>0 else 0}
    @staticmethod
    def get_compression_tips(prompt):
        text=str(prompt or ""); tips=[]
        if len(text.split())>200: tips.append("💡 Prompt agak panjang, ringkas 50%")
        lowered=text.lower()
        if "tolong" in lowered or "terima kasih" in lowered: tips.append("✂️ Hapus kata basa-basi")
        if len(text.split('.'))>5: tips.append("📏 Pecah jadi poin-poin singkat")
        return tips
