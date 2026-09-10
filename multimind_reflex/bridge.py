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


def _requested_primary_index(source: Mapping[str, str], prefix: str, provider: str) -> int | None:
    raw = source.get(f"{prefix}{provider.upper()}_PRIMARY_RESOURCE", "").strip().lower()
    if not raw:
        return None
    if raw in {"primary", "1"}:
        return 1
    if raw.isdigit() and int(raw) >= 2:
        return int(raw)
    raise ValueError(f"Invalid primary resource selector for {provider}.")


def _select_item(items: list[tuple[int, str]], requested_index: int | None) -> tuple[int, str] | None:
    if not items:
        return None
    if requested_index is None:
        return items[0]
    return next((item for item in items if item[0] == requested_index), None)


def _user_pool(source: Mapping[str, str], slot: str) -> dict:
    prefix = f"MULTIMIND_USER_{slot}_"
    provider_resources = {}
    selected_resource_ids = {}
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
        requested = _requested_primary_index(source, prefix, provider)
        chosen = _select_item(items, requested)
        if chosen is not None:
            selected[f"{provider}_key"] = chosen[1]
            selected_resource_ids[provider] = _resource_id(chosen[0])
        elif requested is not None:
            selected_resource_ids[provider] = "unavailable"

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
    requested_cf = _requested_primary_index(source, prefix, "cloudflare")
    ready_cf = [index for index in cf_indices if cf_keys.get(index) and cf_accounts.get(index)]
    chosen_cf = None
    if requested_cf is None and ready_cf:
        chosen_cf = ready_cf[0]
    elif requested_cf is not None and requested_cf in ready_cf:
        chosen_cf = requested_cf
    if chosen_cf is not None:
        selected["cloudflare_key"] = cf_keys[chosen_cf]
        selected["cloudflare_account_id"] = cf_accounts[chosen_cf]
        selected_resource_ids["cloudflare"] = _resource_id(chosen_cf)
    elif requested_cf is not None:
        selected_resource_ids["cloudflare"] = "unavailable"

    selected["provider_resources"] = provider_resources
    selected["selected_resource_ids"] = selected_resource_ids
    return selected


def environment_secrets_source(environ: Mapping[str, str] | None = None):
    """Expose strict user-scoped deployment credentials plus an operator default.

    Global MULTIMIND_* provider variables remain the operator/default pool for
    deployment smoke tooling, but strict Config resolution never lends that pool
    to a browser identity. Named users receive only their own slot credentials.
    """
    source = os.environ if environ is None else environ
    result = {
        "__policy__": {
            "allow_default_fallback": False,
            "allow_explicit_default_identity": False,
        },
        "default": _default_environment_pool(source),
    }

    seen_user_ids = set()
    for name in sorted(source):
        match = _USER_SLOT_ID_RE.fullmatch(name)
        if not match:
            continue
        raw_user_id = source.get(name, "").strip()
        if not raw_user_id:
            continue
        slot = match.group(1)
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
