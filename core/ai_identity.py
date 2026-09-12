"""AI-identity-first routing over built-in and discovered provider resources.

Users select an AI/model identity. Infrastructure routes remain server-side and
responses are rejected when their effective identity does not match the selected
identity. Endpoint-declared model IDs are useful routing evidence, not proof of
upstream vendor provenance.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from providers.base import BaseProvider


@dataclass(frozen=True)
class AiIdentitySpec:
    identity_id: str
    display_name: str
    families: tuple[str, ...]
    route_order: tuple[str, ...]
    execution_slot: str


AI_IDENTITIES: dict[str, AiIdentitySpec] = {
    "gemini": AiIdentitySpec("gemini", "Gemini", ("gemini",), ("gemini",), "gemini"),
    "gpt-oss": AiIdentitySpec("gpt-oss", "GPT-OSS", ("gpt-oss",), ("groq", "huggingface"), "groq"),
    "llama": AiIdentitySpec("llama", "Llama", ("llama",), ("cloudflare",), "cloudflare"),
    "deepseek": AiIdentitySpec("deepseek", "DeepSeek", ("deepseek",), ("deepseek",), "deepseek"),
}

AI_IDENTITY_OPTIONS = tuple(AI_IDENTITIES)
AI_IDENTITY_LABELS = {key: spec.display_name for key, spec in AI_IDENTITIES.items()}

_MODEL_IDENTITY_CHECKS = (
    (("gemini",), "gemini"),
    (("gpt-oss",), "gpt-oss"),
    (("llama", "meta/llama", "meta-llama"), "llama"),
    (("deepseek",), "deepseek"),
    (("claude", "anthropic/"), "claude"),
    (("qwen",), "qwen"),
    (("kimi", "moonshot"), "kimi"),
    (("grok", "x-ai/", "xai/"), "grok"),
    (("gpt-", "openai/gpt-"), "gpt"),
)

_FAMILY_ALIASES = {
    "gemini": "gemini", "gpt-oss": "gpt-oss", "llama": "llama",
    "deepseek": "deepseek", "claude": "claude", "qwen": "qwen",
    "kimi": "kimi", "moonshot": "kimi", "grok": "grok", "gpt": "gpt",
}

_DYNAMIC_LABELS = {
    "claude": "Claude", "gpt": "GPT", "qwen": "Qwen", "kimi": "Kimi",
    "grok": "Grok", "gemini": "Gemini", "deepseek": "DeepSeek",
    "llama": "Llama", "gpt-oss": "GPT-OSS",
}


def infer_ai_identity(*, model_id: str | None = None, family: str | None = None) -> str | None:
    """Infer identity conservatively from provider-supplied provenance."""
    model = str(model_id or "").strip().lower()
    if model:
        for needles, identity in _MODEL_IDENTITY_CHECKS:
            if any(needle in model for needle in needles):
                return identity
    return _FAMILY_ALIASES.get(str(family or "").strip().lower())


def _model_from_response(response: dict, provider) -> str:
    return str(response.get("actual_model") or response.get("resolved_model") or getattr(provider, "model_name", "") or "")


def runtime_identity_specs(agents: Mapping[str, object] | None) -> dict[str, AiIdentitySpec]:
    """Return static identities plus identities truthfully classifiable from routes.

    Discovered resources use route IDs prefixed with ``resource:``. Multiple
    models/routes for the same family become same-identity fallbacks. Unknown
    catalogue entries stay inert rather than being guessed into the UI.
    """
    configured = agents or {}
    route_map: dict[str, list[str]] = {key: list(spec.route_order) for key, spec in AI_IDENTITIES.items()}
    for route_id, provider in configured.items():
        if not str(route_id).startswith("resource:") or provider is None:
            continue
        identity_id = infer_ai_identity(model_id=getattr(provider, "model_name", None))
        if not identity_id:
            continue
        route_map.setdefault(identity_id, []).append(str(route_id))

    result = dict(AI_IDENTITIES)
    for identity_id, routes in route_map.items():
        unique_routes = tuple(dict.fromkeys(routes))
        if identity_id in result:
            base = result[identity_id]
            result[identity_id] = AiIdentitySpec(base.identity_id, base.display_name, base.families, unique_routes, base.execution_slot)
            continue
        result[identity_id] = AiIdentitySpec(
            identity_id=identity_id,
            display_name=_DYNAMIC_LABELS.get(identity_id, identity_id.title()),
            families=(identity_id,),
            route_order=unique_routes,
            execution_slot="groq",
        )
    return result


class IdentityRoutedProvider(BaseProvider):
    """One selected AI identity with one or more same-identity provider routes."""

    def __init__(self, spec: AiIdentitySpec, routes: list[tuple[str, BaseProvider]]):
        super().__init__(spec.display_name)
        self.spec = spec
        self.routes = list(routes)
        self.model_name = spec.display_name

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 4096, **kwargs) -> dict:
        attempts: list[dict[str, str]] = []
        for route_index, (route_id, provider) in enumerate(self.routes):
            try:
                response = provider.generate(prompt=prompt, system_prompt=system_prompt, mode=mode, max_tokens=max_tokens, **kwargs)
            except Exception as exc:
                attempts.append({"route": route_id, "status": "error", "reason": type(exc).__name__})
                continue
            if not BaseProvider.has_usable_response(response):
                attempts.append({"route": route_id, "status": "error", "reason": str(response.get("failure_category") or "provider_error") if isinstance(response, dict) else "provider_error"})
                continue
            model_id = _model_from_response(response, provider)
            effective_identity = infer_ai_identity(model_id=model_id, family=response.get("model_family") if isinstance(response, dict) else None)
            if effective_identity != self.spec.identity_id:
                attempts.append({"route": route_id, "status": "rejected", "reason": "identity_mismatch"})
                continue
            result = dict(response)
            result.update({
                "requested_identity": self.spec.identity_id,
                "effective_identity": effective_identity,
                "route_provider": route_id,
                "actual_model": model_id or response.get("actual_model"),
                "identity_route_fallback": route_index > 0,
                "identity_fallback_reason": "same_identity_route_failure" if route_index > 0 else None,
                "route_attempts": attempts + [{"route": route_id, "status": "success", "reason": ""}],
                "identity_provenance": response.get("identity_provenance", "provider_model_provenance"),
            })
            result["agent"] = route_id
            self.model_name = model_id or self.spec.display_name
            self.set_availability(True)
            return result

        self.set_availability(False, "No truthful route available")
        return {
            "status": "error", "text": "Provider temporarily unavailable. Trying another provider.",
            "agent": self.spec.display_name, "tokens": 0, "cost": 0.0,
            "failure_category": "identity_unavailable", "requested_identity": self.spec.identity_id,
            "effective_identity": None, "route_provider": None, "identity_route_fallback": False,
            "identity_fallback_reason": "all_same_identity_routes_failed", "route_attempts": attempts,
        }


def build_identity_providers(agents: Mapping[str, object] | None) -> dict[str, IdentityRoutedProvider]:
    configured = agents or {}
    identities: dict[str, IdentityRoutedProvider] = {}
    for identity_id, spec in runtime_identity_specs(configured).items():
        routes = [(route_id, configured[route_id]) for route_id in spec.route_order if configured.get(route_id) is not None]
        if routes:
            identities[identity_id] = IdentityRoutedProvider(spec, routes)
    return identities


def available_identity_options(agents: Mapping[str, object] | None) -> list[str]:
    return list(build_identity_providers(agents))
