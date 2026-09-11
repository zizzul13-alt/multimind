from providers.base import BaseProvider
from utils.error_handler import error_logger


TERMINAL_PROVIDER_FAILURE_TEXT = "AI providers are temporarily unavailable. Please try again."


def _log_provider_failure(name, response=None, exception_type=None):
    category = response.get("failure_category", "provider_error") if isinstance(response, dict) else "provider_exception"
    details = f"provider={name} category={category}"
    if isinstance(response, dict) and response.get("status_code") is not None:
        details += f" status_code={response['status_code']}"
    safe_exception_type = exception_type or (response.get("exception_type") if isinstance(response, dict) else None)
    if safe_exception_type:
        details += f" exception_type={safe_exception_type}"
    error_logger.log("PROVIDER_FAILURE", details)


def _is_rate_limited(response):
    """Recognize sanitized metadata and legacy provider text without exposing raw errors."""
    if not isinstance(response, dict):
        return False
    if response.get("status_code") == 429 or response.get("failure_category") == "rate_limited":
        return True
    text = response.get("text", "")
    return isinstance(text, str) and ("429" in text or "rate limit" in text.lower())


def _sanitized_failure(response=None, *, exception_type=None):
    """Keep only bounded diagnostics that are safe to persist or surface internally."""
    if isinstance(response, dict):
        return {
            "failure_category": response.get("failure_category", "provider_error"),
            "status_code": response.get("status_code"),
            "exception_type": response.get("exception_type"),
        }
    return {
        "failure_category": "provider_exception",
        "status_code": None,
        "exception_type": exception_type,
    }


class ModelRouter:
    """Provider routing with bounded fallback and sanitized diagnostics."""

    def __init__(self, providers: list):
        self.providers = providers
        self.stats = {p.name: {"success": 0, "error": 0, "rate_limited": False, "last_error": ""} for p in providers}

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 4096, preferred_provider_name: str = None) -> dict:
        ordered_providers = list(self.providers)
        if preferred_provider_name:
            wanted = preferred_provider_name.lower()
            pref = [p for p in self.providers if p.name.lower() == wanted or wanted in p.name.lower()]
            rest = [p for p in self.providers if p not in pref]
            ordered_providers = pref + rest

        last_failure = None
        for provider in ordered_providers:
            name = provider.name
            self.stats.setdefault(name, {"success": 0, "error": 0, "rate_limited": False, "last_error": ""})
            if self.stats[name]["rate_limited"]:
                continue
            try:
                response = provider.generate(prompt=prompt, system_prompt=system_prompt, mode=mode, max_tokens=max_tokens)
                if response.get("status") == "error":
                    last_failure = _sanitized_failure(response)
                    failure_category = response.get("failure_category", "provider_error")
                    if _is_rate_limited(response):
                        self.stats[name]["rate_limited"] = True
                        self.stats[name]["last_error"] = "Rate limited"
                        provider.set_availability(False, "Rate limited")
                    else:
                        self.stats[name]["error"] += 1
                        self.stats[name]["last_error"] = failure_category
                        provider.set_availability(False, failure_category)
                    _log_provider_failure(name, response)
                    continue
                if BaseProvider.has_usable_response(response):
                    self.stats[name]["success"] += 1
                    self.stats[name]["rate_limited"] = False
                    provider.set_availability(True)
                    return response
                self.stats[name]["error"] += 1
                self.stats[name]["last_error"] = "Empty or malformed response"
                provider.set_availability(False, "Empty or malformed response")
                last_failure = _sanitized_failure({"failure_category": "empty_response"})
                _log_provider_failure(name, {"failure_category": "empty_response"})
            except Exception as e:
                self.stats[name]["error"] += 1
                self.stats[name]["last_error"] = type(e).__name__
                provider.set_availability(False, type(e).__name__)
                last_failure = _sanitized_failure(exception_type=type(e).__name__)
                _log_provider_failure(name, exception_type=type(e).__name__)

        # If every route failed, allow a later independent request to retry all providers.
        for name in self.stats:
            self.stats[name]["rate_limited"] = False
        terminal = {
            "status": "error",
            "text": TERMINAL_PROVIDER_FAILURE_TEXT,
            "agent": "Router",
            "tokens": 0,
            "cost": 0.0,
        }
        if last_failure:
            terminal.update({key: value for key, value in last_failure.items() if value is not None})
        return terminal

    def reset_rate_limits(self):
        for name in self.stats:
            self.stats[name]["rate_limited"] = False
