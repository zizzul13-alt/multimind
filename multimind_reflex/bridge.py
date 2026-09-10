"""Reflex-edge helpers that adapt deployment/runtime inputs to core contracts."""

from __future__ import annotations

import io
import os
from typing import Mapping

from core.composition import build_application_for_user
from utils.provider_resources import parse_user_provider_pools


_ENV_KEY_ALIASES = {
    "gemini_key": ("MULTIMIND_GEMINI_KEY", "GEMINI_API_KEY"),
    "deepseek_key": ("MULTIMIND_DEEPSEEK_KEY", "DEEPSEEK_API_KEY"),
    "groq_key": ("MULTIMIND_GROQ_KEY", "GROQ_API_KEY"),
    "cloudflare_key": ("MULTIMIND_CLOUDFLARE_KEY", "CLOUDFLARE_API_KEY"),
    "cloudflare_account_id": (
        "MULTIMIND_CLOUDFLARE_ACCOUNT_ID",
        "CLOUDFLARE_ACCOUNT_ID",
    ),
    "openrouter_key": ("MULTIMIND_OPENROUTER_KEY", "OPENROUTER_API_KEY"),
    "huggingface_key": (
        "MULTIMIND_HUGGINGFACE_KEY",
        "HUGGINGFACE_API_KEY",
        "HF_TOKEN",
    ),
    "remote_url": ("MULTIMIND_REMOTE_URL",),
}


def _truthy(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def default_credentials_allowed_for_users(environ: Mapping[str, str] | None = None) -> bool:
    """Resolve authenticated-user fallback policy without breaking migration.

    Before a per-user pool is configured, the existing deployment/default pool
    remains active so merging this code cannot silently disable an already
    running deployment. As soon as ``MULTIMIND_USER_PROVIDER_POOLS_JSON`` is set,
    fallback becomes fail-closed by default. Operators can explicitly override
    either state with ``MULTIMIND_ALLOW_DEFAULT_CREDENTIALS_FOR_USERS``.
    """
    source = os.environ if environ is None else environ
    explicit = source.get("MULTIMIND_ALLOW_DEFAULT_CREDENTIALS_FOR_USERS")
    if explicit is not None and str(explicit).strip() != "":
        return _truthy(explicit)
    return not bool(str(source.get("MULTIMIND_USER_PROVIDER_POOLS_JSON", "")).strip())


def environment_secrets_source(environ: Mapping[str, str] | None = None):
    """Expose user-scoped and operator/default provider credentials.

    Per-user pools come from the server-side JSON resource map. Existing
    deployment-level variables remain under ``default`` for explicit operator or
    backwards-compatible proof use. Callers decide whether fallback to that
    default pool is permitted.
    """
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

    pools = parse_user_provider_pools(source.get("MULTIMIND_USER_PROVIDER_POOLS_JSON", ""))
    pools["default"] = default_resolved
    return pools


def build_host_application(user_id, runtime_memories, *, agents=None):
    """Build the shared application from the Reflex presentation edge."""
    return build_application_for_user(
        user_id,
        secrets_source=environment_secrets_source,
        allow_default_credentials=default_credentials_allowed_for_users(),
        runtime_memories=runtime_memories,
        agents=agents,
    )


class BufferedUpload(io.BytesIO):
    """Small sync file adapter matching the existing FileHandler contract."""

    def __init__(self, name: str, data: bytes):
        super().__init__(data)
        self.name = name
        self.size = len(data)
