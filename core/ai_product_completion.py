"""Bounded AI Product DNA completion over the closed deliberation core.

This module extends, rather than replaces, the already-closed participant semantic
contract. Rounds 1-2 delegate to the proven orchestrator unchanged. Rounds >=3 add
traceable same-participant revision phases before synthesis. The application
subclass adds one bounded persistence operation for the human/user verdict.
"""

from __future__ import annotations

import json
from datetime import datetime

from agents.role_agent import RoleAgent
from agents.router import ModelRouter, TERMINAL_PROVIDER_FAILURE_TEXT
from core.application import MultiMindApplication
from core.debate import DebateOrchestrator
from providers.base import BaseProvider
from utils.error_handler import error_logger


class DeepDebateOrchestrator(DebateOrchestrator):
    """Extend the proven orchestrator with deep-round participant revision."""

    DEEP_DEBATE_MIN_ROUNDS = 3

    def debate(self, prompt, context="", mode="coding", rounds=1, agents=None, skill=None):
        effective_rounds = self._normalize_rounds(rounds)
        if effective_rounds < self.DEEP_DEBATE_MIN_ROUNDS:
            result = super().debate(
                prompt=prompt,
                context=context,
                mode=mode,
                rounds=effective_rounds,
                agents=agents,
                skill=skill,
            )
            if isinstance(result, dict):
                result.setdefault(
                    "deliberation_depth",
                    "panel" if effective_rounds == 1 else "deliberate",
                )
                result.setdefault("revisions", [])
            return result

        requested_agents = ["cloudflare"] if agents is None else list(agents)
        active_agents = self._normalize_agents(requested_agents)
        debate_log = {
            "prompt": prompt,
            "context": context,
            "mode": mode,
            "rounds": effective_rounds,
            "deliberation_depth": "deep_debate",
            "requested_agents": requested_agents,
            "agents": active_agents,
            "responses": [],
            "participants": [],
            "deliberation": [],
            "revisions": [],
            "judge": {},
            "system_verdict": None,
            "user_verdict": None,
            "total_tokens": 0,
            "total_cost": 0.0,
            "start_time": datetime.now().isoformat(),
        }

        try:
            full_prompt = self._build_full_prompt(prompt, context, skill)
            configured = self._configured_providers()
            if not configured:
                raise ValueError("No providers configured on DebateOrchestrator")

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

            # Keep immutable initial contributions and a separate working position.
            working_positions = [dict(item) for item in successful_participants]

            for deliberation_round in range(2, effective_rounds + 1):
                comparison = self._format_participants(working_positions)
                earlier = self._format_critiques(debate_log["deliberation"])
                round_critiques = []

                for participant_index, participant in enumerate(working_positions):
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
                    critique = self._critique_record(
                        participant=participant,
                        provider=provider,
                        response=response,
                        round_number=deliberation_round,
                    )
                    debate_log["deliberation"].append(critique)
                    round_critiques.append(critique)
                    debate_log["responses"].append(
                        self._legacy_response(
                            response,
                            role=role,
                            phase="critique",
                            participant_id=participant["participant_id"],
                            round_number=deliberation_round,
                        )
                    )

                # Round 2 remains the existing deliberate behavior. Deep rounds
                # additionally let each participant revise its own position after
                # seeing the panel and the accumulated criticism.
                if deliberation_round < self.DEEP_DEBATE_MIN_ROUNDS:
                    continue

                critique_context = self._format_critiques(debate_log["deliberation"])
                position_by_id = {
                    item["participant_id"]: item for item in working_positions
                }
                for participant_index, participant in enumerate(list(working_positions)):
                    agent_id = participant["requested_provider"]
                    provider = configured.get(agent_id)
                    if provider is None:
                        continue
                    revision_task = self._revision_prompt(
                        original_task=full_prompt,
                        current_positions=comparison,
                        critiques=critique_context,
                        own_participant_id=participant["participant_id"],
                        own_current_answer=participant["text"],
                        round_number=deliberation_round,
                    )
                    role = (
                        f"{self._participant_role(mode, participant_index)} "
                        f"— Revision R{deliberation_round}"
                    )
                    response = self._execute_single_provider(
                        provider=provider,
                        role=role,
                        task=revision_task,
                        mode=mode,
                        max_tokens=self._max_tokens(agent_id),
                    )
                    self._accumulate_usage(debate_log, response)
                    revision = self._revision_record(
                        participant=participant,
                        provider=provider,
                        response=response,
                        round_number=deliberation_round,
                    )
                    debate_log["revisions"].append(revision)
                    debate_log["responses"].append(
                        self._legacy_response(
                            response,
                            role=role,
                            phase="revision",
                            participant_id=participant["participant_id"],
                            round_number=deliberation_round,
                        )
                    )
                    if revision["status"] == "success":
                        updated = dict(position_by_id[participant["participant_id"]])
                        updated["text"] = revision["text"]
                        updated["actual_provider"] = revision["actual_provider"]
                        updated["model"] = revision["model"]
                        updated["latest_revision_round"] = deliberation_round
                        position_by_id[participant["participant_id"]] = updated

                working_positions = [
                    position_by_id[item["participant_id"]]
                    for item in working_positions
                ]

            judge_eligible_providers = self._judge_provider_ids(successful_participants)
            judge_response = self._run_deep_judge(
                configured=configured,
                eligible_provider_ids=judge_eligible_providers,
                initial_participants=successful_participants,
                current_positions=working_positions,
                critiques=debate_log["deliberation"],
                revisions=debate_log["revisions"],
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
                fallback = working_positions[0]
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

            debate_log["final_answer"] = self._apply_release_gate(
                candidate_for_gate, mode, debate_log
            )
            debate_log["status"] = "success"
            debate_log["successful_participants"] = len(successful_participants)
            debate_log["selected_participants"] = len(active_agents)
            debate_log["revision_count"] = sum(
                1 for item in debate_log["revisions"] if item.get("status") == "success"
            )
            debate_log["end_time"] = datetime.now().isoformat()
        except Exception as exc:
            error_logger.log("DEEP_DEBATE_ERROR", f"exception_type={type(exc).__name__}")
            debate_log["status"] = "error"
            debate_log["final_answer"] = TERMINAL_PROVIDER_FAILURE_TEXT
            debate_log["end_time"] = datetime.now().isoformat()

        return debate_log

    def _critique_record(self, participant, provider, response, round_number):
        usable = BaseProvider.has_usable_response(response)
        return {
            "round": round_number,
            "participant_id": participant["participant_id"],
            "requested_provider": participant["requested_provider"],
            "actual_provider": (
                response.get("agent", self._provider_label(provider))
                if usable else self._provider_label(provider)
            ),
            "model": getattr(provider, "model_name", self._provider_label(provider)),
            "status": "success" if usable else "error",
            "text": response.get("text", "") if usable else "",
            "failure_category": response.get("failure_category") if isinstance(response, dict) else None,
            "tokens": response.get("tokens", 0) if isinstance(response, dict) else 0,
            "cost": response.get("cost", 0.0) if isinstance(response, dict) else 0.0,
        }

    def _revision_record(self, participant, provider, response, round_number):
        usable = BaseProvider.has_usable_response(response)
        return {
            "round": round_number,
            "participant_id": participant["participant_id"],
            "requested_provider": participant["requested_provider"],
            "actual_provider": (
                response.get("agent", self._provider_label(provider))
                if usable else self._provider_label(provider)
            ),
            "model": getattr(provider, "model_name", self._provider_label(provider)),
            "status": "success" if usable else "error",
            "text": response.get("text", "") if usable else "",
            "failure_category": response.get("failure_category") if isinstance(response, dict) else None,
            "tokens": response.get("tokens", 0) if isinstance(response, dict) else 0,
            "cost": response.get("cost", 0.0) if isinstance(response, dict) else 0.0,
        }

    @staticmethod
    def _revision_prompt(
        original_task,
        current_positions,
        critiques,
        own_participant_id,
        own_current_answer,
        round_number,
    ):
        return f"""You are revising your position in MultiMind deep-debate round {round_number}.

ORIGINAL TASK:
{original_task}

CURRENT PANEL POSITIONS:
{current_positions}

CRITIQUES SO FAR:
{critiques}

YOUR PARTICIPANT ID:
{own_participant_id}

YOUR CURRENT ANSWER:
{own_current_answer}

Produce a standalone revised answer. Correct concrete mistakes exposed by the panel,
incorporate stronger evidence or constraints when warranted, and explicitly preserve
any disagreement you still believe is materially justified. Do not change position
merely to manufacture consensus. Preserve code, numbers, filenames, requirements,
and evidence when they matter. Return only the revised answer."""

    @staticmethod
    def _format_revisions(revisions):
        usable = [
            item for item in revisions
            if item.get("status") == "success" and item.get("text")
        ]
        if not usable:
            return "(none)"
        return "\n\n".join(
            f"--- Revision R{item['round']} / {item['participant_id']} ---\n{item['text']}"
            for item in usable
        )

    def _run_deep_judge(
        self,
        configured,
        eligible_provider_ids,
        initial_participants,
        current_positions,
        critiques,
        revisions,
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
        role_agent = RoleAgent(
            role=self._judge_role(mode),
            skill=self._judge_system_prompt(mode),
            router=ModelRouter(providers),
        )
        judge_task = self._deep_judge_prompt(
            original_task=full_prompt,
            initial_participants=self._format_participants(initial_participants),
            current_positions=self._format_participants(current_positions),
            critiques=self._format_critiques(critiques),
            revisions=self._format_revisions(revisions),
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
    def _deep_judge_prompt(
        original_task,
        initial_participants,
        current_positions,
        critiques,
        revisions,
    ):
        return f"""You are MultiMind's deep-debate synthesis judge.

ORIGINAL TASK:
{original_task}

INITIAL PARTICIPANT CONTRIBUTIONS:
{initial_participants}

CURRENT PARTICIPANT POSITIONS AFTER REVISION:
{current_positions}

CRITIQUES:
{critiques}

TRACEABLE REVISIONS:
{revisions}

Evaluate correctness, completeness, consistency, relevance, evidence, how well each
participant responded to criticism, and any material disagreement that remains.
Do not reward superficial convergence. Preserve useful minority corrections or
explicit unresolved uncertainty when warranted.

Your response MUST use this shape:
WINNER: <exact participant-id from the initial participants>
FINAL:
<standalone final answer to the user>

The winner identifies the strongest participant trajectory. The FINAL answer may
combine material contributions from multiple participants and revisions."""


class AIProductApplication(MultiMindApplication):
    """MultiMind application boundary with persistent human verdict semantics."""

    def record_user_verdict(self, session_id, chat_id, participant_id):
        if not session_id or not chat_id or not participant_id:
            return False
        database = self._database()
        get_chat = getattr(database, "get_chat", None)
        update = getattr(database, "update_chat_debate_data", None)
        if not callable(get_chat) or not callable(update):
            raise RuntimeError("Persistence adapter does not support user verdict updates.")

        row = get_chat(session_id, chat_id)
        if not row:
            return False
        try:
            debate = json.loads(row.get("debate_data") or "{}")
        except (TypeError, ValueError):
            return False
        if not isinstance(debate, dict):
            return False
        successful_ids = {
            str(item.get("participant_id"))
            for item in debate.get("participants", [])
            if isinstance(item, dict)
            and item.get("status") == "success"
            and item.get("participant_id")
        }
        if participant_id not in successful_ids:
            return False

        # Human judgment is an independent truth. Never rewrite system_verdict.
        debate["user_verdict"] = participant_id
        return bool(
            update(
                session_id,
                chat_id,
                json.dumps(debate, ensure_ascii=False),
            )
        )
