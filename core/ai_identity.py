"""AI-identity-first routing over existing provider adapters.

Users select an AI/model identity.  This module resolves the boring infrastructure
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


# This is a product-identity catalogue over routes that the current repository
# can truthfully pin today.  Gateway brands are deliberately absent as identities.
AI_IDENTITIES: dict[str, AiIdentitySpec] = {
    "gemini": AiIdentitySpec("gemini", "Gemini", ("gemini",), ("gemini",)),
    "gpt-oss": AiIdentitySpec("gpt-oss", "GPT-OSS", ("gpt-oss",), ("groq", "huggingface")),
    "llama": AiIdentitySpec("llama", "Llama", ("llama",), ("cloudflare",)),
    "deepseek": AiIdentitySpec("deepseek", "DeepSeek", ("deepseek",), ("deepseek",)),
}

AI_IDENTITY_OPTIONS = tuple(AI_IDENTITIES)
AI_IDENTITY_LABELS = {key: spec.display_name for key, spec in AI_IDENTITIES.items()}


def infer_ai_identity(*, model_id: str | None = None, family: str | None = None) -> str | None:
    """Infer a durable AI identity only from provider-supplied model provenance.

    Unknown/dynamic models return ``None`` rather than being guessed.  The extra
    families below are forward-compatible recognition only; they do not make a
    route selectable unless the catalogue above explicitly maps one.
    """
    family_value = str(family or "").strip().lower()
    family_aliases = {
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
    if family_value in family_aliases:
        return family_aliases[family_value]

    model = str(model_id or "").strip().lower()
    if not model:
        return None
    checks = (
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
    for needles, identity in checks:
        if any(needle in model for needle in needles):
            return identity
    return None


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
                # A gateway/provider response is not allowed to cosplay the selected AI.
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
            # Preserve old response consumers while making the actual route explicit.
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
