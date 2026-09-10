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


def _numbered_items(source: Mapping[str, str], prefix: str, suffix: str) -> list[tuple[int, str]]:
    """Return configured resource values with stable original numeric identity."""
    values = []
    primary = source.get(f"{prefix}{suffix}", "")
    if primary:
        values.append((1, primary))

    marker = f"{prefix}{suffix}_"
    for name, value in source.items():
        if not value or not name.startswith(marker):
            continue
        tail = name[len(marker):]
        if tail.isdigit() and int(tail) >= 2:
            values.append((int(tail), value))
    return sorted(values)


def _resource_id(index: int) -> str:
    return "primary" if index == 1 else str(index)


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
        items = _numbered_items(source, prefix, suffix)
        provider_resources[provider] = tuple(
            {"resource_id": _resource_id(index), "credential": value}
            for index, value in items
        )
        if items:
            selected[f"{provider}_key"] = items[0][1]

    cf_keys = dict(_numbered_items(source, prefix, "CLOUDFLARE_KEY"))
    cf_accounts = dict(_numbered_items(source, prefix, "CLOUDFLARE_ACCOUNT_ID"))
    cf_indices = sorted(set(cf_keys) | set(cf_accounts))
    provider_resources["cloudflare"] = tuple(
        {
            "resource_id": _resource_id(index),
            "credential": cf_keys.get(index, ""),
            "account_id": cf_accounts.get(index, ""),
            "ready": bool(cf_keys.get(index) and cf_accounts.get(index)),
        }
        for index in cf_indices
    )
    for index in cf_indices:
        if cf_keys.get(index) and cf_accounts.get(index):
            selected["cloudflare_key"] = cf_keys[index]
            selected["cloudflare_account_id"] = cf_accounts[index]
            break

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
