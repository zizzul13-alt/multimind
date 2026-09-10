"""Server-side per-user provider credential resource parsing.

This module deliberately returns only the currently selected credential values
needed by existing provider adapters.  It never performs quota rotation and it
never persists or presents secret material.
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


def parse_user_provider_pools(raw: str | None) -> dict[str, dict[str, str]]:
    """Parse redaction-safe per-user resource pools into adapter key mappings.

    Invalid JSON, invalid users, malformed provider specs, and malformed selected
    resources are ignored/fail closed.  Additional named resources remain inert;
    there is intentionally no automatic credential rotation. The ``default``
    namespace is reserved for deployment/operator credentials and cannot be
    supplied through the per-user pool JSON.
    """
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        document = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    if not isinstance(document, Mapping):
        return {}

    result: dict[str, dict[str, str]] = {}
    seen_users: set[str] = set()
    for supplied_user, providers in document.items():
        try:
            canonical_user = Config.validate_user_id(supplied_user)
        except (InvalidUserIdError, TypeError):
            continue
        if canonical_user == "default":
            continue
        if canonical_user in seen_users or not isinstance(providers, Mapping):
            # Duplicate canonical identities are ambiguous and therefore ignored.
            result.pop(canonical_user, None)
            continue
        seen_users.add(canonical_user)

        selected: dict[str, str] = dict(Config.EMPTY_API_KEYS)
        selected["remote_url"] = ""
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

            target_key = _PROVIDER_TO_KEY.get(provider)
            if target_key is None:
                continue
            if isinstance(resource, str) and resource:
                selected[target_key] = resource
                any_valid = True

        if any_valid:
            result[canonical_user] = selected
    return result
