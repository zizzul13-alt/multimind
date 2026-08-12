"""
Multi-agent debate orchestrator - Decoupled Agent-Centric Collaboration Pipeline (Task 3.1)
Draft (Agent A) -> Review (Agent B) -> Improve (Agent C) -> Release Gate
Collaboration stages are independent of the number of selected providers.
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

            # ===== 1. PREPARE ALL CONFIGURED PROVIDERS =====
            all_providers = []
            if self.cloudflare:
                all_providers.append(("cloudflare", "☁️ Cloudflare", self.cloudflare))
            if self.groq:
                all_providers.append(("groq", "⚡ Groq", self.groq))
            if self.openrouter:
                all_providers.append(("openrouter", "🌐 OpenRouter", self.openrouter))
            if self.huggingface:
                all_providers.append(("huggingface", "🤗 HuggingFace", self.huggingface))
            if self.deepseek:
                all_providers.append(("deepseek", "🐳 DeepSeek", self.deepseek))
            if self.gemini:
                all_providers.append(("gemini", "🔍 Gemini", self.gemini))

            if not all_providers:
                raise ValueError("No providers configured on DebateOrchestrator")

            # ===== 2. BUILD EXACTLY THREE COLLABORATION STAGES =====
            # 3 stages: 0 = Draft, 1 = Review, 2 = Improve
            # Decoupled from the count of chosen agents (uses modulo round-robin)
            active_role_agents = []
            for stage_idx in range(3):
                active_id = agents[stage_idx % len(agents)]

                primary_tuple = next((p for p in all_providers if p[0] == active_id), None)
                if not primary_tuple:
                    primary_tuple = all_providers[0]
                    active_id = primary_tuple[0]

                providers_for_router = [primary_tuple[2]]
                for p in all_providers:
                    if p[0] != active_id:
                        providers_for_router.append(p[2])

                router = ModelRouter(providers_for_router)
                role_name = self._get_role_name(mode, stage_idx)
                system_prompt = self._draft_prompt(mode) if active_id != "gemini" else self._full_prompt(mode)

                role_agent = RoleAgent(
                    role=role_name,
                    skill=system_prompt,
                    router=router
                )

                active_role_agents.append({
                    "agent": role_agent,
                    "id": active_id,
                    "max_tokens": 8192 if active_id == "gemini" else (2048 if active_id == "huggingface" else 4096)
                })

            # ===== 3. COLLABORATION PIPELINE =====
            draft_text = ""
            review_text = ""
            improve_text = ""

            for stage_idx, item in enumerate(active_role_agents):
                agent_inst = item["agent"]
                max_tokens = item["max_tokens"]
                agent_id = item["id"]

                # Gemini fallback check
                if agent_id == "gemini" and improve_text:
                    continue

                try:
                    if stage_idx == 0:
                        # --- STAGE 1: DRAFT ---
                        response = agent_inst.execute(
                            task=full_prompt,
                            mode=mode,
                            max_tokens=max_tokens
                        )
                        provider_name = response.get("agent", "Unknown Provider")
                        response["agent"] = f"{agent_inst.role} ({provider_name})"

                        if response.get("status") == "success" and response.get("text") and len(response.get("text", "")) > 50:
                            draft_text = response.get("text", "")

                    elif stage_idx == 1:
                        # --- STAGE 2: REVIEW (Receives user task + draft) ---
                        task_for_agent_b = f"""You are a reviewer. Your task is to review and critique the draft response generated for the user task below.

--- ORIGINAL TASK ---
{full_prompt}

--- DRAFT RESPONSE TO REVIEW ---
{draft_text}

---
Provide a constructive critique, identifying issues, security/performance concerns, and suggested improvements."""

                        response = agent_inst.execute(
                            task=task_for_agent_b,
                            mode=mode,
                            max_tokens=max_tokens
                        )
                        provider_name = response.get("agent", "Unknown Provider")
                        response["agent"] = f"{agent_inst.role} ({provider_name})"

                        if response.get("status") == "success" and response.get("text") and len(response.get("text", "")) > 50:
                            review_text = response.get("text", "")

                    else:
                        # --- STAGE 3: IMPROVE (Receives user task + draft + review) ---
                        task_for_agent_c = f"""You are an improver. Your task is to produce the final, polished, and significantly improved answer based on the original user task, the initial draft, and the peer critique provided below.

--- ORIGINAL TASK ---
{full_prompt}

--- INITIAL DRAFT ---
{draft_text}

--- PEER CRITIQUE ---
{review_text}

---
Generate the best possible final response, resolving any identified issues and incorporating improvements."""

                        response = agent_inst.execute(
                            task=task_for_agent_c,
                            mode=mode,
                            max_tokens=max_tokens
                        )
                        provider_name = response.get("agent", "Unknown Provider")
                        response["agent"] = f"{agent_inst.role} ({provider_name})"

                        if response.get("status") == "success" and response.get("text") and len(response.get("text", "")) > 50:
                            improve_text = response.get("text", "")

                    debate_log["responses"].append(response)
                    debate_log["total_tokens"] += response.get("tokens", 0)
                    debate_log["total_cost"] += response.get("cost", 0.0)

                except Exception as e:
                    debate_log["responses"].append({
                        "status": "error",
                        "text": str(e)[:100],
                        "agent": f"{agent_inst.role} (Error)",
                        "tokens": 0,
                        "cost": 0.0
                    })

            # ===== GABUNGIN RESPONSES ONLY FOR BACKWARD LOGS/METADATA =====
            # The final displayed answer must come solely from the improved candidate (if available) or draft (if fallback)
            candidate_for_gate = improve_text if improve_text else (draft_text if draft_text else "")

            # ===== RELEASE GATE CHECK =====
            if candidate_for_gate and "❌" not in candidate_for_gate[:5]:
                passed, issues, score = ReleaseGate.check(candidate_for_gate, mode)
                debate_log["gate_score"] = score
                debate_log["gate_issues"] = issues
                debate_log["gate_passed"] = passed

                gate_header = f"✅ **Quality Check Passed** ({ReleaseGate.get_badge(score)})" if passed else f"⚠️ **Quality Warning** ({ReleaseGate.get_badge(score)})"

                # Final Answer strictly contains the improved candidate response
                final_answer = f"""{gate_header}

{candidate_for_gate}"""

                if not passed:
                    final_answer += f"\n\n---\n**Issues Found:**\n" + "\n".join(issues)
            else:
                final_answer = candidate_for_gate if candidate_for_gate else "❌ Semua agent gagal merespons. Coba lagi nanti."

            debate_log["final_answer"] = final_answer
            debate_log["status"] = "success"
            debate_log["end_time"] = datetime.now().isoformat()

        except Exception as e:
            error_msg = str(e)[:200]
            error_logger.log("DEBATE_ERROR", str(e))
            debate_log["status"] = "error"
            debate_log["final_answer"] = f"Error: {error_msg}"

        return debate_log

    def _get_role_name(self, mode, index):
        roles_map = {
            "coding": [
                "💻 Lead Developer",
                "🏗️ Senior Architect",
                "🔍 Code Reviewer",
                "⚙️ DevOps Engineer"
            ],
            "research": [
                "📚 Lead Researcher",
                "📊 Subject Analyst",
                "🔎 Fact Checker",
                "📝 Scientific Writer"
            ],
            "thinking": [
                "🧠 Systems Thinker",
                "🧩 Logic Validator",
                "🎯 Strategic Analyst",
                "⚖️ Cognitive Analyst"
            ]
        }
        roles = roles_map.get(mode, [
            "🤖 Primary Expert",
            "👥 Peer Reviewer",
            "⚖️ Critical Critic",
            "💡 Assistant"
        ])
        return roles[index % len(roles)]

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
