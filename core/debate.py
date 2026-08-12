"""
Multi-agent debate orchestrator - Agent-Centric Implementation
Order: Cloudflare → Groq → OpenRouter → HuggingFace → DeepSeek → Gemini (fallback)
"""
import time
from datetime import datetime
from utils.token_counter import TokenCounter
from utils.error_handler import error_logger
from core.release_gate import ReleaseGate
from core.skills_manager import SkillsManager
from agents.role_agent import RoleAgent
from agents.router import ModelRouter


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
        self.skills_manager = SkillsManager()

    def debate(self, prompt, context="", mode="coding", rounds=1, agents=None, skill=None):
        if not agents:
            agents = ["cloudflare"]

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
            
            # ===== APPLY SKILL =====
            if skill and skill != "default":
                skill_prompt = self.skills_manager.get_skill(skill)
                if skill_prompt:
                    full_prompt = f"{skill_prompt}\n\nTASK:\n{full_prompt}"

            draft_text = ""
            draft_agent = ""

            # ===== DYNAMIC AGENT INSTANCE BUILDER =====
            # Map legacy provider configuration to generic RoleAgent + ModelRouter instances
            provider_definitions = [
                {
                    "id": "cloudflare",
                    "name": "☁️ Cloudflare",
                    "provider": self.cloudflare,
                    "system_prompt": self._draft_prompt(mode),
                    "max_tokens": 4096
                },
                {
                    "id": "groq",
                    "name": "⚡ Groq",
                    "provider": self.groq,
                    "system_prompt": self._draft_prompt(mode),
                    "max_tokens": 4096
                },
                {
                    "id": "openrouter",
                    "name": "🌐 OpenRouter",
                    "provider": self.openrouter,
                    "system_prompt": self._draft_prompt(mode),
                    "max_tokens": 4096
                },
                {
                    "id": "huggingface",
                    "name": "🤗 HuggingFace",
                    "provider": self.huggingface,
                    "system_prompt": self._draft_prompt(mode),
                    "max_tokens": 2048
                },
                {
                    "id": "deepseek",
                    "name": "🐳 DeepSeek",
                    "provider": self.deepseek,
                    "system_prompt": self._draft_prompt(mode),
                    "max_tokens": 4096
                },
                {
                    "id": "gemini",
                    "name": "🔍 Gemini",
                    "provider": self.gemini,
                    "system_prompt": self._full_prompt(mode),
                    "max_tokens": 8192
                }
            ]

            active_role_agents = []
            for pdef in provider_definitions:
                if pdef["id"] in agents and pdef["provider"]:
                    # Bind the provider instance to a clean ModelRouter
                    router = ModelRouter([pdef["provider"]])
                    # Instantiate generic RoleAgent representing the actor role
                    agent_inst = RoleAgent(
                        role=pdef["name"],
                        skill=pdef["system_prompt"],
                        router=router
                    )
                    active_role_agents.append({
                        "agent": agent_inst,
                        "max_tokens": pdef["max_tokens"],
                        "id": pdef["id"]
                    })

            # ===== AGENT DEBATE LOOP =====
            for item in active_role_agents:
                agent_inst = item["agent"]
                max_tokens = item["max_tokens"]
                agent_id = item["id"]

                # Gemini is a fallback-only provider unless it is the only one in sequence
                if agent_id == "gemini" and draft_text:
                    continue

                try:
                    # Execute task generic Agent-centric way
                    response = agent_inst.execute(
                        task=full_prompt,
                        mode=mode,
                        max_tokens=max_tokens
                    )

                    response["agent"] = agent_inst.role
                    debate_log["responses"].append(response)
                    debate_log["total_tokens"] += response.get("tokens", 0)
                    debate_log["total_cost"] += response.get("cost", 0.0)

                    if response.get("status") == "success" and response.get("text") and len(response.get("text", "")) > 50:
                        if not draft_text:
                            draft_text = response.get("text", "")
                            draft_agent = agent_inst.role
                except Exception as e:
                    debate_log["responses"].append({
                        "status": "error",
                        "text": str(e)[:100],
                        "agent": agent_inst.role,
                        "tokens": 0,
                        "cost": 0.0
                    })

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
