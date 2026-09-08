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
        self.model_name = name

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
    assert log["selected_participants"] == 2
    assert len(log["participants"]) == 2
    assert [item["requested_provider"] for item in log["participants"]] == ["cloudflare", "groq"]
    # 2 participant calls + one judge/synthesis utility response in legacy response log.
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

def test_debate_independent_participants_then_separate_judge_utility():
    p_a = MockProvider(
        "Cloudflare",
        return_text="Pristine code block containing ```python\ndef hello_a(): pass\n``` that serves as Candidate A.",
        fail_after_calls=2,
    )
    p_b = MockProvider(
        "Groq",
        return_text="Excellent code block containing ```python\ndef hello_b(): pass\n``` that serves as Candidate B.",
        fail_after_calls=2,
    )
    p_c = MockProvider(
        "OpenRouter",
        return_text="Clean code block containing ```python\ndef hello_c(): pass\n``` that serves as Candidate C.",
        fail_after_calls=2,
    )
    p_d = MockProvider(
        "DeepSeek",
        return_text="DeepSeek contribution and synthesis with ```python\ndef hello_d(): pass\n``` that is long enough.",
    )

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

    # Every selected participant independently receives the original task once.
    assert len(log["participants"]) == 4
    assert [item["requested_provider"] for item in log["participants"]] == [
        "cloudflare", "groq", "openrouter", "deepseek"
    ]
    for provider in (p_a, p_b, p_c, p_d):
        assert "Analyze my design pattern" in provider.last_prompts[0]
        assert "INDEPENDENT PARTICIPANT CONTRIBUTIONS" not in provider.last_prompts[0]

    # Judge routing is separate utility work. A/B/C fail their second call so D
    # services synthesis; actual provider provenance is explicit.
    assert p_d.call_count == 2
    assert "participant-1-cloudflare" in p_d.last_prompts[1]
    assert "participant-2-groq" in p_d.last_prompts[1]
    assert "participant-3-openrouter" in p_d.last_prompts[1]
    assert "participant-4-deepseek" in p_d.last_prompts[1]
    assert log["judge"]["status"] == "success"
    assert log["judge"]["actual_provider"] == "DeepSeek"

    assert log["status"] == "success"
    assert "DeepSeek contribution and synthesis" in log["final_answer"]
    assert "gate_score" in log
    assert log["gate_score"] is not None

def test_judge_failure_fallback_with_independent_participants():
    p_a = MockProvider(
        "Cloudflare",
        return_text="Pristine code block containing ```python\ndef hello_a(): pass\n``` that serves as Candidate A.",
        fail_after_calls=2,
    )
    p_b = MockProvider(
        "Groq",
        return_text="Excellent code block containing ```python\ndef hello_b(): pass\n``` that serves as Candidate B.",
        fail_after_calls=2,
    )
    p_c = MockProvider(
        "OpenRouter",
        return_text="Clean code block containing ```python\ndef hello_c(): pass\n``` that serves as Candidate C.",
        fail_after_calls=2,
    )
    p_d_failed = MockProvider(
        "DeepSeek",
        return_text="Independent DeepSeek candidate that is long enough to be usable.",
        fail_after_calls=2,
    )

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

    assert log["status"] == "success"
    assert len(log["participants"]) == 4
    assert log["judge"]["status"] == "error"
    assert log["judge"]["fallback_participant_id"] == "participant-1-cloudflare"
    assert "Candidate A" in log["final_answer"]

def test_partial_candidate_failures():
    p_a = MockProvider("Cloudflare", fail=True)
    p_b = MockProvider(
        "Groq",
        return_text="Excellent code block containing ```python\ndef hello_b(): pass\n``` that serves as Candidate B.",
        fail_after_calls=2,
    )
    p_c = MockProvider(
        "OpenRouter",
        return_text="Clean code block containing ```python\ndef hello_c(): pass\n``` that serves as Candidate C.",
        fail_after_calls=2,
    )
    p_d = MockProvider(
        "DeepSeek",
        return_text="I am the DeepSeek contribution/synthesis evaluating the successful participants with enough detail.",
    )

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
    assert log["participants"][0]["status"] == "error"
    assert log["participants"][0]["requested_provider"] == "cloudflare"
    assert log["successful_participants"] == 3
    assert log["judge"]["actual_provider"] == "DeepSeek"
    judge_prompt = p_d.last_prompts[1]
    assert "participant-2-groq" in judge_prompt
    assert "participant-3-openrouter" in judge_prompt
    assert "participant-4-deepseek" in judge_prompt
    assert "participant-1-cloudflare" not in judge_prompt
