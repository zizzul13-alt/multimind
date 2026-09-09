"""Small in-process provider/model registry and deterministic resolver.

Provider identity is durable; model identity is replaceable runtime state.  This
module deliberately has no presentation, persistence, or transport concerns.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional


@dataclass(frozen=True)
class ModelCandidate:
    model_id: str
    modes: tuple[str, ...] = ("coding", "research", "thinking", "general")
    free_class: str = "free_allocation"
    family: str = "unknown"


@dataclass(frozen=True)
class ModelResolution:
    model_id: str
    source: str
    provider: str
    mode: str
    family: str
    free_class: str


# Central bootstrap policy.  These are bounded known-good candidates, not
# permanent adapter truth. Discovery can supersede them when a provider exposes
# a usable catalogue. Paid-only candidates are intentionally absent here.
REGISTRY: dict[str, tuple[ModelCandidate, ...]] = {
    "groq": (
        ModelCandidate("openai/gpt-oss-20b", family="gpt-oss"),
    ),
    "gemini": (
        ModelCandidate("gemini-flash-latest", family="gemini"),
    ),
    "cloudflare": (
        ModelCandidate("@cf/meta/llama-3.1-8b-instruct-fp8", family="llama"),
    ),
    "deepseek": (
        ModelCandidate("deepseek-v4-flash", free_class="paid_optional", family="deepseek"),
    ),
    "huggingface": (
        ModelCandidate("openai/gpt-oss-20b:cheapest", family="gpt-oss"),
    ),
    # OpenRouter's free router is itself a dynamic same-provider model resolver.
    # When the response exposes the concrete upstream model, adapters persist it
    # as actual_model so provenance is not lost.
    "openrouter": (
        ModelCandidate("openrouter/free", family="dynamic-free-router"),
    ),
}


def _normalise_ids(items: Iterable[object]) -> tuple[str, ...]:
    result: list[str] = []
    for item in items or ():
        value = getattr(item, "id", item)
        if not isinstance(value, str):
            continue
        value = value.strip()
        if value and value not in result:
            result.append(value)
    return tuple(result)


def resolve_model(
    provider: str,
    mode: str,
    *,
    discover: Optional[Callable[[], Iterable[object]]] = None,
    allow_paid: bool = False,
) -> Optional[ModelResolution]:
    """Resolve one model deterministically without ever changing provider.

    Discovery is advisory and boring-failure safe. A discovered catalogue only
    validates/selects registry policy candidates; arbitrary catalogue ordering
    cannot silently opt the application into a paid model. If discovery fails or
    is malformed, the first eligible bootstrap candidate is used.
    """
    provider_id = str(provider or "").strip().lower()
    task_mode = str(mode or "general").strip().lower()
    candidates = [
        item for item in REGISTRY.get(provider_id, ())
        if task_mode in item.modes or "general" in item.modes
        if allow_paid or item.free_class != "paid_optional"
    ]
    if not candidates:
        return None

    discovered: tuple[str, ...] = ()
    discovery_ok = False
    if discover is not None:
        try:
            discovered = _normalise_ids(discover())
            discovery_ok = bool(discovered)
        except Exception:
            discovered = ()

    if discovery_ok:
        discovered_set = set(discovered)
        for item in candidates:
            if item.model_id in discovered_set:
                return ModelResolution(item.model_id, "discovered", provider_id, task_mode, item.family, item.free_class)
        # Catalogue was authoritative enough to say none of our bounded
        # candidates exists. Do not call a stale/deprecated ID.
        return None

    item = candidates[0]
    return ModelResolution(item.model_id, "registry_fallback", provider_id, task_mode, item.family, item.free_class)


def openai_catalog(client) -> tuple[str, ...]:
    """Read model ids from OpenAI-compatible clients without assuming pager type."""
    page = client.models.list()
    data = getattr(page, "data", page)
    return _normalise_ids(data)
