"""Identity-first MultiMindApplication extension.

Keeps legacy provider-keyed callers working while allowing presentation hosts to
submit AI identities such as ``gemini``/``gpt-oss``/``llama``/``deepseek``.
Provider routing stays server-side and cross-identity fallback stays disabled.
"""
from __future__ import annotations

from dataclasses import replace

from core.ai_identity import AI_IDENTITIES, build_identity_providers
from core.application import MultiMindApplication
from core.product_semantics import CapabilityRegistry
from core.debate import DebateOrchestrator
from utils.error_handler import error_logger


_IDENTITY_CAPABILITIES = {
    identity_id: {"coding", "research", "thinking"}
    for identity_id in AI_IDENTITIES
}


class IdentityFirstApplication(MultiMindApplication):
    """Application boundary that resolves identity intent to existing adapters."""

    def __init__(self, *args, capability_registry=None, **kwargs):
        super().__init__(
            *args,
            capability_registry=capability_registry or CapabilityRegistry(capabilities=_IDENTITY_CAPABILITIES),
            **kwargs,
        )

    def _identity_mode(self, active_agents):
        selected = list(active_agents or [])
        return bool(selected) and all(item in AI_IDENTITIES for item in selected)

    def capability_state(self, mode):
        identities = build_identity_providers(self.agents)
        states = self.capability_registry.evaluate(mode, identities)
        return {
            "mode": self.capability_registry.normalize_mode(mode),
            "participants": [state.as_dict() for state in states],
            "recommended": self.capability_registry.recommended(mode, identities),
        }

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

        identities = build_identity_providers(self.agents)
        execution_agents = dict(self.agents)
        slot_to_identity: dict[str, str] = {}
        active_slots: list[str] = []

        for identity_id in request.active_agents:
            spec = AI_IDENTITIES[identity_id]
            slot = spec.execution_slot
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
            result = orchestrator.debate(
                prompt=final_prompt,
                context=context[:3000],
                mode=request.session_mode,
                rounds=request.debate_rounds,
                agents=active_slots,
                skill=None,
            )
        except Exception as exc:
            error_logger.log("IDENTITY_DEBATE_EXECUTION_FAILURE", f"exception_type={type(exc).__name__}")
            return {"status": "error", "responses": [], "total_tokens": 0, "total_cost": 0}

        # Decorate persisted deliberation truth with identity provenance. The
        # wrapper only returns success after verifying model-family identity.
        participant_identity: dict[str, str] = {}
        for participant in result.get("participants", []):
            slot = str(participant.get("requested_provider") or "")
            identity_id = slot_to_identity.get(slot, "")
            if not identity_id:
                continue
            participant_identity[str(participant.get("participant_id") or "")] = identity_id
            spec = AI_IDENTITIES[identity_id]
            route = str(participant.get("actual_provider") or "")
            participant["requested_identity"] = identity_id
            participant["effective_identity"] = identity_id if participant.get("status") == "success" else ""
            participant["route_provider"] = route
            participant["identity_route_fallback"] = bool(route and route != spec.route_order[0])
            participant["identity_fallback_reason"] = (
                "same_identity_route_failure" if participant["identity_route_fallback"] else ""
            )

        for collection_name in ("deliberation", "revisions"):
            for item in result.get(collection_name, []):
                identity_id = participant_identity.get(str(item.get("participant_id") or ""), "")
                if not identity_id:
                    continue
                spec = AI_IDENTITIES[identity_id]
                route = str(item.get("actual_provider") or "")
                item["requested_identity"] = identity_id
                item["effective_identity"] = identity_id if item.get("status") == "success" else ""
                item["route_provider"] = route
                item["identity_route_fallback"] = bool(route and route != spec.route_order[0])

        result["requested_identities"] = list(request.active_agents)
        result["identity_routing"] = {
            "mode": "identity_first",
            "cross_identity_fallback": "disabled",
            "routes": {
                identity_id: list(AI_IDENTITIES[identity_id].route_order)
                for identity_id in request.active_agents
            },
        }
        product = result.get("product_semantics")
        if isinstance(product, dict):
            product["explicit_identities"] = list(request.active_agents)
        return result
