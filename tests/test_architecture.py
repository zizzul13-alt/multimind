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
    def __init__(self, name, fail=False, rate_limit=False, return_text="Success", fail_after_calls=None):
        super().__init__(name)
        self.fail = fail
        self.rate_limit = rate_limit
        self.return_text = return_text
        self.fail_after_calls = fail_after_calls
        self.call_count = 0
        self.last_prompts = []

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096, **kwargs):
        self.call_count += 1
        self.last_prompts.append(prompt)

        if self.fail_after_calls is not None and self.call_count >= self.fail_after_calls:
            return {
                "status": "error",
                "text": "Some API error occurred after call count limit",
                "agent": self.name,
                "tokens": 0,
                "cost": 0.0
            }

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
    assert len(log["responses"]) == 4

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

def test_debate_parallel_collaboration_pipeline_with_judge():
    p_a = MockProvider("Cloudflare", return_text="Pristine code block containing ```python\ndef hello_a(): pass\n``` that serves as Candidate A.")
    p_b = MockProvider("Groq", return_text="Excellent code block containing ```python\ndef hello_b(): pass\n``` that serves as Candidate B.")
    p_c = MockProvider("OpenRouter", return_text="Clean code block containing ```python\ndef hello_c(): pass\n``` that serves as Candidate C.")
    p_d = MockProvider("DeepSeek", return_text="I am the judge. I select Candidate B with ```python\ndef hello_b(): pass\n``` because it is the most optimized.")

    orchestrator = DebateOrchestrator(
        gemini_agent=None,
        cloudflare_agent=p_a,
        groq_agent=p_b,
        openrouter_agent=p_c,
        deepseek_agent=p_d
    )

    log = orchestrator.debate(
        prompt="Analyze my design pattern",
        agents=["cloudflare", "groq", "openrouter", "deepseek"],
        mode="coding"
    )

    # 1. Verify parallel candidates generated from ORIGINAL task prompt
    assert p_a.call_count == 1
    assert "Analyze my design pattern" in p_a.last_prompts[0]

    assert p_b.call_count == 1
    assert "Analyze my design pattern" in p_b.last_prompts[0]
    assert "Candidate A" not in p_b.last_prompts[0]  # Indenpendent candidate B

    assert p_c.call_count == 1
    assert "Analyze my design pattern" in p_c.last_prompts[0]
    assert "Candidate A" not in p_c.last_prompts[0]
    assert "Candidate B" not in p_c.last_prompts[0]  # Independent candidate C

    # 2. Verify Judge evaluates all successfully generated candidates collectively
    assert p_d.call_count == 1
    assert "Analyze my design pattern" in p_d.last_prompts[0]
    assert "Candidate A" in p_d.last_prompts[0]
    assert "Candidate B" in p_d.last_prompts[0]
    assert "Candidate C" in p_d.last_prompts[0]

    # 3. Verify Judge output becomes the final candidate
    assert log["status"] == "success"
    assert "I am the judge" in log["final_answer"]
    assert "Candidate A" not in log["final_answer"]
    assert "Candidate C" not in log["final_answer"]

    # 4. Verify Release Gate executes on the Judge's final candidate
    assert "gate_score" in log
    assert log["gate_score"] is not None
    assert log["gate_passed"] is True

def test_judge_failure_fallback_with_parallel():
    p_a = MockProvider("Cloudflare", return_text="Pristine code block containing ```python\ndef hello_a(): pass\n``` that serves as Candidate A.", fail_after_calls=2)
    p_b = MockProvider("Groq", return_text="Excellent code block containing ```python\ndef hello_b(): pass\n``` that serves as Candidate B.", fail_after_calls=2)
    p_c = MockProvider("OpenRouter", return_text="Clean code block containing ```python\ndef hello_c(): pass\n``` that serves as Candidate C.", fail_after_calls=2)
    p_d_failed = MockProvider("DeepSeek", fail=True)

    orchestrator = DebateOrchestrator(
        gemini_agent=None,
        cloudflare_agent=p_a,
        groq_agent=p_b,
        openrouter_agent=p_c,
        deepseek_agent=p_d_failed
    )

    log = orchestrator.debate(
        prompt="Analyze my design pattern",
        agents=["cloudflare", "groq", "openrouter", "deepseek"],
        mode="coding"
    )

    # Output should fall back gracefully to the first successful candidate (Candidate A)
    assert log["status"] == "success"
    assert "Candidate A" in log["final_answer"]

def test_partial_candidate_failures():
    # Verify that Judge continues to work even if some candidates fail
    p_a = MockProvider("Cloudflare", fail=True)
    p_b = MockProvider("Groq", return_text="Excellent code block containing ```python\ndef hello_b(): pass\n``` that serves as Candidate B.")
    p_c = MockProvider("OpenRouter", return_text="Clean code block containing ```python\ndef hello_c(): pass\n``` that serves as Candidate C.")
    p_d = MockProvider("DeepSeek", return_text="I am the judge evaluating the successful candidates.")

    orchestrator = DebateOrchestrator(
        gemini_agent=None,
        cloudflare_agent=p_a,
        groq_agent=p_b,
        openrouter_agent=p_c,
        deepseek_agent=p_d
    )

    log = orchestrator.debate(
        prompt="Analyze my design pattern",
        agents=["cloudflare", "groq", "openrouter", "deepseek"],
        mode="coding"
    )

    assert log["status"] == "success"
    assert "I am the judge evaluating the successful candidates" in log["final_answer"]
    # Candidate A failed, so Judge prompt must contain B and C, but not A
    assert "Candidate B" in p_d.last_prompts[0]
    assert "Candidate C" in p_d.last_prompts[0]
    assert "Candidate A" not in p_d.last_prompts[0]
