"""Reflex-edge helpers that adapt deployment/runtime inputs to core contracts."""

from __future__ import annotations

import io
import os
import re
from typing import Mapping

from core.composition import build_application_for_user
from utils.config import Config


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

_USER_RESOURCE_SUFFIXES = {
    "gemini": "GEMINI_KEY",
    "deepseek": "DEEPSEEK_KEY",
    "groq": "GROQ_KEY",
    "cloudflare": "CLOUDFLARE_KEY",
    "openrouter": "OPENROUTER_KEY",
    "huggingface": "HUGGINGFACE_KEY",
}
_USER_SLOT_ID_RE = re.compile(r"^MULTIMIND_USER_([A-Z0-9_]+)_ID$")


def _default_environment_pool(source: Mapping[str, str]) -> dict:
    resolved = {}
    for key, names in _ENV_KEY_ALIASES.items():
        value = ""
        for name in names:
            candidate = source.get(name, "")
            if candidate:
                value = candidate
                break
        resolved[key] = value
    return resolved


def _numbered_values(source: Mapping[str, str], prefix: str, suffix: str) -> list[str]:
    """Return primary, then numbered resources in deterministic numeric order."""
    values = []
    primary = source.get(f"{prefix}{suffix}", "")
    if primary:
        values.append(primary)

    numbered = []
    marker = f"{prefix}{suffix}_"
    for name, value in source.items():
        if not value or not name.startswith(marker):
            continue
        tail = name[len(marker):]
        if tail.isdigit() and int(tail) >= 2:
            numbered.append((int(tail), value))
    for _number, value in sorted(numbered):
        values.append(value)
    return values


def _user_pool(source: Mapping[str, str], slot: str) -> dict:
    prefix = f"MULTIMIND_USER_{slot}_"
    provider_resources = {}
    selected = {
        "gemini_key": "",
        "deepseek_key": "",
        "groq_key": "",
        "cloudflare_key": "",
        "cloudflare_account_id": "",
        "openrouter_key": "",
        "huggingface_key": "",
        "remote_url": source.get(f"{prefix}REMOTE_URL", ""),
    }

    for provider, suffix in _USER_RESOURCE_SUFFIXES.items():
        values = _numbered_values(source, prefix, suffix)
        provider_resources[provider] = tuple(
            {"resource_id": "primary" if index == 1 else str(index), "credential": value}
            for index, value in enumerate(values, start=1)
        )
        if values:
            selected[f"{provider}_key"] = values[0]

    account_ids = _numbered_values(source, prefix, "CLOUDFLARE_ACCOUNT_ID")
    if account_ids:
        selected["cloudflare_account_id"] = account_ids[0]
    provider_resources["cloudflare_account_id"] = tuple(
        {"resource_id": "primary" if index == 1 else str(index), "value": value}
        for index, value in enumerate(account_ids, start=1)
    )
    selected["provider_resources"] = provider_resources
    return selected


def environment_secrets_source(environ: Mapping[str, str] | None = None):
    """Expose strict user-scoped deployment credentials plus an operator default.

    Global MULTIMIND_* provider variables remain the explicit ``default`` pool.
    Named deployment users are declared with ``MULTIMIND_USER_<SLOT>_ID`` and
    receive only their own slot credentials. Additional numbered credentials are
    retained as resource metadata but are not automatically rotated by runtime.
    """
    source = os.environ if environ is None else environ
    result = {
        "__policy__": {"allow_default_fallback": False},
        "default": _default_environment_pool(source),
    }

    seen_user_ids = set()
    for name in sorted(source):
        match = _USER_SLOT_ID_RE.fullmatch(name)
        if not match:
            continue
        slot = match.group(1)
        raw_user_id = source.get(name, "")
        user_id = Config.validate_user_id(raw_user_id)
        if user_id == "default" or user_id in seen_user_ids:
            raise ValueError("Deployment user slots must map to unique non-default user ids.")
        seen_user_ids.add(user_id)
        result[user_id] = _user_pool(source, slot)
    return result


def build_host_application(user_id, runtime_memories, *, agents=None):
    """Build the shared application from the Reflex presentation edge."""
    return build_application_for_user(
        user_id,
        secrets_source=environment_secrets_source,
        runtime_memories=runtime_memories,
        agents=agents,
    )


class BufferedUpload(io.BytesIO):
    """Small sync file adapter matching the existing FileHandler contract."""

    def __init__(self, name: str, data: bytes):
        super().__init__(data)
        self.name = name
        self.size = len(data)
