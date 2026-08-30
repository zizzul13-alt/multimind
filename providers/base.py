from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """
    Base class representing an AI service/API Provider.
    """
    def __init__(self, name: str):
        self.name = name
        self.is_available = True
        self.last_error = ""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 4096, **kwargs) -> dict:
        """
        Generate response from the provider.
        Returns a dict with:
        - "status": "success" | "error"
        - "text": str (the generated content or error message)
        - "agent": str (the provider/model identification name)
        - "tokens": int (token count used or estimated)
        - "cost": float (calculated cost or 0.0)
        """
        pass

    def set_availability(self, available: bool, error_msg: str = ""):
        self.is_available = available
        self.last_error = error_msg

    @staticmethod
    def has_usable_response(response) -> bool:
        """Return whether a provider result contains mechanically usable text."""
        return (
            isinstance(response, dict)
            and response.get("status") == "success"
            and isinstance(response.get("text"), str)
            and bool(response["text"].strip())
        )

    def failure_response(self, category: str, *, exception_type: str = None, status_code: int = None) -> dict:
        """Build a sanitized provider-level failure result.

        Terminal wording belongs to the existing router/application boundaries.
        """
        result = {
            "status": "error",
            "text": "Provider temporarily unavailable. Trying another provider.",
            "agent": self.model_name if hasattr(self, "model_name") else self.name,
            "tokens": 0,
            "cost": 0.0,
            "failure_category": category,
        }
        if exception_type:
            result["exception_type"] = exception_type
        if status_code is not None:
            result["status_code"] = status_code
        return result
