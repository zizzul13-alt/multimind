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
        self.last_prompt = ""

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096, **kwargs):
        self.call_count += 1
        self.last_prompt = prompt
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
    p_cf = MockProvider("Cloudflare", return_text="Response from Cloudflare provider that is long enough to pass length gate")
    p_groq = MockProvider("Groq", return_text="Response from Groq provider that is also long enough to pass length gate")

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
    # Even if 2 agents selected, it executes all 3 stages of collaboration pipeline
    assert len(log["responses"]) == 3

def test_role_agent_failover_and_fallback():
    p_failing = MockProvider("FailingPrimary", fail=True)
    p_healthy = MockProvider("HealthyBackup", return_text="Hello from backup provider")

    router = ModelRouter([p_failing, p_healthy])

    role_agent = RoleAgent(
        role="Systems Engineer",
        skill="Write efficient scripts.",
        router=router
    )

    response = role_agent.execute("Write standard script")

    assert response["status"] == "success"
    assert response["text"] == "Hello from backup provider"
    assert response["agent"] == "HealthyBackup"

    assert p_failing.call_count == 1
    assert p_healthy.call_count == 1

def test_debate_collaboration_pipeline():
    p_a = MockProvider("Cloudflare", return_text="Pristine code block containing ```python\ndef hello(): pass\n``` that serves as our first draft response.")
    p_b = MockProvider("Groq", return_text="This is a constructive critique identifying issues with performance and code styling.")
    p_c = MockProvider("OpenRouter", return_text="An extremely polished final answer incorporating all the reviewer's critique on the draft and fixing style issues with ```python\ndef hello_final(): pass\n```.")

    orchestrator = DebateOrchestrator(
        gemini_agent=None,
        cloudflare_agent=p_a,
        groq_agent=p_b,
        openrouter_agent=p_c
    )

    log = orchestrator.debate(
        prompt="Analyze my design pattern",
        agents=["cloudflare", "groq", "openrouter"],
        mode="coding"
    )

    # 1. Verify Draft -> Review (Agent B gets Agent A's output as context)
    assert p_b.call_count == 1
    assert "Pristine code block" in p_b.last_prompt
    assert "Analyze my design pattern" in p_b.last_prompt

    # 2. Verify Review -> Improve (Agent C gets both Draft and Review as context)
    assert p_c.call_count == 1
    assert "Pristine code block" in p_c.last_prompt
    assert "constructive critique" in p_c.last_prompt
    assert "Analyze my design pattern" in p_c.last_prompt

    # 3. Verify Candidate Improvement from Agent C is the ONLY final answer content
    assert log["status"] == "success"
    assert "An extremely polished final answer" in log["final_answer"]
    assert "Pristine code block" not in log["final_answer"]  # Draft must not be concatenated
    assert "constructive critique" not in log["final_answer"]  # Review must not be concatenated

    # 4. Verify Release Gate executes on the final candidate
    assert "gate_score" in log
    assert log["gate_score"] is not None
    assert log["gate_passed"] is True

def test_collaboration_pipeline_with_various_provider_counts():
    p_cf = MockProvider("Cloudflare", return_text="Draft code block containing ```python\ndef test(): pass\n``` to serve as our draft.")
    p_groq = MockProvider("Groq", return_text="Critique of code style, naming, and indentation with suggestions.")
    p_or = MockProvider("OpenRouter", return_text="Highly optimized code block containing ```python\ndef test_final(): pass\n``` integrating the feedback.")

    # A. Test 1 Provider Selected
    orchestrator_1 = DebateOrchestrator(
        gemini_agent=None,
        cloudflare_agent=p_cf
    )
    log_1 = orchestrator_1.debate(
        prompt="Build code",
        agents=["cloudflare"],
        mode="coding"
    )
    # Even with 1 provider, 3 execution stages happen (each using cloudflare)
    assert len(log_1["responses"]) == 3
    assert p_cf.call_count == 3

    # Reset call counts
    p_cf.call_count = 0
    p_groq.call_count = 0

    # B. Test 2 Providers Selected
    orchestrator_2 = DebateOrchestrator(
        gemini_agent=None,
        cloudflare_agent=p_cf,
        groq_agent=p_groq
    )
    log_2 = orchestrator_2.debate(
        prompt="Build code",
        agents=["cloudflare", "groq"],
        mode="coding"
    )
    # Executes exactly 3 collaboration stages
    assert len(log_2["responses"]) == 3
    assert p_cf.call_count == 2   # Slot 1 and Slot 3 (0 % 2 and 2 % 2)
    assert p_groq.call_count == 1  # Slot 2 (1 % 2)
