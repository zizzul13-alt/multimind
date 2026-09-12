"""Conversation-first operating-model primitives for MultiMind."""
from __future__ import annotations
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

AUTO_VALUES={"auto","lazy"}; WORK_MODES=("coding","research","thinking"); AUTHORITY_LEVELS=("think","retrieve","act","high_impact")
_CODING={"code","coding","implement","implementation","bug","fix","refactor","repo","repository","commit","pr","test","pytest","python","typescript","javascript","sql","api","function","class"}
_RESEARCH={"research","riset","cari","search","source","sumber","evidence","bukti","compare","banding","benchmark","latest","terbaru","web","fact","fakta","verify","verifikasi"}
_THINKING={"plan","rencana","strategy","strategi","reason","analisis","analyze","arsitektur","architecture","design","tradeoff","decide","putuskan","pilih","why","kenapa","bagaimana"}
_CRYSTALLIZE={"gas","implement","kerjakan","lakukan","jadikan task","buatkan","fix","repair","merge","commit","roro jonggrang","trabas","lanjutkan"}
_STOP={"yang","dan","atau","untuk","dengan","dari","ini","itu","the","to","of","in","on","is","are","for","gw","gue","aku","saya","lu","kamu","please","tolong"}

def _terms(text): return {w for w in re.findall(r"[a-zA-Z0-9_+-]{2,}",str(text or "").lower()) if w not in _STOP}

def select_work_mode(prompt,requested_mode="thinking",policy="manual"):
    requested=str(requested_mode or "thinking").strip().lower(); policy=str(policy or "manual").strip().lower()
    if policy not in AUTO_VALUES:
        return {"policy":"manual","requested":requested,"selected":requested if requested in WORK_MODES else "thinking","reason":"manual_override"}
    terms=_terms(prompt); scores={"coding":len(terms&_CODING),"research":len(terms&_RESEARCH),"thinking":len(terms&_THINKING)}
    best=max(scores,key=lambda n:(scores[n],-WORK_MODES.index(n)))
    if scores[best]==0: best="thinking"
    return {"policy":"auto","requested":requested,"selected":best,"reason":"prompt_intent","scores":scores}

def normalize_authority(authority):
    value=str(authority or "think").strip().lower(); return value if value in AUTHORITY_LEVELS else "think"

def should_crystallize(prompt):
    text=str(prompt or "").strip().lower(); return bool(text) and any(h in text for h in _CRYSTALLIZE)

@dataclass(frozen=True)
class TaskState:
    objective:str; constraints:tuple[str,...]; accepted_decisions:tuple[str,...]; rejected_options:tuple[str,...]; open_questions:tuple[str,...]; authority:str; exit_condition:str; status:str; updated_at:str
    def as_dict(self):
        data=asdict(self)
        for key in ("constraints","accepted_decisions","rejected_options","open_questions"): data[key]=list(data[key])
        return data

def crystallize_task_state(prompt,previous=None,authority="think"):
    if not should_crystallize(prompt): return previous
    prior=dict(previous or {}); text=" ".join(str(prompt or "").split())
    return TaskState(text[:1200],tuple(prior.get("constraints") or ()),tuple(prior.get("accepted_decisions") or ()),tuple(prior.get("rejected_options") or ()),tuple(prior.get("open_questions") or ()),normalize_authority(authority),str(prior.get("exit_condition") or "Return a verified result or an exact blocker/checkpoint."),"active",datetime.now(timezone.utc).isoformat()).as_dict()

def retrieve_relevant_chats(rows,query,limit=6):
    query_terms=_terms(query); ranked=[]
    for index,row in enumerate(rows or []):
        overlap=len(query_terms&_terms(str(row.get("prompt") or "")+" "+str(row.get("final_answer") or "")))
        if overlap: ranked.append((overlap,index,row))
    ranked.sort(key=lambda item:(item[0],item[1]),reverse=True)
    return [row for _,_,row in ranked[:max(0,int(limit))]]

def format_retrieved_context(rows,max_chars=5000):
    chunks=[f"[session:{row.get('session_id','')}] Q: {str(row.get('prompt') or '')[:500]}\nA: {str(row.get('final_answer') or '')[:900]}" for row in rows or []]
    return "\n\n".join(chunks)[:max_chars]

AUTO_IDENTITY_ORDER={"coding":("qwen","gpt","claude","deepseek","gpt-oss","gemini","llama","kimi","grok"),"research":("gemini","claude","gpt","qwen","deepseek","kimi","grok","gpt-oss","llama"),"thinking":("claude","gpt","gemini","qwen","deepseek","kimi","grok","gpt-oss","llama")}
def select_auto_identities(mode,available,count=1):
    available_set=set(available or []); order=AUTO_IDENTITY_ORDER.get(str(mode or "thinking").lower(),AUTO_IDENTITY_ORDER["thinking"]); selected=[i for i in order if i in available_set]; selected.extend(sorted(available_set-set(order))); return selected[:max(1,int(count))]
