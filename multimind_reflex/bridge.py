"""Reflex-edge helpers that adapt deployment/runtime inputs to core contracts."""
from __future__ import annotations

import io
import json
import os
from typing import Mapping

from core.composition import build_application_for_user
from utils.provider_resources import parse_user_provider_pools

_ENV_KEY_ALIASES = {
    "gemini_key": ("MULTIMIND_GEMINI_KEY", "GEMINI_API_KEY"),
    "deepseek_key": ("MULTIMIND_DEEPSEEK_KEY", "DEEPSEEK_API_KEY"),
    "groq_key": ("MULTIMIND_GROQ_KEY", "GROQ_API_KEY"),
    "cloudflare_key": ("MULTIMIND_CLOUDFLARE_KEY", "CLOUDFLARE_API_KEY"),
    "cloudflare_account_id": ("MULTIMIND_CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_ACCOUNT_ID"),
    "openrouter_key": ("MULTIMIND_OPENROUTER_KEY", "OPENROUTER_API_KEY"),
    "huggingface_key": ("MULTIMIND_HUGGINGFACE_KEY", "HUGGINGFACE_API_KEY", "HF_TOKEN"),
    "remote_url": ("MULTIMIND_REMOTE_URL",),
}


def _truthy(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _operator_compatible_resources(raw: object) -> list[dict[str, str]]:
    """Parse deployment resources without ever returning them to browser state."""
    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return []
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        resource_id, base_url = item.get("id"), item.get("base_url")
        key = item.get("key") or item.get("api_key")
        if all(isinstance(v, str) and v.strip() for v in (resource_id, base_url, key)):
            result.append({"id": resource_id.strip(), "label": str(item.get("label") or resource_id).strip(), "base_url": base_url.strip(), "api_key": key})
    return result


def default_credentials_allowed_for_users(environ: Mapping[str, str] | None = None) -> bool:
    source = os.environ if environ is None else environ
    explicit = source.get("MULTIMIND_ALLOW_DEFAULT_CREDENTIALS_FOR_USERS")
    if explicit is not None and str(explicit).strip() != "":
        return _truthy(explicit)
    return not bool(str(source.get("MULTIMIND_USER_PROVIDER_POOLS_JSON", "")).strip())


def environment_secrets_source(environ: Mapping[str, str] | None = None):
    """Expose user-scoped and operator/default provider credentials server-side."""
    source = os.environ if environ is None else environ
    default_resolved = {}
    for key, names in _ENV_KEY_ALIASES.items():
        value = ""
        for name in names:
            candidate = source.get(name, "")
            if candidate:
                value = candidate
                break
        default_resolved[key] = value
    default_resolved["openai_compatible_resources"] = _operator_compatible_resources(
        source.get("MULTIMIND_OPENAI_COMPATIBLE_RESOURCES_JSON", "")
    )
    pools = parse_user_provider_pools(source.get("MULTIMIND_USER_PROVIDER_POOLS_JSON", ""))
    pools["default"] = default_resolved
    return pools


def build_host_application(user_id, runtime_memories, *, agents=None):
    return build_application_for_user(
        user_id, secrets_source=environment_secrets_source,
        allow_default_credentials=default_credentials_allowed_for_users(),
        runtime_memories=runtime_memories, agents=agents,
    )


class BufferedUpload(io.BytesIO):
    def __init__(self, name: str, data: bytes):
        super().__init__(data)
        self.name = name
        self.size = len(data)
