"""
Multi-agent debate orchestrator
Semua agent dijalankan + response digabungin + Release Gates + Gemini fallback
"""
import time
from datetime import datetime
from utils.token_counter import TokenCounter
from utils.error_handler import error_logger
from core.release_gate import ReleaseGate


class DebateOrchestrator:
    """Orchestrate multi-agent debate"""

    def __init__(self, gemini_agent, deepseek_agent=None, groq_agent=None, cloudflare_agent=None, openrouter_agent=None, huggingface_agent=None, coze_agent=None):
        self.gemini = gemini_agent
        self.deepseek = deepseek_agent
        self.groq = groq_agent
        self.cloudflare = cloudflare_agent
        self.openrouter = openrouter_agent
        self.huggingface = huggingface_agent
        self.coze = coze_agent

    def debate(self, prompt, context="", mode="coding", rounds=1, agents=None):
        debate_log = {
            "prompt": prompt, "responses": [
                {"agent": "TEST Cloudflare", "status": "success", "text": "Ini test Cloudflare", "tokens": 3, "cost": 0},
                {"agent": "TEST Gemini", "status": "success", "text": "Ini test Gemini", "tokens": 3, "cost": 0},
            ],
            "final_answer": "TEST FINAL ANSWER",
            "total_tokens": 6,
            "total_cost": 0.0
        }
        return debate_log

        # DEBUG EKSTRIM
        print(f"DEBUG: Agents yang dicentang: {agents}")
        print(f"DEBUG: Cloudflare exists: {self.cloudflare is not None}")
        print(f"DEBUG: Gemini exists: {self.gemini is not None}")
        print(f"DEBUG: Groq exists: {self.groq is not None}")
        print(f"DEBUG: OpenRouter exists: {self.openrouter is not None}")
        print(f"DEBUG: HuggingFace exists: {self.huggingface is not None}")
        print(f"DEBUG: DeepSeek exists: {self.deepseek is not None}")

        try:
            full_prompt = prompt
            if context:
                full_prompt = f"CONTEXT:\n{context}\n\nTASK:\n{prompt}"

            draft_text = ""

            # ===== 1. CLOUDFLARE =====
            if "cloudflare" in agents and self.cloudflare:
                print(f"DEBUG: Cloudflare section START")
                try:
                    response = self.cloudflare.generate(prompt=full_prompt, system_prompt=self._draft_prompt(mode), mode=mode, max_tokens=4096)
                    print(f"DEBUG: Cloudflare response status: {response.get('status')}")
                    print(f"DEBUG: Cloudflare response text length: {len(response.get('text', ''))}")
                    response["agent"] = "☁️ Cloudflare"
                    debate_log["responses"].append(response)
                    print(f"DEBUG: Cloudflare APPENDED. Total responses: {len(debate_log['responses'])}")
                    debate_log["total_tokens"] += response.get("tokens", 0)
                    if response.get("status") == "success" and response.get("text") and len(response.get("text", "")) > 50:
                        draft_text = response.get("text", "")
                except Exception as e:
                    print(f"DEBUG: Cloudflare EXCEPTION: {e}")
                    debate_log["responses"].append({"status": "error", "text": str(e)[:100], "agent": "☁️ Cloudflare", "tokens": 0, "cost": 0})

            # ===== 2. OPENROUTER =====
            if "openrouter" in agents and self.openrouter:
                print(f"DEBUG: OpenRouter section START")
                try:
                    response = self.openrouter.generate(prompt=full_prompt, system_prompt=self._draft_prompt(mode), mode=mode, max_tokens=4096)
                    print(f"DEBUG: OpenRouter response status: {response.get('status')}")
                    response["agent"] = "🌐 OpenRouter"
                    debate_log["responses"].append(response)
                    print(f"DEBUG: OpenRouter APPENDED. Total responses: {len(debate_log['responses'])}")
                    debate_log["total_tokens"] += response.get("tokens", 0)
                except Exception as e:
                    print(f"DEBUG: OpenRouter EXCEPTION: {e}")
                    debate_log["responses"].append({"status": "error", "text": str(e)[:100], "agent": "🌐 OpenRouter", "tokens": 0, "cost": 0})

            # ===== 3. GROQ =====
            if "groq" in agents and self.groq:
                print(f"DEBUG: Groq section START")
                try:
                    response = self.groq.generate(prompt=full_prompt, system_prompt=self._draft_prompt(mode), max_tokens=4096)
                    print(f"DEBUG: Groq response status: {response.get('status')}")
                    response["agent"] = "⚡ Groq"
                    debate_log["responses"].append(response)
                    print(f"DEBUG: Groq APPENDED. Total responses: {len(debate_log['responses'])}")
                    debate_log["total_tokens"] += response.get("tokens", 0)
                except Exception as e:
                    print(f"DEBUG: Groq EXCEPTION: {e}")
                    debate_log["responses"].append({"status": "error", "text": str(e)[:100], "agent": "⚡ Groq", "tokens": 0, "cost": 0})

            # ===== 4. HUGGINGFACE =====
            if "huggingface" in agents and self.huggingface:
                print(f"DEBUG: HuggingFace section START")
                try:
                    response = self.huggingface.generate(prompt=full_prompt, system_prompt=self._draft_prompt(mode), mode=mode, max_tokens=2048)
                    print(f"DEBUG: HuggingFace response status: {response.get('status')}")
                    response["agent"] = "🤗 HuggingFace"
                    debate_log["responses"].append(response)
                    print(f"DEBUG: HuggingFace APPENDED. Total responses: {len(debate_log['responses'])}")
                    debate_log["total_tokens"] += response.get("tokens", 0)
                except Exception as e:
                    print(f"DEBUG: HuggingFace EXCEPTION: {e}")
                    debate_log["responses"].append({"status": "error", "text": str(e)[:100], "agent": "🤗 HuggingFace", "tokens": 0, "cost": 0})

            # ===== 5. DEEPSEEK =====
            if "deepseek" in agents and self.deepseek:
                print(f"DEBUG: DeepSeek section START")
                try:
                    response = self.deepseek.generate(prompt=full_prompt, system_prompt=self._draft_prompt(mode), max_tokens=4096)
                    print(f"DEBUG: DeepSeek response status: {response.get('status')}")
                    response["agent"] = "🐳 DeepSeek"
                    debate_log["responses"].append(response)
                    print(f"DEBUG: DeepSeek APPENDED. Total responses: {len(debate_log['responses'])}")
                    debate_log["total_tokens"] += response.get("tokens", 0)
                    debate_log["total_cost"] += response.get("cost", 0)
                except Exception as e:
                    print(f"DEBUG: DeepSeek EXCEPTION: {e}")
                    debate_log["responses"].append({"status": "error", "text": str(e)[:100], "agent": "🐳 DeepSeek", "tokens": 0, "cost": 0})

            # ===== 6. GEMINI =====
            if "gemini" in agents and self.gemini:
                print(f"DEBUG: Gemini section START")
                try:
                    response = self.gemini.generate(prompt=full_prompt, system_prompt=self._full_prompt(mode), max_tokens=8192)
                    print(f"DEBUG: Gemini response status: {response.get('status')}")
                    response["agent"] = "🔍 Gemini"
                    debate_log["responses"].append(response)
                    print(f"DEBUG: Gemini APPENDED. Total responses: {len(debate_log['responses'])}")
                    debate_log["total_tokens"] += response.get("tokens", 0)
                    if not draft_text and response.get("status") == "success" and response.get("text") and len(response.get("text", "")) > 50:
                        draft_text = response.get("text", "")
                except Exception as e:
                    print(f"DEBUG: Gemini EXCEPTION: {e}")
                    debate_log["responses"].append({"status": "error", "text": str(e)[:100], "agent": "🔍 Gemini", "tokens": 0, "cost": 0})

            print(f"DEBUG: FINAL responses count: {len(debate_log['responses'])}")

            # ===== GABUNGIN SEMUA RESPONSE =====
            all_texts = []
            for r in debate_log["responses"]:
                if r.get("status") == "success" and r.get("text") and len(r.get("text", "")) > 50:
                    all_texts.append(f"### {r.get('agent', 'Unknown')}\n\n{r.get('text', '')}")

            if all_texts:
                final_answer = "\n\n---\n\n".join(all_texts)
            elif draft_text and len(draft_text.strip()) > 50:
                final_answer = draft_text
            else:
                final_answer = "❌ Semua agent gagal merespons. Coba lagi nanti."

            # ===== RELEASE GATE CHECK =====
            if final_answer and "❌" not in final_answer[:5]:
                passed, issues, score = ReleaseGate.check(final_answer, mode)
                debate_log["gate_score"] = score
                debate_log["gate_issues"] = issues
                debate_log["gate_passed"] = passed

                if not passed:
                    final_answer = f"""⚠️ **Quality Warning** ({ReleaseGate.get_badge(score)})

{final_answer}

---
**Issues Found:**
{chr(10).join(issues)}"""
                else:
                    final_answer = f"""✅ **Quality Check Passed** ({ReleaseGate.get_badge(score)})

{final_answer}"""

            debate_log["final_answer"] = final_answer
            debate_log["status"] = "success"
            debate_log["end_time"] = datetime.now().isoformat()

        except Exception as e:
            error_msg = str(e)[:200]
            print(f"DEBUG: CRITICAL ERROR: {error_msg}")
            error_logger.log("DEBATE_ERROR", str(e))
            debate_log["status"] = "error"
            debate_log["final_answer"] = f"Error: {error_msg}"

        print(f"DEBUG: RETURN debate_log with {len(debate_log['responses'])} responses")
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
