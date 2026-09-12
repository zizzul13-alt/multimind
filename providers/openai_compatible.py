"""Generic server-side OpenAI-compatible resource discovery and execution.

The API key never leaves the provider boundary.  Discovery trusts only what the
configured endpoint itself declares; it does not pretend that a declared model
ID proves upstream provenance.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlparse

from openai import OpenAI

from providers.base import BaseProvider
from providers.model_registry import openai_catalog
from utils.config import Config
from utils.error_handler import error_logger


@dataclass(frozen=True)
class OpenAICompatibleResourceSpec:
    resource_id: str
    base_url: str
    api_key: str
    label: str = ""


def _safe_resource_id(value: object) -> str:
    raw = str(value or "").strip().lower().replace("_", "-")
    return "".join(ch for ch in raw if ch.isalnum() or ch in {"-", "."}).strip("-.")


def normalize_resource_spec(spec: Mapping[str, object] | OpenAICompatibleResourceSpec) -> OpenAICompatibleResourceSpec | None:
    if isinstance(spec, OpenAICompatibleResourceSpec):
        candidate = spec
    elif isinstance(spec, Mapping):
        candidate = OpenAICompatibleResourceSpec(
            resource_id=_safe_resource_id(spec.get("id") or spec.get("resource_id")),
            base_url=str(spec.get("base_url") or "").strip().rstrip("/"),
            api_key=str(spec.get("api_key") or spec.get("key") or "").strip(),
            label=str(spec.get("label") or "").strip(),
        )
    else:
        return None

    parsed = urlparse(candidate.base_url)
    if (
        not candidate.resource_id
        or not candidate.api_key
        or parsed.scheme not in {"http", "https"}
        or not parsed.netloc
    ):
        return None
    return candidate


def _route_id(resource_id: str, model_id: str) -> str:
    digest = hashlib.sha256(model_id.encode("utf-8")).hexdigest()[:10]
    return f"resource:{resource_id}:{digest}"


class OpenAICompatibleProvider(BaseProvider):
    """One concrete model route discovered from an OpenAI-compatible endpoint."""

    def __init__(self, spec: OpenAICompatibleResourceSpec, model_id: str, *, client=None):
        self.resource_id = spec.resource_id
        self.resource_label = spec.label or spec.resource_id
        self.base_url = spec.base_url
        self.discovered_model_id = str(model_id or "").strip()
        self.identity_provenance = "declared_by_provider_catalog"
        super().__init__(self.resource_label)
        self.model_name = self.discovered_model_id
        self.client = client or OpenAI(
            api_key=spec.api_key,
            base_url=spec.base_url,
            timeout=Config.API_TIMEOUT,
            max_retries=0,
        )
        self.set_availability(bool(self.discovered_model_id), None if self.discovered_model_id else "model_not_configured")

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 4096, **kwargs) -> dict:
        if not self.discovered_model_id:
            return self.failure_response("no_eligible_model")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            response = self.client.chat.completions.create(
                model=self.discovered_model_id,
                messages=messages,
                max_tokens=max_tokens,
            )
            choice = response.choices[0]
            text = getattr(getattr(choice, "message", None), "content", None)
            if not isinstance(text, str) or not text.strip():
                self.set_availability(False, "Malformed or empty response")
                return self.failure_response("malformed_response")
            actual_model = str(getattr(response, "model", "") or self.discovered_model_id)
            usage = getattr(response, "usage", None)
            tokens = int(getattr(usage, "total_tokens", 0) or 0)
            self.model_name = actual_model
            self.set_availability(True)
            return {
                "status": "success",
                "text": text,
                "agent": self.resource_label,
                "tokens": tokens,
                "cost": 0.0,
                "resolved_model": self.discovered_model_id,
                "actual_model": actual_model,
                "model_resolution_source": "provider_catalog_discovery",
                "identity_provenance": self.identity_provenance,
                "resource_id": self.resource_id,
            }
        except Exception as exc:
            self.set_availability(False, type(exc).__name__)
            error_logger.log(
                "PROVIDER_FAILURE",
                f"provider=OpenAICompatible resource={self.resource_id} category=network_or_sdk_exception exception_type={type(exc).__name__}",
            )
            return self.failure_response("network_or_sdk_exception", exception_type=type(exc).__name__)


def discover_resource_providers(
    spec: Mapping[str, object] | OpenAICompatibleResourceSpec,
    *,
    client_factory=OpenAI,
    max_models: int = 128,
) -> dict[str, OpenAICompatibleProvider]:
    """Discover endpoint-declared models and return concrete server-side routes.

    Discovery failure is boring: the resource contributes zero routes while the
    rest of MultiMind remains operational. Unknown model identities may exist in
    the returned routes but are not exposed as selectable AI identities until the
    application identity layer can conservatively classify them.
    """
    normalized = normalize_resource_spec(spec)
    if normalized is None:
        return {}
    try:
        client = client_factory(
            api_key=normalized.api_key,
            base_url=normalized.base_url,
            timeout=Config.API_TIMEOUT,
            max_retries=0,
        )
        model_ids = openai_catalog(client)
    except Exception as exc:
        error_logger.log(
            "PROVIDER_DISCOVERY_FAILURE",
            f"resource={normalized.resource_id} exception_type={type(exc).__name__}",
        )
        return {}

    routes: dict[str, OpenAICompatibleProvider] = {}
    for model_id in model_ids[: max(0, int(max_models))]:
        route_id = _route_id(normalized.resource_id, model_id)
        routes[route_id] = OpenAICompatibleProvider(normalized, model_id, client=client)
    return routes
