"""AI-identity-first routing over existing provider adapters.

Users select an AI/model identity. This module resolves the boring infrastructure
route underneath it and refuses to surface a response whose effective model
identity does not match the selected identity.

It intentionally does not own credentials, persistence, presentation, pricing,
or cross-identity fallback policy.
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


# Product identities over routes the current repository can truthfully pin today.
# Gateway/inference brands are deliberately absent from the user-facing identity list.
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
    "gemini": "gemini",
    "gpt-oss": "gpt-oss",
    "llama": "llama",
    "deepseek": "deepseek",
    "claude": "claude",
    "qwen": "qwen",
    "kimi": "kimi",
    "moonshot": "kimi",
    "grok": "grok",
    "gpt": "gpt",
}


def infer_ai_identity(*, model_id: str | None = None, family: str | None = None) -> str | None:
    """Infer identity conservatively from provider-supplied provenance.

    A concrete model identifier is stronger evidence than a family hint. If the
    model is recognizable, it wins even when a stale/misconfigured family field
    claims something else. Family is used only when the model string itself is
    absent or not recognizable. Unknown provenance returns ``None``.
    """
    model = str(model_id or "").strip().lower()
    if model:
        for needles, identity in _MODEL_IDENTITY_CHECKS:
            if any(needle in model for needle in needles):
                return identity

    family_value = str(family or "").strip().lower()
    return _FAMILY_ALIASES.get(family_value)


def _model_from_response(response: dict, provider) -> str:
    return str(
        response.get("actual_model")
        or response.get("resolved_model")
        or getattr(provider, "model_name", "")
        or ""
    )


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
                response = provider.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    mode=mode,
                    max_tokens=max_tokens,
                    **kwargs,
                )
            except Exception as exc:
                attempts.append({"route": route_id, "status": "error", "reason": type(exc).__name__})
                continue

            if not BaseProvider.has_usable_response(response):
                attempts.append({
                    "route": route_id,
                    "status": "error",
                    "reason": str(response.get("failure_category") or "provider_error") if isinstance(response, dict) else "provider_error",
                })
                continue

            model_id = _model_from_response(response, provider)
            effective_identity = infer_ai_identity(
                model_id=model_id,
                family=response.get("model_family") if isinstance(response, dict) else None,
            )
            if effective_identity != self.spec.identity_id:
                # Infrastructure may be abstracted; the AI identity may not be falsified.
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
            })
            # Old orchestration records response['agent'] as actual provider provenance.
            result["agent"] = route_id
            self.model_name = model_id or self.spec.display_name
            self.set_availability(True)
            return result

        self.set_availability(False, "No truthful route available")
        return {
            "status": "error",
            "text": "Provider temporarily unavailable. Trying another provider.",
            "agent": self.spec.display_name,
            "tokens": 0,
            "cost": 0.0,
            "failure_category": "identity_unavailable",
            "requested_identity": self.spec.identity_id,
            "effective_identity": None,
            "route_provider": None,
            "identity_route_fallback": False,
            "identity_fallback_reason": "all_same_identity_routes_failed",
            "route_attempts": attempts,
        }


def build_identity_providers(agents: Mapping[str, object] | None) -> dict[str, IdentityRoutedProvider]:
    """Build available identity participants from already-composed provider adapters."""
    configured = agents or {}
    identities: dict[str, IdentityRoutedProvider] = {}
    for identity_id, spec in AI_IDENTITIES.items():
        routes = [
            (route_id, configured[route_id])
            for route_id in spec.route_order
            if configured.get(route_id) is not None
        ]
        if routes:
            identities[identity_id] = IdentityRoutedProvider(spec, routes)
    return identities


def available_identity_options(agents: Mapping[str, object] | None) -> list[str]:
    return list(build_identity_providers(agents))
