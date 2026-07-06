"""
Multi-agent debate orchestrator
Pola: Draft (Groq/Cloudflare/OpenRouter/Coze) → Langsung pakai
Gemini HANYA fallback terakhir
"""
import time
from datetime import datetime
from utils.token_counter import TokenCounter
from utils.error_handler import error_logger

class DebateOrchestrator:
    """Orchestrate multi-agent debate"""

    def __init__(self, gemini_agent, deepseek_agent=None, groq_agent=None, cloudflare_agent=None, openrouter_agent=None, coze_agent=None):
        self.gemini = gemini_agent
        self.deepseek = deepseek_agent
        self.groq = groq_agent
        self.cloudflare = cloudflare_agent
        self.openrouter = openrouter_agent
        self.coze = coze_agent

    def debate(self, prompt, context="", mode="coding", rounds=1, agents=None):
        if not agents:
            agents = ["groq"]

        debate_log = {
            "prompt": prompt, "context": context, "mode": mode,
            "rounds": rounds, "agents": agents, "responses": [],
            "total_tokens": 0, "total_cost": 0.0,
            "start_time": datetime.now().isoformat()
        }

        try:
            full_prompt = prompt
            if context:
                full_prompt = f"CONTEXT:\n{context}\n\nTASK:\n{prompt}"

            draft_text = ""
            draft_agent = ""

            # ===== COZE =====
            if "coze" in agents and self.coze:
                import streamlit as st
                complexity = st.session_state.get("coze_complexity", 1)
                try:
                    response = self.coze.generate(prompt=full_prompt, system_prompt=self._draft_prompt(mode), complexity=complexity, max_tokens=4096)
                    response["agent"] = "Coze"
                    debate_log["responses"].append(response)
                    debate_log["total_tokens"] += response.get("tokens", 0)
                    debate_log["total_cost"] += response.get("cost", 0)
                    if response.get("status") == "success":
                        draft_text = response.get("text", "")
                        draft_agent = "Coze"
                except Exception as e:
                    debate_log["responses"].append({"status": "error", "text": str(e)[:100], "agent": "Coze", "tokens": 0, "cost": 0})
                st.session_state.coze_confirmed = False

            # ===== GROQ =====
            if not draft_text and "groq" in agents and self.groq:
                try:
                    response = self.groq.generate(prompt=full_prompt, system_prompt=self._draft_prompt(mode), max_tokens=4096)
                    response["agent"] = "Groq"
                    debate_log["responses"].append(response)
                    debate_log["total_tokens"] += response.get("tokens", 0)
                    if response.get("status") == "success":
                        draft_text = response.get("text", "")
                        draft_agent = "Groq"
                except Exception as e:
                    debate_log["responses"].append({"status": "error", "text": str(e)[:100], "agent": "Groq", "tokens": 0, "cost": 0})

            # ===== CLOUDFLARE =====
            if not draft_text and "cloudflare" in agents and self.cloudflare:
                try:
                    response = self.cloudflare.generate(prompt=full_prompt, system_prompt=self._draft_prompt(mode), mode=mode, max_tokens=4096)
                    response["agent"] = "Cloudflare"
                    debate_log["responses"].append(response)
                    debate_log["total_tokens"] += response.get("tokens", 0)
                    if response.get("status") == "success":
                        draft_text = response.get("text", "")
                        draft_agent = "Cloudflare"
                except Exception as e:
                    debate_log["responses"].append({"status": "error", "text": str(e)[:100], "agent": "Cloudflare", "tokens": 0, "cost": 0})

            # ===== OPENROUTER =====
            if not draft_text and "openrouter" in agents and self.openrouter:
                try:
                    response = self.openrouter.generate(prompt=full_prompt, system_prompt=self._draft_prompt(mode), mode=mode, max_tokens=4096)
                    response["agent"] = "OpenRouter"
                    debate_log["responses"].append(response)
                    debate_log["total_tokens"] += response.get("tokens", 0)
                    if response.get("status") == "success":
                        draft_text = response.get("text", "")
                        draft_agent = "OpenRouter"
                except Exception as e:
                    debate_log["responses"].append({"status": "error", "text": str(e)[:100], "agent": "OpenRouter", "tokens": 0, "cost": 0})

            # ===== DEEPSEEK =====
            if not draft_text and "deepseek" in agents and self.deepseek:
                try:
                    response = self.deepseek.generate(prompt=full_prompt, system_prompt=self._draft_prompt(mode), max_tokens=4096)
                    response["agent"] = "DeepSeek"
                    debate_log["responses"].append(response)
                    debate_log["total_tokens"] += response.get("tokens", 0)
                    debate_log["total_cost"] += response.get("cost", 0)
                    if response.get("status") == "success":
                        draft_text = response.get("text", "")
                        draft_agent = "DeepSeek"
                except Exception as e:
                    debate_log["responses"].append({"status": "error", "text": str(e)[:100], "agent": "DeepSeek", "tokens": 0, "cost": 0})

            # ===== HASIL =====
            if draft_text and len(draft_text) > 50:
                # Ada draft → langsung pakai! (HEMAT GEMINI!)
                debate_log["final_answer"] = draft_text
            elif self.gemini:
                # Semua agent gagal → Gemini fallback terakhir
                response = self.gemini.generate(prompt=full_prompt, system_prompt=self._full_prompt(mode), max_tokens=8192)
                response["agent"] = "Gemini (Fallback)"
                debate_log["responses"].append(response)
                debate_log["total_tokens"] += response.get("tokens", 0)
                debate_log["final_answer"] = response.get("text", "")
            else:
                debate_log["final_answer"] = "No AI agent available. Please check API keys."

            debate_log["status"] = "success"
            debate_log["end_time"] = datetime.now().isoformat()

        except Exception as e:
            error_msg = str(e)[:200]
            error_logger.log("DEBATE_ERROR", str(e))
            debate_log["status"] = "error"
            debate_log["final_answer"] = f"Error: {error_msg}"

        return debate_log

    def _draft_prompt(self, mode):
        prompts = {
            "coding": "Write code solution. Be brief.",
            "research": "Provide key points. Be concise.",
            "thinking": "Break down step-by-step. Keep each step short."
        }
        return prompts.get(mode, prompts["coding"])

    def _full_prompt(self, mode):
        prompts = {
            "coding": "You are an EXPERT CODER. Write clean, working code with explanation.",
            "research": "You are a RESEARCHER. Provide comprehensive analysis.",
            "thinking": "You are a SYSTEMS THINKER. Break down problems step-by-step. Be thorough and complete."
        }
        return prompts.get(mode, prompts["coding"])
