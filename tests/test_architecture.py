import pytest
from providers.base import BaseProvider
from agents.router import ModelRouter
from agents.base import BaseAgent
from agents.role_agent import RoleAgent
from agents.unified_agent import UnifiedAgent
from agents.gemini import GeminiAgent
from agents.groq import GroqAgent
from agents.cloudflare import CloudflareAgent
from agents.coze import CozeAgent
from core.debate import DebateOrchestrator

# A mock provider for testing
class MockProvider(BaseProvider):
    def __init__(self, name, fail=False, rate_limit=False, return_text="Success"):
        super().__init__(name)
        self.fail = fail
        self.rate_limit = rate_limit
        self.return_text = return_text
        self.call_count = 0

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096, **kwargs):
        self.call_count += 1
        if self.rate_limit:
            return {
                "status": "error",
                "text": "429 Rate limit exceeded",
                "agent": self.name,
                "tokens": 0,
                "cost": 0.0
            }
        if self.fail:
            return {
                "status": "error",
                "text": "Some API error occurred",
                "agent": self.name,
                "tokens": 0,
                "cost": 0.0
            }
        return {
            "status": "success",
            "text": self.return_text,
            "agent": self.name,
            "tokens": 10,
            "cost": 0.0001
        }

def test_provider_availability():
    provider = MockProvider("TestProvider")
    assert provider.name == "TestProvider"
    assert provider.is_available is True

    provider.set_availability(False, "Rate limit")
    assert provider.is_available is False
    assert provider.last_error == "Rate limit"

def test_router_routing_and_failover():
    p1 = MockProvider("Primary", rate_limit=True)
    p2 = MockProvider("Secondary", return_text="Hello from secondary")

    router = ModelRouter([p1, p2])
    response = router.generate("test task")

    assert response["status"] == "success"
    assert response["text"] == "Hello from secondary"
    assert response["agent"] == "Secondary"
    assert p1.call_count == 1
    assert p2.call_count == 1

    response2 = router.generate("another task")
    assert response2["text"] == "Hello from secondary"
    assert p1.call_count == 1
    assert p2.call_count == 2

def test_role_agent_execution_with_skill():
    p = MockProvider("GeminiProvider", return_text="Executed code successfully")
    router = ModelRouter([p])

    skill_prompt = "You are an EXPERT CODER. Always write docstrings."
    agent = RoleAgent(role="Senior Coder", skill=skill_prompt, router=router)

    response = agent.execute("Write quicksort")
    assert response["status"] == "success"
    assert response["text"] == "Executed code successfully"
    assert response["agent_role"] == "Senior Coder"
    assert p.call_count == 1

def test_compatibility_adapters():
    gemini = GeminiAgent(api_key="")
    assert gemini.model is None
    assert "not configured" in gemini.model_name

    groq = GroqAgent(api_key="")
    assert groq.client is None
    assert "not configured" in groq.model_name

def test_unified_agent_structure():
    api_keys = {
        "gemini_key": "dummy_gemini",
        "groq_key": "dummy_groq"
    }
    unified = UnifiedAgent(api_keys)

    assert len(unified.providers) == 2
    names = [p["name"] for p in unified.providers]
    assert "🔍 Gemini" in names
    assert "⚡ Groq" in names

    avail = unified.get_available_providers()
    assert "🔍 Gemini" in avail
    assert "⚡ Groq" in avail

    stats = unified.get_stats()
    assert "🔍 Gemini" in stats
    assert stats["🔍 Gemini"]["success"] == 0
    assert stats["🔍 Gemini"]["rate_limited"] is False

def test_legacy_adapters_signature_safety():
    cf = CloudflareAgent(api_key="")
    response_cf = cf.generate("prompt", "sys", 1000, "general")
    assert response_cf["status"] == "error"

    coze = CozeAgent(api_key="")
    response_coze = coze.generate("prompt", "sys", 3, 2000)
    assert response_coze["status"] == "error"

def test_debate_orchestrator_agent_centric():
    p_cf = MockProvider("Cloudflare", return_text="Response from Cloudflare provider")
    p_groq = MockProvider("Groq", return_text="Response from Groq provider")

    orchestrator = DebateOrchestrator(
        gemini_agent=None,
        cloudflare_agent=p_cf,
        groq_agent=p_groq
    )

    log = orchestrator.debate(
        prompt="Analyze my design pattern",
        agents=["cloudflare", "groq"],
        mode="coding"
    )

    assert log["status"] == "success"
    assert len(log["responses"]) == 2

    resp_cf = log["responses"][0]
    resp_groq = log["responses"][1]

    assert resp_cf["status"] == "success"
    assert "Lead Developer" in resp_cf["agent"]
    assert "Cloudflare" in resp_cf["agent"]
    assert "Response from Cloudflare provider" in resp_cf["text"]

    assert resp_groq["status"] == "success"
    assert "Senior Architect" in resp_groq["agent"]
    assert "Groq" in resp_groq["agent"]
    assert "Response from Groq provider" in resp_groq["text"]

def test_role_agent_failover_and_fallback():
    # Prove that one RoleAgent can use a router with multiple providers and perform fallback when the first provider fails
    p_failing = MockProvider("FailingPrimary", fail=True)
    p_healthy = MockProvider("HealthyBackup", return_text="Hello from backup provider")

    router = ModelRouter([p_failing, p_healthy])

    role_agent = RoleAgent(
        role="Systems Engineer",
        skill="Write efficient scripts.",
        router=router
    )

    response = role_agent.execute("Write standard script")

    # Assert successful fallback response
    assert response["status"] == "success"
    assert response["text"] == "Hello from backup provider"
    assert response["agent"] == "HealthyBackup"

    # Assert call count verification
    assert p_failing.call_count == 1
    assert p_healthy.call_count == 1
