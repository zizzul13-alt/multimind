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
