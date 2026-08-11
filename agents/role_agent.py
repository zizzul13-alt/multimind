from agents.base import BaseAgent

class RoleAgent(BaseAgent):
    """
    A generic role-based agent implementing specified Role/Skill capabilities.
    """
    def __init__(self, role: str, skill: str = None, router = None):
        super().__init__(role, skill, router)

    def execute(self, task: str, mode: str = "coding", max_tokens: int = 4096, preferred_provider_name: str = None) -> dict:
        """
        Execute the task with the configured skill (system prompt instructions) via router.
        """
        if not self.router:
            return {
                "status": "error",
                "text": "Agent has no configured ModelRouter.",
                "agent": self.role,
                "tokens": 0,
                "cost": 0.0
            }

        # Apply skill prompt instructions
        system_prompt = self.skill if self.skill else f"You are a helpful AI assistant acting as a {self.role}."

        # Generate response using model/provider router
        response = self.router.generate(
            prompt=task,
            system_prompt=system_prompt,
            mode=mode,
            max_tokens=max_tokens,
            preferred_provider_name=preferred_provider_name
        )

        if response.get("status") == "success":
            response["agent_role"] = self.role

        return response
