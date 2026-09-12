"""Identity-first MultiMindApplication extension.

Keeps legacy provider-keyed callers working while allowing presentation hosts to
submit built-in or dynamically discovered AI identities. Provider routing stays
server-side and cross-identity fallback stays disabled.
"""
from __future__ import annotations

from core.ai_identity import build_identity_providers, runtime_identity_specs
from core.application import MultiMindApplication
from core.product_semantics import CapabilityRegistry
from utils.error_handler import error_logger


class IdentityFirstApplication(MultiMindApplication):
    """Application boundary that resolves identity intent to existing adapters."""

    def __init__(self, *args, capability_registry=None, **kwargs):
        super().__init__(*args, capability_registry=capability_registry, **kwargs)

    def _identity_specs(self):
        return runtime_identity_specs(self.agents)

    def _identity_capability_registry(self):
        return CapabilityRegistry(capabilities={identity_id: {"coding", "research", "thinking"} for identity_id in self._identity_specs()})

    def _identity_mode(self, active_agents):
        selected = list(active_agents or [])
        specs = self._identity_specs()
        return bool(selected) and all(item in specs for item in selected)

    def capability_state(self, mode):
        identities = build_identity_providers(self.agents)
        registry = self._identity_capability_registry()
        states = registry.evaluate(mode, identities)
        return {"mode": registry.normalize_mode(mode), "participants": [state.as_dict() for state in states], "recommended": registry.recommended(mode, identities)}

    def _compression_utility(self, explicit_agents):
        if self._identity_mode(explicit_agents):
            identities = build_identity_providers(self.agents)
            for identity_id in explicit_agents:
                provider = identities.get(identity_id)
                if provider is not None:
                    return identity_id, provider
            return None, None
        return super()._compression_utility(explicit_agents)

    def _route(self, request, final_prompt, context):
        if not self._identity_mode(request.active_agents):
            return super()._route(request, final_prompt, context)

        specs = self._identity_specs()
        identities = build_identity_providers(self.agents)
        execution_agents = dict(self.agents)
        slot_to_identity: dict[str, str] = {}
        active_slots: list[str] = []
        available_slots = ["gemini", "deepseek", "groq", "cloudflare", "openrouter", "huggingface"]

        for identity_id in request.active_agents:
            spec = specs[identity_id]
            preferred = spec.execution_slot
            slot = preferred if preferred not in slot_to_identity else next((item for item in available_slots if item not in slot_to_identity), "")
            if not slot:
                return {"status": "error", "responses": [], "total_tokens": 0, "total_cost": 0, "failure_category": "identity_slot_exhausted"}
            slot_to_identity[slot] = identity_id
            active_slots.append(slot)
            execution_agents[slot] = identities.get(identity_id)

        orchestrator = self.debate_factory(
            gemini_agent=execution_agents.get("gemini"),
            deepseek_agent=execution_agents.get("deepseek"),
            groq_agent=execution_agents.get("groq"),
            cloudflare_agent=execution_agents.get("cloudflare"),
            openrouter_agent=execution_agents.get("openrouter"),
            huggingface_agent=execution_agents.get("huggingface"),
        )
        try:
            result = orchestrator.debate(prompt=final_prompt, context=context[:3000], mode=request.session_mode, rounds=request.debate_rounds, agents=active_slots, skill=None)
        except Exception as exc:
            error_logger.log("IDENTITY_DEBATE_EXECUTION_FAILURE", f"exception_type={type(exc).__name__}")
            return {"status": "error", "responses": [], "total_tokens": 0, "total_cost": 0}

        participant_identity: dict[str, str] = {}
        participant_id_map: dict[str, str] = {}
        for index, participant in enumerate(result.get("participants", []), 1):
            slot = str(participant.get("requested_provider") or "")
            identity_id = slot_to_identity.get(slot, "")
            if not identity_id:
                continue
            old_participant_id = str(participant.get("participant_id") or "")
            new_participant_id = f"participant-{index}-{identity_id}"
            participant_identity[old_participant_id] = identity_id
            participant_id_map[old_participant_id] = new_participant_id
            participant["participant_id"] = new_participant_id
            spec = specs[identity_id]
            route = str(participant.get("actual_provider") or "")
            participant["requested_identity"] = identity_id
            participant["effective_identity"] = identity_id if participant.get("status") == "success" else ""
            participant["route_provider"] = route
            participant["identity_route_fallback"] = bool(route and route != spec.route_order[0])
            participant["identity_fallback_reason"] = "same_identity_route_failure" if participant["identity_route_fallback"] else ""

        for collection_name in ("deliberation", "revisions"):
            for item in result.get(collection_name, []):
                old_participant_id = str(item.get("participant_id") or "")
                identity_id = participant_identity.get(old_participant_id, "")
                if not identity_id:
                    continue
                item["participant_id"] = participant_id_map.get(old_participant_id, old_participant_id)
                spec = specs[identity_id]
                route = str(item.get("actual_provider") or "")
                item["requested_identity"] = identity_id
                item["effective_identity"] = identity_id if item.get("status") == "success" else ""
                item["route_provider"] = route
                item["identity_route_fallback"] = bool(route and route != spec.route_order[0])
                item["identity_fallback_reason"] = "same_identity_route_failure" if item["identity_route_fallback"] else ""

        for item in result.get("responses", []):
            old_participant_id = str(item.get("participant_id") or "")
            if old_participant_id in participant_id_map:
                item["participant_id"] = participant_id_map[old_participant_id]
        old_verdict = str(result.get("system_verdict") or "")
        if old_verdict in participant_id_map:
            result["system_verdict"] = participant_id_map[old_verdict]

        result["requested_identities"] = list(request.active_agents)
        result["identity_routing"] = {"mode": "identity_first", "cross_identity_fallback": "disabled", "routes": {identity_id: list(specs[identity_id].route_order) for identity_id in request.active_agents}}
        return result
