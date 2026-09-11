import json

from core.ai_product_completion import AIProductApplication, DeepDebateOrchestrator
from database.verdict_persistence import VerdictDatabaseManager
from providers.base import BaseProvider
from utils.token_counter import TokenCounter


class ScriptedProvider(BaseProvider):
    def __init__(self, name, responses=None):
        super().__init__(name)
        self.model_name = f"{name}-model"
        self.responses = list(responses or [])
        self.calls = []

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096, **kwargs):
        self.calls.append({"prompt": prompt, "system_prompt": system_prompt, "mode": mode})
        if self.responses:
            item = self.responses.pop(0)
            if callable(item):
                return item(prompt)
            return dict(item)
        return {
            "status": "success",
            "text": f"answer-{self.name}-{len(self.calls)} with enough detail for release checks",
            "agent": self.model_name,
            "tokens": 10,
            "cost": 0.0,
        }


def ok(name, text):
    return {
        "status": "success",
        "text": text,
        "agent": f"{name}-model",
        "tokens": 10,
        "cost": 0.0,
    }


def fail(name):
    return {
        "status": "error",
        "text": "failed",
        "agent": f"{name}-model",
        "tokens": 0,
        "cost": 0.0,
        "failure_category": "timeout",
    }


def orchestrator(gemini=None, groq=None):
    return DeepDebateOrchestrator(
        gemini_agent=gemini,
        groq_agent=groq,
        deepseek_agent=None,
        cloudflare_agent=None,
        openrouter_agent=None,
        huggingface_agent=None,
    )


def test_rounds_one_and_two_preserve_closed_behavior_without_revisions():
    for rounds, critique_count in ((1, 0), (2, 2)):
        log = orchestrator(ScriptedProvider("gemini"), ScriptedProvider("groq")).debate(
            "task", agents=["gemini", "groq"], mode="thinking", rounds=rounds
        )
        assert log["status"] == "success"
        assert len(log["deliberation"]) == critique_count
        assert log["revisions"] == []
        assert log["deliberation_depth"] == ("panel" if rounds == 1 else "deliberate")


def test_round_three_adds_same_participant_revision_after_critique():
    gemini = ScriptedProvider("gemini")
    groq = ScriptedProvider("groq")
    log = orchestrator(gemini, groq).debate(
        "deep task", agents=["gemini", "groq"], mode="thinking", rounds=3
    )

    assert log["status"] == "success"
    assert log["deliberation_depth"] == "deep_debate"
    assert len(log["participants"]) == 2
    assert len(log["deliberation"]) == 4
    assert len(log["revisions"]) == 2
    assert {item["participant_id"] for item in log["revisions"]} == {
        "participant-1-gemini", "participant-2-groq"
    }
    assert {item["requested_provider"] for item in log["revisions"]} == {"gemini", "groq"}
    assert all(item["status"] == "success" for item in log["revisions"])
    assert log["revision_count"] == 2

    revision_prompts = [
        call["prompt"] for call in gemini.calls + groq.calls
        if "YOUR PARTICIPANT ID:" in call["prompt"]
    ]
    assert len(revision_prompts) == 2
    assert all("CURRENT PANEL POSITIONS:" in prompt for prompt in revision_prompts)
    assert all("CRITIQUES SO FAR:" in prompt for prompt in revision_prompts)


def test_failed_revision_does_not_destroy_last_successful_position():
    # Candidate, critique R2, critique R3, revision R3 fails, judge succeeds.
    gemini = ScriptedProvider(
        "gemini",
        responses=[
            ok("gemini", "stable initial answer with enough detail"),
            ok("gemini", "critique two"),
            ok("gemini", "critique three"),
            fail("gemini"),
            ok(
                "gemini",
                "WINNER: participant-1-gemini\nFINAL:\nstable initial answer remains usable after failed revision",
            ),
        ],
    )
    log = orchestrator(gemini, None).debate(
        "deep task", agents=["gemini"], mode="thinking", rounds=3
    )
    assert log["status"] == "success"
    assert log["revisions"][0]["status"] == "error"
    assert log["revision_count"] == 0
    assert "stable initial answer remains usable" in log["final_answer"]


def test_judge_receives_traceable_revisions_and_latest_positions():
    captured = {}

    def judge(prompt):
        captured["prompt"] = prompt
        return ok(
            "gemini",
            "WINNER: participant-1-gemini\nFINAL:\ncombined deep synthesis with enough detail",
        )

    gemini = ScriptedProvider(
        "gemini",
        responses=[
            ok("gemini", "initial-g"),
            ok("gemini", "critique-g-r2"),
            ok("gemini", "critique-g-r3"),
            ok("gemini", "revised-g"),
            judge,
        ],
    )
    log = orchestrator(gemini, None).debate(
        "deep task", agents=["gemini"], mode="thinking", rounds=3
    )
    assert log["status"] == "success"
    assert "INITIAL PARTICIPANT CONTRIBUTIONS:" in captured["prompt"]
    assert "CURRENT PARTICIPANT POSITIONS AFTER REVISION:" in captured["prompt"]
    assert "TRACEABLE REVISIONS:" in captured["prompt"]
    assert "initial-g" in captured["prompt"]
    assert "revised-g" in captured["prompt"]


def test_user_verdict_persists_separately_from_system_verdict(tmp_path):
    db = VerdictDatabaseManager(str(tmp_path / "user.db"))
    db.create_session("s1", "session")
    debate = {
        "participants": [
            {"participant_id": "participant-1-gemini", "status": "success"},
            {"participant_id": "participant-2-groq", "status": "success"},
        ],
        "system_verdict": "participant-1-gemini",
    }
    db.save_chat("s1", {
        "id": "c1", "prompt": "q", "final_answer": "a",
        "debate_data": json.dumps(debate),
    })
    app = AIProductApplication(db=db)

    assert app.record_user_verdict("s1", "c1", "participant-2-groq") is True
    stored = json.loads(db.get_chat("s1", "c1")["debate_data"])
    assert stored["system_verdict"] == "participant-1-gemini"
    assert stored["user_verdict"] == "participant-2-groq"


def test_user_verdict_rejects_failed_unknown_or_cross_session_participant(tmp_path):
    db = VerdictDatabaseManager(str(tmp_path / "user.db"))
    db.create_session("s1", "one")
    db.create_session("s2", "two")
    db.save_chat("s1", {
        "id": "c1", "prompt": "q", "final_answer": "a",
        "debate_data": json.dumps({
            "participants": [
                {"participant_id": "good", "status": "success"},
                {"participant_id": "failed", "status": "error"},
            ],
            "system_verdict": "good",
        }),
    })
    app = AIProductApplication(db=db)

    assert app.record_user_verdict("s1", "c1", "failed") is False
    assert app.record_user_verdict("s1", "c1", "missing") is False
    assert app.record_user_verdict("s2", "c1", "good") is False
    stored = json.loads(db.get_chat("s1", "c1")["debate_data"])
    assert "user_verdict" not in stored


def test_token_estimator_counts_deep_revision_calls():
    r1 = TokenCounter.estimate_total("hello world", rounds=1, participants=2, compressor_on=False)
    r2 = TokenCounter.estimate_total("hello world", rounds=2, participants=2, compressor_on=False)
    r3 = TokenCounter.estimate_total("hello world", rounds=3, participants=2, compressor_on=False)
    r5 = TokenCounter.estimate_total("hello world", rounds=5, participants=2, compressor_on=False)

    assert r1["provider_calls_estimate"] == 3  # 2 candidates + judge
    assert r2["provider_calls_estimate"] == 5  # +2 critiques
    assert r3["provider_calls_estimate"] == 9  # +2 critiques +2 revisions
    assert r5["provider_calls_estimate"] == 17
    assert r3["revision_calls_estimate"] == 2
