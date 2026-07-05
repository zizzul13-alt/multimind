"""
Multi-agent debate orchestrator
Dengan fallback otomatis: DeepSeek → Gemini
"""
import time
from datetime import datetime
from utils.token_counter import TokenCounter
from utils.error_handler import error_logger

class DebateOrchestrator:
    """Orchestrate multi-agent debate dengan fallback"""

    def __init__(self, gemini_agent, deepseek_agent=None):
        self.gemini = gemini_agent
        self.deepseek = deepseek_agent

    def debate(self, prompt, context="", mode="coding", rounds=1, agents=None):
        """Run debate - otomatis fallback ke Gemini kalau DeepSeek error"""
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
            "start_time": datetime.now().isoformat(),
            "fallback_used": False
        }

        try:
            full_prompt = prompt
            if context:
                full_prompt = f"CONTEXT:\n{context}\n\nTASK:\n{prompt}"

            # ===== ROUND 1: COBA DEEPSEEK DULU =====
            if "deepseek" in agents and self.deepseek:
                try:
                    response = self.deepseek.generate(
                        prompt=full_prompt,
                        system_prompt=self._get_system_prompt(mode),
                        max_tokens=1500
                    )

                    if response.get("status") == "success":
                        debate_log["responses"].append(response)
                        debate_log["total_tokens"] += response.get("tokens", 0)
                        debate_log["total_cost"] += response.get("cost", 0)
                    else:
                        # DeepSeek error → fallback ke Gemini
                        raise Exception(response.get("text", "DeepSeek failed"))

                except Exception as e:
                    # FALLBACK KE GEMINI
                    error_logger.log("DEEPSEEK_FALLBACK", str(e))
                    debate_log["fallback_used"] = True

                    if self.gemini:
                        response = self.gemini.generate(
                            prompt=full_prompt,
                            system_prompt=self._get_system_prompt(mode),
                            max_tokens=1500
                        )
                        response["agent"] = "Gemini (fallback from DeepSeek)"
                        debate_log["responses"].append(response)
                        debate_log["total_tokens"] += response.get("tokens", 0)

            # ===== KALAU GA ADA DEEPSEEK, LANGSUNG GEMINI =====
            elif self.gemini:
                response = self.gemini.generate(
                    prompt=full_prompt,
                    system_prompt=self._get_system_prompt(mode),
                    max_tokens=1500
                )
                debate_log["responses"].append(response)
                debate_log["total_tokens"] += response.get("tokens", 0)

            # ===== ROUND 2 (OPTIONAL): REVIEW PAKAI GEMINI =====
            if rounds >= 2 and self.gemini and debate_log["responses"]:
                first_response = debate_log["responses"][0].get("text", "")
                if first_response:
                    try:
                        review = self.gemini.generate(
                            prompt=f"Original task:\n{full_prompt[:1000]}\n\nResponse to review:\n{first_response[:1500]}\n\nProvide a brief critique and suggest improvements:",
                            max_tokens=500
                        )
                        review["agent"] = "Gemini (Reviewer)"
                        debate_log["responses"].append(review)
                        debate_log["total_tokens"] += review.get("tokens", 0)
                    except:
                        pass

            # ===== SYNTHESIZE FINAL ANSWER =====
            if debate_log["responses"]:
                final = debate_log["responses"][-1]  # Ambil response terakhir
                debate_log["final_answer"] = final.get("text", "No response generated")
            elif self.gemini:
                # Last resort: Gemini langsung
                final = self.gemini.generate(prompt=full_prompt, max_tokens=1000)
                debate_log["final_answer"] = final.get("text", "No response")
                debate_log["responses"].append(final)
            else:
                debate_log["final_answer"] = "No AI agent available. Please check API keys."

            debate_log["status"] = "success"
            debate_log["end_time"] = datetime.now().isoformat()

        except Exception as e:
            error_msg = str(e)[:200]
            error_logger.log("DEBATE_CRITICAL", str(e))
            debate_log["status"] = "error"
            debate_log["error"] = error_msg
            debate_log["final_answer"] = f"Sorry, an error occurred: {error_msg}. Please try again."

        return debate_log

    def _get_system_prompt(self, mode):
        """Get system prompt based on mode"""
        prompts = {
            "coding": "You are an EXPERT CODER. Write clean, working code with brief explanation.",
            "research": "You are a RESEARCHER. Provide comprehensive analysis with key points.",
            "thinking": "You are a SYSTEMS THINKER. Break down problems step-by-step."
        }
        return prompts.get(mode, prompts["coding"])
