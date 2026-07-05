"""
Multi-agent debate orchestrator
Pola: Groq/DeepSeek (draft) → Gemini (review & lengkapi)
"""
import time
from datetime import datetime
from utils.token_counter import TokenCounter
from utils.error_handler import error_logger

class DebateOrchestrator:
    """Orchestrate multi-agent debate dengan pola Draft → Review"""

    def __init__(self, gemini_agent, deepseek_agent=None, groq_agent=None):
        self.gemini = gemini_agent
        self.deepseek = deepseek_agent
        self.groq = groq_agent

    def debate(self, prompt, context="", mode="coding", rounds=1, agents=None):
        """Run debate - Draft (Groq/DeepSeek) → Review (Gemini)"""
        if not agents:
            agents = ["gemini"]

        debate_log = {
            "prompt": prompt,
            "context": context,
            "mode": mode,
            "rounds": rounds,
            "agents": agents,
            "responses": [],
            "total_tokens": 0,
            "total_cost": 0.0,
            "start_time": datetime.now().isoformat()
        }

        try:
            full_prompt = prompt
            if context:
                full_prompt = f"CONTEXT:\n{context}\n\nTASK:\n{prompt}"

            draft_response = None
            draft_agent = None

            # ===== STEP 1: BUAT DRAFT =====
            # Prioritas: Groq → DeepSeek → Gemini

            if "groq" in agents and self.groq:
                try:
                    response = self.groq.generate(
                        prompt=full_prompt,
                        system_prompt=self._get_draft_prompt(mode),
                        max_tokens=2048
                    )
                    if response.get("status") == "success":
                        draft_response = response
                        draft_agent = "Groq"
                        debate_log["responses"].append(response)
                        debate_log["total_tokens"] += response.get("tokens", 0)
                except:
                    pass

            if not draft_response and "deepseek" in agents and self.deepseek:
                try:
                    response = self.deepseek.generate(
                        prompt=full_prompt,
                        system_prompt=self._get_draft_prompt(mode),
                        max_tokens=2048
                    )
                    if response.get("status") == "success":
                        draft_response = response
                        draft_agent = "DeepSeek"
                        debate_log["responses"].append(response)
                        debate_log["total_tokens"] += response.get("tokens", 0)
                        debate_log["total_cost"] += response.get("cost", 0)
                except:
                    pass

            if not draft_response and "gemini" in agents and self.gemini:
                response = self.gemini.generate(
                    prompt=full_prompt,
                    system_prompt=self._get_draft_prompt(mode),
                    max_tokens=2048
                )
                draft_response = response
                draft_agent = "Gemini"
                debate_log["responses"].append(response)
                debate_log["total_tokens"] += response.get("tokens", 0)

            # ===== STEP 2: GEMINI REVIEW & LENGKAPI =====
            if draft_response and "gemini" in agents and self.gemini:
                draft_text = draft_response.get("text", "")
                
                if len(draft_text) > 50:
                    review_prompt = f"""TASK: {full_prompt[:300]}

DRAFT from {draft_agent} (may be truncated):
{draft_text[:2000]}

YOUR JOB:
- Continue from where the draft stops
- Complete ALL unfinished points
- Add missing analysis
- Provide ONE complete, well-structured final answer

FINAL COMPLETE ANSWER:"""

                    review = self.gemini.generate(
                        prompt=review_prompt,
                        max_tokens=4096
                    )
                    review["agent"] = f"Gemini (reviewed {draft_agent})"
                    debate_log["responses"].append(review)
                    debate_log["total_tokens"] += review.get("tokens", 0)
                    
                    debate_log["final_answer"] = review.get("text", draft_text)
                else:
                    debate_log["final_answer"] = draft_text
            elif draft_response:
                debate_log["final_answer"] = draft_response.get("text", "")
            else:
                debate_log["final_answer"] = "No AI agent available."

            debate_log["status"] = "success"
            debate_log["end_time"] = datetime.now().isoformat()

        except Exception as e:
            error_msg = str(e)[:200]
            error_logger.log("DEBATE_CRITICAL", str(e))
            debate_log["status"] = "error"
            debate_log["error"] = error_msg
            debate_log["final_answer"] = f"Sorry, an error occurred: {error_msg}."

        return debate_log

    def _get_draft_prompt(self, mode):
        """Prompt buat draft (singkat & cepat)"""
        prompts = {
            "coding": "Write code solution. Be brief. Focus on working code.",
            "research": "Provide key analysis points. Be concise but informative.",
            "thinking": "Break down step-by-step. Keep each step short."
        }
        return prompts.get(mode, prompts["coding"])
