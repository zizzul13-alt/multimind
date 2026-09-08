"""Behavioral contract for MultiMind's accepted deliberation semantics."""

from core.application import ChatRequest, MultiMindApplication
from core.debate import DebateOrchestrator
from providers.base import BaseProvider


class ScriptedProvider(BaseProvider):
    def __init__(self, name, responses=None):
        super().__init__(name)
        self.model_name = f"{name}-model"
        self.responses = list(responses or [])
        self.calls = []

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096, **kwargs):
        self.calls.append(
            {
                "prompt": prompt,
                "system_prompt": system_prompt,
                "mode": mode,
                "max_tokens": max_tokens,
            }
        )
        if self.responses:
            item = self.responses.pop(0)
            if callable(item):
                return item(prompt)
            return dict(item)
        return {
            "status": "success",
            "text": f"Independent answer from {self.name} with enough detail for verification.",
            "agent": self.model_name,
            "tokens": 10,
            "cost": 0.0,
        }


def ok(name, text=None):
    return {
        "status": "success",
        "text": text or f"Independent answer from {name} with enough detail for verification.",
        "agent": f"{name}-model",
        "tokens": 10,
        "cost": 0.0,
    }


def fail(name, category="timeout"):
    return {
        "status": "error",
        "text": "Provider temporarily unavailable. Trying another provider.",
        "agent": f"{name}-model",
        "tokens": 0,
        "cost": 0.0,
        "failure_category": category,
    }


def _orchestrator(**providers):
    return DebateOrchestrator(
        gemini_agent=providers.get("gemini"),
        deepseek_agent=providers.get("deepseek"),
        groq_agent=providers.get("groq"),
        cloudflare_agent=providers.get("cloudflare"),
        openrouter_agent=providers.get("openrouter"),
        huggingface_agent=providers.get("huggingface"),
    )


def test_selected_count_equals_traceable_participant_attempts_for_one_two_three_and_six():
    ids = ["cloudflare", "groq", "openrouter", "huggingface", "deepseek", "gemini"]
    providers = {name: ScriptedProvider(name) for name in ids}

    for count in (1, 2, 3, 6):
        # Fresh providers avoid judge calls from one case affecting another.
        current = {name: ScriptedProvider(name) for name in ids}
        log = _orchestrator(**current).debate(
            "Build a reliable example implementation",
            agents=ids[:count],
            mode="coding",
            rounds=1,
        )

        assert log["status"] == "success"
        assert log["selected_participants"] == count
        assert len(log["participants"]) == count
        assert [item["requested_provider"] for item in log["participants"]] == ids[:count]
        assert all(item["status"] == "success" for item in log["participants"])
        assert all(item["participant_id"] for item in log["participants"])


def test_participant_failure_is_not_replaced_by_another_selected_provider():
    gemini = ScriptedProvider("gemini", responses=[fail("gemini"), fail("gemini")])
    groq = ScriptedProvider("groq")

    log = _orchestrator(gemini=gemini, groq=groq).debate(
        "Analyze this failure honestly",
        agents=["gemini", "groq"],
        mode="thinking",
        rounds=1,
    )

    assert log["status"] == "success"
    assert len(log["participants"]) == 2

    failed_participant = log["participants"][0]
    healthy_participant = log["participants"][1]
    assert failed_participant["requested_provider"] == "gemini"
    assert failed_participant["status"] == "error"
    assert failed_participant["actual_provider"] == "gemini"
    assert failed_participant["text"] == ""

    assert healthy_participant["requested_provider"] == "groq"
    assert healthy_participant["status"] == "success"
    assert "groq" in healthy_participant["actual_provider"].lower()

    # Gemini's participant attempt is one Gemini call. Groq is not called in its
    # place; any later Groq call belongs to the judge utility and is separately
    # represented in log["judge"].
    candidate_responses = [item for item in log["responses"] if item.get("phase") == "candidate"]
    assert len(candidate_responses) == 2
    assert candidate_responses[0]["participant_id"].endswith("gemini")
    assert candidate_responses[1]["participant_id"].endswith("groq")


def test_unconfigured_selected_participant_is_explicit_failure_not_substitution():
    cloudflare = ScriptedProvider("cloudflare")
    log = _orchestrator(cloudflare=cloudflare).debate(
        "Do the task",
        agents=["cloudflare", "gemini"],
        rounds=1,
    )

    assert log["selected_participants"] == 2
    assert len(log["participants"]) == 2
    missing = log["participants"][1]
    assert missing["requested_provider"] == "gemini"
    assert missing["status"] == "error"
    assert missing["actual_provider"] is None
    assert missing["failure_category"] == "not_configured"


def test_rounds_have_real_bounded_execution_semantics():
    agent_ids = ["cloudflare", "groq"]

    round1 = _orchestrator(
        cloudflare=ScriptedProvider("cloudflare"),
        groq=ScriptedProvider("groq"),
    ).debate("Reason about this", agents=agent_ids, mode="thinking", rounds=1)
    round2 = _orchestrator(
        cloudflare=ScriptedProvider("cloudflare"),
        groq=ScriptedProvider("groq"),
    ).debate("Reason about this", agents=agent_ids, mode="thinking", rounds=2)
    round3 = _orchestrator(
        cloudflare=ScriptedProvider("cloudflare"),
        groq=ScriptedProvider("groq"),
    ).debate("Reason about this", agents=agent_ids, mode="thinking", rounds=3)

    assert round1["deliberation"] == []
    assert len(round2["deliberation"]) == 2
    assert {item["round"] for item in round2["deliberation"]} == {2}
    assert len(round3["deliberation"]) == 4
    assert {item["round"] for item in round3["deliberation"]} == {2, 3}


def test_deliberation_critiques_remain_attributable_to_original_participants():
    cloudflare = ScriptedProvider("cloudflare")
    groq = ScriptedProvider("groq")
    log = _orchestrator(cloudflare=cloudflare, groq=groq).debate(
        "Compare alternatives",
        agents=["cloudflare", "groq"],
        mode="research",
        rounds=2,
    )

    participant_ids = {item["participant_id"] for item in log["participants"]}
    assert len(log["deliberation"]) == 2
    assert {item["participant_id"] for item in log["deliberation"]} == participant_ids
    assert {item["requested_provider"] for item in log["deliberation"]} == {"cloudflare", "groq"}


def test_judge_utility_fallback_reports_actual_provider_without_rewriting_participants():
    gemini = ScriptedProvider(
        "gemini",
        responses=[ok("gemini"), fail("gemini")],
    )
    groq = ScriptedProvider(
        "groq",
        responses=[
            ok("groq"),
            ok(
                "groq",
                "WINNER: participant-2-groq\nFINAL:\nGroq-backed judge synthesis with enough detail for release gate.",
            ),
        ],
    )

    log = _orchestrator(gemini=gemini, groq=groq).debate(
        "Synthesize carefully",
        agents=["gemini", "groq"],
        mode="thinking",
        rounds=1,
    )

    assert [item["requested_provider"] for item in log["participants"]] == ["gemini", "groq"]
    assert all(item["status"] == "success" for item in log["participants"])
    assert log["judge"]["status"] == "success"
    assert "groq" in log["judge"]["actual_provider"].lower()
    assert log["system_verdict"] == "participant-2-groq"
    assert "Groq-backed judge synthesis" in log["final_answer"]


def test_exhausted_judge_preserves_first_successful_candidate_as_explicit_fallback():
    cloudflare = ScriptedProvider(
        "cloudflare",
        responses=[
            ok("cloudflare", "Candidate survives judge failure with enough detail for quality checks."),
            fail("cloudflare"),
        ],
    )

    log = _orchestrator(cloudflare=cloudflare).debate(
        "Do the task",
        agents=["cloudflare"],
        rounds=1,
    )

    assert log["status"] == "success"
    assert log["judge"]["status"] == "error"
    assert log["judge"]["fallback_participant_id"] == "participant-1-cloudflare"
    assert "Candidate survives judge failure" in log["final_answer"]


def test_all_participants_failed_is_terminal_and_never_runs_synthesis():
    cloudflare = ScriptedProvider("cloudflare", responses=[fail("cloudflare")])
    groq = ScriptedProvider("groq", responses=[fail("groq")])

    log = _orchestrator(cloudflare=cloudflare, groq=groq).debate(
        "Do the task",
        agents=["cloudflare", "groq"],
        rounds=3,
    )

    assert log["status"] == "error"
    assert log["selected_participants"] == 2
    assert log["successful_participants"] == 0
    assert log["judge"] == {}
    assert log["deliberation"] == []


def test_judge_winner_marker_is_validated_against_real_participant_ids():
    cloudflare = ScriptedProvider(
        "cloudflare",
        responses=[
            ok("cloudflare"),
            ok(
                "cloudflare",
                "WINNER: fabricated-participant\nFINAL:\nA valid synthesis body that should not create a fabricated verdict.",
            ),
        ],
    )
    log = _orchestrator(cloudflare=cloudflare).debate(
        "Do the task", agents=["cloudflare"], rounds=1
    )

    assert log["status"] == "success"
    assert log["system_verdict"] is None
    assert "valid synthesis body" in log["final_answer"]


def test_selected_provider_duplicates_do_not_create_fake_extra_minds():
    cloudflare = ScriptedProvider("cloudflare")
    log = _orchestrator(cloudflare=cloudflare).debate(
        "Do the task",
        agents=["cloudflare", "cloudflare", "cloudflare"],
        rounds=1,
    )

    assert log["requested_agents"] == ["cloudflare", "cloudflare", "cloudflare"]
    assert log["agents"] == ["cloudflare"]
    assert log["selected_participants"] == 1
    assert len(log["participants"]) == 1


def test_application_persists_structured_deliberation_data_without_flattening():
    captured = {}

    class FakeDB:
        pass

    def persist_chat(_db, _session_id, _memories, chat_data):
        captured.update(chat_data)
        return True

    structured = {
        "status": "success",
        "final_answer": "final",
        "participants": [
            {
                "participant_id": "participant-1-groq",
                "requested_provider": "groq",
                "actual_provider": "groq-model",
                "status": "success",
                "text": "answer",
            }
        ],
        "deliberation": [],
        "judge": {"status": "success", "actual_provider": "groq-model"},
        "system_verdict": "participant-1-groq",
        "total_tokens": 12,
        "total_cost": 0.0,
    }

    class FakeOrchestrator:
        def __init__(self, **_kwargs):
            pass

        def debate(self, **_kwargs):
            return structured

    app = MultiMindApplication(
        agents={"groq": ScriptedProvider("groq")},
        runtime_memories={},
        db=FakeDB(),
        debate_factory=FakeOrchestrator,
        persist_chat=persist_chat,
    )
    result = app.execute_chat(
        ChatRequest(
            original_prompt="prompt",
            context_mode="standalone",
            session_id="session-1",
            session_mode="thinking",
            active_agents=["groq"],
        )
    )

    assert result.status == "success"
    assert result.debate_data["participants"][0]["participant_id"] == "participant-1-groq"
    assert '"participant_id": "participant-1-groq"' in captured["debate_data"]
    assert '"system_verdict": "participant-1-groq"' in captured["debate_data"]
