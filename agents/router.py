from providers.base import BaseProvider

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

                    if "429" in error_text or "rate" in error_text.lower():
                        self.stats[name]["rate_limited"] = True
                        self.stats[name]["last_error"] = "Rate limited"
                        provider.set_availability(False, "Rate limited")
                        continue

                    self.stats[name]["error"] += 1
                    self.stats[name]["last_error"] = error_text[:100]
                    provider.set_availability(False, error_text[:100])
                    continue

                if response.get("status") == "success":
                    self.stats[name]["success"] += 1
                    self.stats[name]["rate_limited"] = False
                    provider.set_availability(True)
                    return response

            except Exception as e:
                error_msg = str(e)
                self.stats[name]["error"] += 1
                self.stats[name]["last_error"] = error_msg[:100]
                provider.set_availability(False, error_msg[:100])
                continue

        # Reset rate limit flags after all failed
        for name in self.stats:
            self.stats[name]["rate_limited"] = False
            for p in self.providers:
                if p.name == name:
                    p.set_availability(True)

        return {
            "status": "error",
            "text": "❌ Semua provider gagal",
            "agent": "Router",
            "tokens": 0,
            "cost": 0.0
        }

    def reset_rate_limits(self):
        for name in self.stats:
            self.stats[name]["rate_limited"] = False
