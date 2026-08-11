from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Base class representing an Agent role/capability.
    """
    def __init__(self, role: str, skill: str = None, router = None):
        self.role = role
        self.skill = skill  # Instruction prompt/capability
        self.router = router  # ModelRouter instance

    @abstractmethod
    def execute(self, task: str, mode: str = "coding", max_tokens: int = 4096) -> dict:
        """
        Execute the assigned task.
        """
        pass
