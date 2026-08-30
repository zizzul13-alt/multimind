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

class ModelRouter:
    """
    Decides which model/provider should execute the task.
    Handles auto-failover/fallback.
    """
    def __init__(self, providers: list):
        self.providers = providers  # List of BaseProvider instances
        self.stats = {}
        for p in self.providers:
            self.stats[p.name] = {
                "success": 0,
                "error": 0,
                "rate_limited": False,
                "last_error": ""
            }

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 4096, preferred_provider_name: str = None) -> dict:
        """
        Generate response with auto-failover + rate limit handling
        """
        ordered_providers = list(self.providers)
        if preferred_provider_name:
            pref = [p for p in self.providers if p.name.lower() == preferred_provider_name.lower() or preferred_provider_name.lower() in p.name.lower()]
            rest = [p for p in self.providers if not (p.name.lower() == preferred_provider_name.lower() or preferred_provider_name.lower() in p.name.lower())]
            ordered_providers = pref + rest

        for provider in ordered_providers:
            name = provider.name

            if name not in self.stats:
                self.stats[name] = {
                    "success": 0,
                    "error": 0,
                    "rate_limited": False,
                    "last_error": ""
                }

            if self.stats[name]["rate_limited"]:
                continue

            try:
                # Call generate on provider with all possible kwargs
                response = provider.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    mode=mode,
                    max_tokens=max_tokens
                )

                if response.get("status") == "error":
                    error_text = response.get("text", "")
                    failure_category = response.get("failure_category", "provider_error")

                    if "429" in error_text or "rate" in error_text.lower():
                        self.stats[name]["rate_limited"] = True
                        self.stats[name]["last_error"] = "Rate limited"
                        provider.set_availability(False, "Rate limited")
                        _log_provider_failure(name, response)
                        continue

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
                _log_provider_failure(name, {"failure_category": "empty_response"})
                continue

            except Exception as e:
                self.stats[name]["error"] += 1
                self.stats[name]["last_error"] = type(e).__name__
                provider.set_availability(False, type(e).__name__)
                _log_provider_failure(name, exception_type=type(e).__name__)
                continue

        # Reset rate limit flags after all failed
        for name in self.stats:
            self.stats[name]["rate_limited"] = False
            for p in self.providers:
                if p.name == name:
                    p.set_availability(True)

        return {
            "status": "error",
            "text": TERMINAL_PROVIDER_FAILURE_TEXT,
            "agent": "Router",
            "tokens": 0,
            "cost": 0.0
        }

    def reset_rate_limits(self):
        for name in self.stats:
            self.stats[name]["rate_limited"] = False
