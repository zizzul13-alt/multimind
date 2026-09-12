"""Server-side per-user provider credential resource parsing.

Secret values remain server-side. Named resources are selected explicitly; there
is no automatic credential rotation or cross-user merge.
"""
from __future__ import annotations

import json
from typing import Mapping

from utils.config import Config, InvalidUserIdError


_PROVIDER_TO_KEY = {
    "gemini": "gemini_key",
    "deepseek": "deepseek_key",
    "groq": "groq_key",
    "openrouter": "openrouter_key",
    "huggingface": "huggingface_key",
    "remote": "remote_url",
}


def _selected_resource(spec):
    if not isinstance(spec, Mapping):
        return None
    default_name = spec.get("default")
    resources = spec.get("resources")
    if not isinstance(default_name, str) or not default_name:
        return None
    if not isinstance(resources, Mapping):
        return None
    return resources.get(default_name)


def _compatible_resource(provider_name: str, resource) -> dict[str, str] | None:
    if not isinstance(resource, Mapping):
        return None
    base_url = resource.get("base_url")
    key = resource.get("key") or resource.get("api_key")
    if not isinstance(base_url, str) or not base_url.strip() or not isinstance(key, str) or not key:
        return None
    resource_id = str(resource.get("id") or provider_name or "").strip()
    if not resource_id:
        return None
    return {"id": resource_id, "label": str(resource.get("label") or provider_name).strip(), "base_url": base_url.strip(), "api_key": key}


def parse_user_provider_pools(raw: str | None) -> dict[str, dict[str, object]]:
    """Parse redaction-safe per-user resources into adapter settings."""
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        document = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    if not isinstance(document, Mapping):
        return {}

    result: dict[str, dict[str, object]] = {}
    seen_users: set[str] = set()
    for supplied_user, providers in document.items():
        try:
            canonical_user = Config.validate_user_id(supplied_user)
        except (InvalidUserIdError, TypeError):
            continue
        if canonical_user == "default":
            continue
        if canonical_user in seen_users or not isinstance(providers, Mapping):
            result.pop(canonical_user, None)
            continue
        seen_users.add(canonical_user)

        selected: dict[str, object] = dict(Config.EMPTY_API_KEYS)
        selected["remote_url"] = ""
        selected["openai_compatible_resources"] = []
        any_valid = False
        for provider_name, spec in providers.items():
            provider = str(provider_name or "").strip().lower()
            resource = _selected_resource(spec)
            if provider == "cloudflare":
                if not isinstance(resource, Mapping):
                    continue
                key = resource.get("key")
                account_id = resource.get("account_id")
                if isinstance(key, str) and key and isinstance(account_id, str) and account_id:
                    selected["cloudflare_key"] = key
                    selected["cloudflare_account_id"] = account_id
                    any_valid = True
                continue
            if provider in {"openai_compatible", "compatible", "custom"}:
                compatible = _compatible_resource(provider, resource)
                if compatible:
                    selected["openai_compatible_resources"].append(compatible)
                    any_valid = True
                continue
            target_key = _PROVIDER_TO_KEY.get(provider)
            if target_key is not None and isinstance(resource, str) and resource:
                selected[target_key] = resource
                any_valid = True

        if any_valid:
            result[canonical_user] = selected
    return result
