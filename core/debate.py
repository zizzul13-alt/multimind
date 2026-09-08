"""MultiMind deliberation orchestrator.

Product invariant:

    N selected participants == N traceable participant attempts.

Participant execution is deliberately *not* routed through cross-provider fallback,
because fallback must never make one provider's response masquerade as another
selected participant. Reliability fallback remains available for utility work such
as judge/synthesis, where the actual provider used is recorded explicitly.
"""

from __future__ import annotations

import re
from datetime import datetime

from agents.role_agent import RoleAgent
from agents.router import ModelRouter, TERMINAL_PROVIDER_FAILURE_TEXT
from core.release_gate import ReleaseGate
from core.skills_manager import SkillsManager
from providers.base import BaseProvider
from utils.error_handler import error_logger


class DebateOrchestrator:
    """Orchestrate independent participants, bounded deliberation and synthesis."""

    MAX_ROUNDS = 5

    def __init__(
        self,
        gemini_agent,
        deepseek_agent=None,
        groq_agent=None,
        cloudflare_agent=None,
        openrouter_agent=None,
        huggingface_agent=None,
        coze_agent=None,
    ):
        self.gemini = gemini_agent
        self.deepseek = deepseek_agent
        self.groq = groq_agent
        self.cloudflare = cloudflare_agent
        self.openrouter = openrouter_agent
        self.huggingface = huggingface_agent
        self.coze = coze_agent
        self.skills_manager = SkillsManager()

    def debate(self, prompt, context="", mode="coding", rounds=1, agents=None, skill=None):
        requested_agents = list(agents or ["cloudflare"])
        active_agents = self._normalize_agents(requested_agents)
        effective_rounds = self._normalize_rounds(rounds)

        debate_log = {
            "prompt": prompt,
            "context": context,
            "mode": mode,
            "rounds": effective_rounds,
            "requested_agents": requested_agents,
            "agents": active_agents,
            "responses": [],
            "participants": [],
            "deliberation": [],
            "judge": {},
            "system_verdict": None,
            "total_tokens": 0,
            "total_cost": 0.0,
            "start_time": datetime.now().isoformat(),
        }

        try:
            full_prompt = self._build_full_prompt(prompt, context, skill)
            configured = self._configured_providers()
            if not configured:
                raise ValueError("No providers configured on DebateOrchestrator")

            # Phase 1: every selected participant gets exactly its own provider route.
            successful_participants = []
            for index, agent_id in enumerate(active_agents, 1):
                participant_id = f"participant-{index}-{agent_id}"
                provider = configured.get(agent_id)
                role = self._participant_role(mode, index - 1)

                if provider is None:
                    failure = self._participant_failure(
                        participant_id=participant_id,
                        requested_provider=agent_id,
                        role=role,
                        category="not_configured",
                    )
                    debate_log["participants"].append(failure)
                    debate_log["responses"].append(self._legacy_failure_response(failure))
                    continue

                response = self._execute_single_provider(
                    provider=provider,
                    role=role,
                    task=full_prompt,
                    mode=mode,
                    max_tokens=self._max_tokens(agent_id),
                )
                self._accumulate_usage(debate_log, response)

                participant = self._participant_record(
                    participant_id=participant_id,
                    requested_provider=agent_id,
                    role=role,
                    provider=provider,
                    response=response,
                )
                debate_log["participants"].append(participant)
                debate_log["responses"].append(
                    self._legacy_response(
                        response,
                        role=role,
                        phase="candidate",
                        participant_id=participant_id,
                    )
                )
                if participant["status"] == "success":
                    successful_participants.append(participant)

            if not successful_participants:
                debate_log["status"] = "error"
                debate_log["final_answer"] = TERMINAL_PROVIDER_FAILURE_TEXT
                debate_log["successful_participants"] = 0
                debate_log["selected_participants"] = len(active_agents)
                debate_log["end_time"] = datetime.now().isoformat()
                return debate_log

            # Phase 2: rounds after 1 are real critique rounds. Each successful
            # participant critiques through its own provider only.
            for deliberation_round in range(2, effective_rounds + 1):
                comparison = self._format_participants(successful_participants)
                earlier = self._format_critiques(debate_log["deliberation"])

                for participant_index, participant in enumerate(successful_participants):
                    agent_id = participant["requested_provider"]
                    provider = configured.get(agent_id)
                    if provider is None:
                        continue

                    critique_task = self._critique_prompt(
                        original_task=full_prompt,
                        comparison=comparison,
                        earlier_critiques=earlier,
                        own_participant_id=participant["participant_id"],
                        round_number=deliberation_round,
                    )
                    role = (
                        f"{self._participant_role(mode, participant_index)} "
                        f"— Critic R{deliberation_round}"
                    )
                    response = self._execute_single_provider(
                        provider=provider,
                        role=role,
                        task=critique_task,
                        mode=mode,
                        max_tokens=min(self._max_tokens(agent_id), 2048),
                    )
                    self._accumulate_usage(debate_log, response)
                    usable = BaseProvider.has_usable_response(response)
                    critique = {
                        "round": deliberation_round,
                        "participant_id": participant["participant_id"],
                        "requested_provider": agent_id,
                        "actual_provider": (
                            response.get("agent", self._provider_label(provider))
                            if usable
                            else self._provider_label(provider)
                        ),
                        "model": getattr(provider, "model_name", self._provider_label(provider)),
                        "status": "success" if usable else "error",
                        "text": response.get("text", "") if usable else "",
                        "failure_category": (
                            response.get("failure_category") if isinstance(response, dict) else None
                        ),
                        "tokens": response.get("tokens", 0) if isinstance(response, dict) else 0,
                        "cost": response.get("cost", 0.0) if isinstance(response, dict) else 0.0,
                    }
                    debate_log["deliberation"].append(critique)
                    debate_log["responses"].append(
                        self._legacy_response(
                            response,
                            role=role,
                            phase="critique",
                            participant_id=participant["participant_id"],
                            round_number=deliberation_round,
                        )
                    )

            # Phase 3: judge/synthesis is utility machinery. It may fallback only
            # across resources the user explicitly selected and that successfully
            # participated. This prevents an unselected paid/configured provider
            # from being called invisibly by judge fallback.
            judge_eligible_providers = self._judge_provider_ids(successful_participants)
            judge_response = self._run_judge(
                configured=configured,
                eligible_provider_ids=judge_eligible_providers,
                successful_participants=successful_participants,
                critiques=debate_log["deliberation"],
                full_prompt=full_prompt,
                mode=mode,
            )
            self._accumulate_usage(debate_log, judge_response)

            judge_usable = BaseProvider.has_usable_response(judge_response)
            winner, synthesis = self._parse_judge_output(
                judge_response.get("text", "") if isinstance(judge_response, dict) else "",
                {item["participant_id"] for item in successful_participants},
            )

            if judge_usable:
                candidate_for_gate = synthesis or judge_response.get("text", "")
                debate_log["judge"] = {
                    "status": "success",
                    "eligible_providers": judge_eligible_providers,
                    "actual_provider": judge_response.get("agent", "Unknown Provider"),
                    "text": judge_response.get("text", ""),
                    "tokens": judge_response.get("tokens", 0),
                    "cost": judge_response.get("cost", 0.0),
                }
                debate_log["responses"].append(
                    self._legacy_response(
                        judge_response,
                        role=self._judge_role(mode),
                        phase="judge",
                    )
                )
                debate_log["system_verdict"] = winner
            else:
                fallback = successful_participants[0]
                candidate_for_gate = fallback["text"]
                debate_log["judge"] = {
                    "status": "error",
                    "eligible_providers": judge_eligible_providers,
                    "actual_provider": (
                        judge_response.get("agent", "Router")
                        if isinstance(judge_response, dict)
                        else "Router"
                    ),
                    "text": "",
                    "failure_category": (
                        judge_response.get("failure_category")
                        if isinstance(judge_response, dict)
                        else "provider_error"
                    ),
                    "tokens": judge_response.get("tokens", 0) if isinstance(judge_response, dict) else 0,
                    "cost": judge_response.get("cost", 0.0) if isinstance(judge_response, dict) else 0.0,
                    "fallback_participant_id": fallback["participant_id"],
                }
                debate_log["responses"].append(
                    self._legacy_response(
                        judge_response,
                        role=self._judge_role(mode),
                        phase="judge",
                    )
                )

            final_answer = self._apply_release_gate(candidate_for_gate, mode, debate_log)
            debate_log["final_answer"] = final_answer
            debate_log["status"] = "success"
            debate_log["successful_participants"] = len(successful_participants)
            debate_log["selected_participants"] = len(active_agents)
            debate_log["end_time"] = datetime.now().isoformat()

        except Exception as exc:
            error_logger.log("DEBATE_ERROR", f"exception_type={type(exc).__name__}")
            debate_log["status"] = "error"
            debate_log["final_answer"] = TERMINAL_PROVIDER_FAILURE_TEXT
            debate_log["end_time"] = datetime.now().isoformat()

        return debate_log

    def _configured_providers(self):
        configured = {
            "cloudflare": self.cloudflare,
            "groq": self.groq,
            "openrouter": self.openrouter,
            "huggingface": self.huggingface,
            "deepseek": self.deepseek,
            "gemini": self.gemini,
        }
        if self.coze:
            configured["coze"] = self.coze
        return {name: provider for name, provider in configured.items() if provider is not None}

    @staticmethod
    def _normalize_agents(agents):
        """Keep explicit order while preventing accidental duplicate participants."""
        normalized = []
        for agent in agents:
            if not isinstance(agent, str):
                continue
            agent_id = agent.strip().lower()
            if agent_id and agent_id not in normalized:
                normalized.append(agent_id)
        return normalized

    @classmethod
    def _normalize_rounds(cls, rounds):
        try:
            value = int(rounds)
        except (TypeError, ValueError):
            value = 1
        return max(1, min(cls.MAX_ROUNDS, value))

    def _build_full_prompt(self, prompt, context, skill):
        full_prompt = prompt
        if context:
            full_prompt = f"CONTEXT:\n{context}\n\nTASK:\n{prompt}"
        if skill and skill != "default":
            skill_prompt = self.skills_manager.get_skill(skill)
            if skill_prompt:
                full_prompt = f"{skill_prompt}\n\nTASK:\n{full_prompt}"
        return full_prompt

    def _execute_single_provider(self, provider, role, task, mode, max_tokens):
        """Execute exactly one provider; no cross-provider participant fallback."""
        role_agent = RoleAgent(
            role=role,
            skill=self._participant_system_prompt(mode),
            router=ModelRouter([provider]),
        )
        try:
            return role_agent.execute(task=task, mode=mode, max_tokens=max_tokens)
        except Exception as exc:
            error_logger.log(
                "DELIBERATION_PARTICIPANT_FAILURE",
                f"role={role} exception_type={type(exc).__name__}",
            )
            return {
                "status": "error",
                "text": TERMINAL_PROVIDER_FAILURE_TEXT,
                "agent": self._provider_label(provider),
                "tokens": 0,
                "cost": 0.0,
                "failure_category": "provider_exception",
                "exception_type": type(exc).__name__,
            }

    def _participant_record(self, participant_id, requested_provider, role, provider, response):
        usable = BaseProvider.has_usable_response(response)
        actual_provider = (
            response.get("agent", self._provider_label(provider))
            if usable
            else self._provider_label(provider)
        )
        return {
            "participant_id": participant_id,
            "requested_provider": requested_provider,
            "actual_provider": actual_provider,
            "model": getattr(provider, "model_name", actual_provider),
            "role": role,
            "status": "success" if usable else "error",
            "text": response.get("text", "") if usable else "",
            "failure_category": (
                response.get("failure_category") if isinstance(response, dict) else None
            ),
            "status_code": response.get("status_code") if isinstance(response, dict) else None,
            "tokens": response.get("tokens", 0) if isinstance(response, dict) else 0,
            "cost": response.get("cost", 0.0) if isinstance(response, dict) else 0.0,
        }

    @staticmethod
    def _participant_failure(participant_id, requested_provider, role, category):
        return {
            "participant_id": participant_id,
            "requested_provider": requested_provider,
            "actual_provider": None,
            "model": None,
            "role": role,
            "status": "error",
            "text": "",
            "failure_category": category,
            "status_code": None,
            "tokens": 0,
            "cost": 0.0,
        }

    @staticmethod
    def _legacy_failure_response(participant):
        return {
            "status": "error",
            "text": TERMINAL_PROVIDER_FAILURE_TEXT,
            "agent": f"{participant['role']} ({participant['requested_provider']})",
            "tokens": 0,
            "cost": 0.0,
            "phase": "candidate",
            "participant_id": participant["participant_id"],
            "requested_provider": participant["requested_provider"],
            "failure_category": participant["failure_category"],
        }

    @staticmethod
    def _legacy_response(response, role, phase, participant_id=None, round_number=None):
        response = dict(response or {})
        provider_name = response.get("agent", "Unknown Provider")
        response["agent"] = f"{role} ({provider_name})"
        response["actual_provider"] = provider_name
        response["phase"] = phase
        if participant_id:
            response["participant_id"] = participant_id
        if round_number is not None:
            response["round"] = round_number
        return response

    @staticmethod
    def _provider_label(provider):
        return getattr(provider, "name", provider.__class__.__name__)

    @staticmethod
    def _max_tokens(agent_id):
        if agent_id == "gemini":
            return 8192
        if agent_id == "huggingface":
            return 2048
        return 4096

    @staticmethod
    def _accumulate_usage(debate_log, response):
        if not isinstance(response, dict):
            return
        debate_log["total_tokens"] += response.get("tokens", 0) or 0
        debate_log["total_cost"] += response.get("cost", 0.0) or 0.0

    @staticmethod
    def _judge_provider_ids(successful_participants):
        """Bound judge utility to resources the user selected successfully.

        Gemini may be preferred when it is already one of those selected resources,
        preserving the historical high-context utility optimization without creating
        a hidden unselected-provider call.
        """
        selected = []
        for participant in successful_participants:
            provider_id = participant.get("requested_provider")
            if provider_id and provider_id not in selected:
                selected.append(provider_id)
        if "gemini" in selected:
            return ["gemini"] + [item for item in selected if item != "gemini"]
        return selected

    def _run_judge(
        self,
        configured,
        eligible_provider_ids,
        successful_participants,
        critiques,
        full_prompt,
        mode,
    ):
        providers = [
            configured[provider_id]
            for provider_id in eligible_provider_ids
            if provider_id in configured
        ]
        if not providers:
            return {
                "status": "error",
                "text": TERMINAL_PROVIDER_FAILURE_TEXT,
                "agent": "Judge Router",
                "tokens": 0,
                "cost": 0.0,
                "failure_category": "no_selected_judge_provider",
            }

        router = ModelRouter(providers)
        role_agent = RoleAgent(
            role=self._judge_role(mode),
            skill=self._judge_system_prompt(mode),
            router=router,
        )
        judge_task = self._judge_prompt(
            original_task=full_prompt,
            participants=self._format_participants(successful_participants),
            critiques=self._format_critiques(critiques),
        )
        try:
            return role_agent.execute(task=judge_task, mode=mode, max_tokens=8192)
        except Exception as exc:
            error_logger.log(
                "DELIBERATION_JUDGE_FAILURE",
                f"exception_type={type(exc).__name__}",
            )
            return {
                "status": "error",
                "text": TERMINAL_PROVIDER_FAILURE_TEXT,
                "agent": "Judge Router",
                "tokens": 0,
                "cost": 0.0,
                "failure_category": "provider_exception",
                "exception_type": type(exc).__name__,
            }

    @staticmethod
    def _format_participants(participants):
        chunks = []
        for item in participants:
            chunks.append(
                "\n".join(
                    [
                        f"--- {item['participant_id']} ---",
                        f"Requested provider: {item['requested_provider']}",
                        f"Actual provider/model: {item['actual_provider']}",
                        f"Role: {item['role']}",
                        item["text"],
                    ]
                )
            )
        return "\n\n".join(chunks)

    @staticmethod
    def _format_critiques(critiques):
        usable = [
            item
            for item in critiques
            if item.get("status") == "success" and item.get("text")
        ]
        if not usable:
            return "(none)"
        return "\n\n".join(
            f"--- Round {item['round']} / {item['participant_id']} ---\n{item['text']}"
            for item in usable
        )

    @staticmethod
    def _critique_prompt(
        original_task,
        comparison,
        earlier_critiques,
        own_participant_id,
        round_number,
    ):
        return f"""You are participating in deliberation round {round_number}.

ORIGINAL TASK:
{original_task}

INDEPENDENT PARTICIPANT CONTRIBUTIONS:
{comparison}

EARLIER CRITIQUES:
{earlier_critiques}

Your participant identity is {own_participant_id}.
Critique the panel concisely. Identify concrete correctness gaps, disagreements,
missing evidence, unsafe assumptions, or improvements. Do not merely restate your
own answer. Preserve code, numbers, filenames, constraints, and evidence when they
matter. Return only the critique."""

    @staticmethod
    def _judge_prompt(original_task, participants, critiques):
        return f"""You are MultiMind's synthesis judge. The participant answers below
are independent contributions to the same user task. Critiques are advisory.

ORIGINAL TASK:
{original_task}

PARTICIPANTS:
{participants}

CRITIQUES:
{critiques}

Evaluate correctness, completeness, consistency, relevance, evidence, and any
material disagreements. Then produce a best synthesis without erasing useful
minority corrections.

Your response MUST use this shape:
WINNER: <exact participant-id from above>
FINAL:
<standalone final answer to the user>

The winner indicates the strongest base contribution. The FINAL answer may combine
material contributions from multiple participants."""

    @staticmethod
    def _parse_judge_output(text, valid_participant_ids):
        if not isinstance(text, str) or not text.strip():
            return None, ""

        winner = None
        match = re.search(r"(?im)^\s*WINNER\s*:\s*([^\s]+)\s*$", text)
        if match:
            candidate = match.group(1).strip()
            if candidate in valid_participant_ids:
                winner = candidate

        final_match = re.search(r"(?im)^\s*FINAL\s*:\s*", text)
        synthesis = text[final_match.end():].strip() if final_match else text.strip()
        return winner, synthesis

    def _apply_release_gate(self, candidate_for_gate, mode, debate_log):
        if not candidate_for_gate:
            return TERMINAL_PROVIDER_FAILURE_TEXT
        if "❌" in candidate_for_gate[:5]:
            return candidate_for_gate

        passed, issues, score = ReleaseGate.check(candidate_for_gate, mode)
        debate_log["gate_score"] = score
        debate_log["gate_issues"] = issues
        debate_log["gate_passed"] = passed

        gate_header = (
            f"✅ **Quality Check Passed** ({ReleaseGate.get_badge(score)})"
            if passed
            else f"⚠️ **Quality Warning** ({ReleaseGate.get_badge(score)})"
        )
        final_answer = f"{gate_header}\n\n{candidate_for_gate}"
        if not passed:
            final_answer += "\n\n---\n**Issues Found:**\n" + "\n".join(issues)
        return final_answer

    def _participant_role(self, mode, index):
        roles_map = {
            "coding": [
                "💻 Lead Developer",
                "🏗️ Senior Architect",
                "🔍 Code Reviewer",
                "🧪 Implementation Tester",
                "🛡️ Reliability Reviewer",
                "⚙️ Systems Integrator",
            ],
            "research": [
                "📚 Lead Researcher",
                "📊 Subject Analyst",
                "🔎 Fact Checker",
                "🧾 Evidence Reviewer",
                "🧭 Counter-Hypothesis Analyst",
                "🗂️ Synthesis Researcher",
            ],
            "thinking": [
                "🧠 Systems Thinker",
                "🧩 Logic Validator",
                "🎯 Strategic Analyst",
                "🔁 Counterfactual Analyst",
                "⚖️ Trade-off Reviewer",
                "🧱 Constraint Analyst",
            ],
        }
        roles = roles_map.get(
            mode,
            ["🤖 Primary Expert", "👥 Peer Reviewer", "⚖️ Critical Critic"],
        )
        if index < len(roles):
            return roles[index]
        return f"🤖 Panel Participant {index + 1}"

    @staticmethod
    def _judge_role(mode):
        judges_map = {
            "coding": "⚖️ Code Synthesis Judge",
            "research": "⚖️ Research Synthesis Referee",
            "thinking": "⚖️ Reasoning Synthesis Arbiter",
        }
        return judges_map.get(mode, "⚖️ Panel Synthesis Judge")

    @staticmethod
    def _participant_system_prompt(mode):
        prompts = {
            "coding": (
                "Act as an independent expert coder. Produce a concrete, correct "
                "implementation-focused answer."
            ),
            "research": (
                "Act as an independent researcher. Separate evidence, inference, "
                "uncertainty, and conclusions."
            ),
            "thinking": (
                "Act as an independent systems thinker. Analyze constraints, "
                "alternatives, and failure modes clearly."
            ),
        }
        return prompts.get(
            mode,
            "Act as an independent expert. Produce your own answer before seeing other participants.",
        )

    @staticmethod
    def _judge_system_prompt(mode):
        prompts = {
            "coding": (
                "Judge implementation quality and synthesize the strongest correct coding answer."
            ),
            "research": (
                "Judge evidence quality and synthesize the strongest research answer "
                "without inventing evidence."
            ),
            "thinking": (
                "Judge reasoning quality and synthesize a coherent answer that preserves important dissent."
            ),
        }
        return prompts.get(mode, "Judge the panel fairly and synthesize the strongest answer.")
