"""Behavioral proof for explicit deep-debate revision semantics."""

from core.debate import DebateOrchestrator
from providers.base import BaseProvider


class ScriptedProvider(BaseProvider):
    def __init__(self, name, responses=None):
        super().__init__(name)
        self.model_name = f"{name}-model"
        self.responses = list(responses or [])
        self.calls = []

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096, **kwargs):
        self.calls.append({
            "prompt": prompt,
            "system_prompt": system_prompt,
            "mode": mode,
            "max_tokens": max_tokens,
        })
        if self.responses:
            item = self.responses.pop(0)
            if callable(item):
                return item(prompt)
            return dict(item)
        return ok(self.name)


def ok(name, text=None):
    return {
        "status": "success",
        "text": text or f"Useful answer from {name} with enough detail for verification.",
        "agent": f"{name}-model",
        "tokens": 10,
        "cost": 0.0,
    }


def fail(name, category="timeout"):
    return {
        "status": "error",
        "text": "Provider unavailable",
        "agent": f"{name}-model",
        "tokens": 0,
        "cost": 0.0,
        "failure_category": category,
    }


def orchestrator(cloudflare=None, groq=None):
    return DebateOrchestrator(
        gemini_agent=None,
        cloudflare_agent=cloudflare,
        groq_agent=groq,
    )


def test_round_three_adds_revision_without_removing_existing_critique_rounds():
    round1 = orchestrator(
        cloudflare=ScriptedProvider("cloudflare"),
        groq=ScriptedProvider("groq"),
    ).debate("Reason carefully", agents=["cloudflare", "groq"], mode="thinking", rounds=1)
    round2 = orchestrator(
        cloudflare=ScriptedProvider("cloudflare"),
        groq=ScriptedProvider("groq"),
    ).debate("Reason carefully", agents=["cloudflare", "groq"], mode="thinking", rounds=2)
    round3 = orchestrator(
        cloudflare=ScriptedProvider("cloudflare"),
        groq=ScriptedProvider("groq"),
    ).debate("Reason carefully", agents=["cloudflare", "groq"], mode="thinking", rounds=3)

    assert round1["deliberation_depth"] == "panel"
    assert round1["revisions"] == []
    assert round2["deliberation_depth"] == "deliberate"
    assert len(round2["deliberation"]) == 2
    assert round2["revisions"] == []
    assert round3["deliberation_depth"] == "deep_debate"
    assert len(round3["deliberation"]) == 4
    assert {item["round"] for item in round3["deliberation"]} == {2, 3}
    assert len(round3["revisions"]) == 2
    assert {item["participant_id"] for item in round3["revisions"]} == {
        "participant-1-cloudflare",
        "participant-2-groq",
    }


def test_revision_sees_original_answer_full_panel_and_critiques():
    cloudflare = ScriptedProvider("cloudflare")
    groq = ScriptedProvider("groq")
    log = orchestrator(cloudflare=cloudflare, groq=groq).debate(
        "Compare two designs",
        agents=["cloudflare", "groq"],
        mode="research",
        rounds=3,
    )

    # candidate, critique R2, critique R3, revision, then possible judge for
    # Cloudflare because it is first eligible judge provider.
    revision_prompt = cloudflare.calls[3]["prompt"]
    assert "YOUR ORIGINAL CONTRIBUTION" in revision_prompt
    assert "FULL PANEL" in revision_prompt
    assert "CRITIQUES FROM THE DELIBERATION" in revision_prompt
    assert "participant-1-cloudflare" in revision_prompt
    assert "participant-2-groq" in revision_prompt
    assert log["revisions"][0]["requested_provider"] == "cloudflare"


def test_revision_failure_is_explicit_and_never_impersonated():
    cloudflare = ScriptedProvider(
        "cloudflare",
        responses=[
            ok("cloudflare", "Original Cloudflare candidate with enough detail."),
            ok("cloudflare", "Cloudflare critique two."),
            ok("cloudflare", "Cloudflare critique three."),
            fail("cloudflare", "revision_timeout"),
            ok("cloudflare", "WINNER: participant-2-groq\nFINAL:\nSynthesis survives one failed revision with enough detail."),
        ],
    )
    groq = ScriptedProvider(
        "groq",
        responses=[
            ok("groq", "Original Groq candidate with enough detail."),
            ok("groq", "Groq critique two."),
            ok("groq", "Groq critique three."),
            ok("groq", "Revised Groq answer with corrected reasoning."),
        ],
    )

    log = orchestrator(cloudflare=cloudflare, groq=groq).debate(
        "Handle revision failure",
        agents=["cloudflare", "groq"],
        mode="thinking",
        rounds=3,
    )

    failed = next(item for item in log["revisions"] if item["participant_id"] == "participant-1-cloudflare")
    healthy = next(item for item in log["revisions"] if item["participant_id"] == "participant-2-groq")
    assert failed["status"] == "error"
    assert failed["requested_provider"] == "cloudflare"
    assert "cloudflare" in failed["actual_provider"].lower()
    assert failed["failure_category"] == "revision_timeout"
    assert healthy["status"] == "success"
    assert healthy["requested_provider"] == "groq"
    assert log["status"] == "success"


def test_judge_receives_post_deliberation_revisions_and_preserves_participant_ids():
    cloudflare = ScriptedProvider(
        "cloudflare",
        responses=[
            ok("cloudflare", "Original C answer."),
            ok("cloudflare", "C critique R2."),
            ok("cloudflare", "C critique R3."),
            ok("cloudflare", "C revised position preserves dissent."),
            ok("cloudflare", "WINNER: participant-1-cloudflare\nFINAL:\nFinal answer uses revised evidence and preserves dissent."),
        ],
    )
    groq = ScriptedProvider(
        "groq",
        responses=[
            ok("groq", "Original G answer."),
            ok("groq", "G critique R2."),
            ok("groq", "G critique R3."),
            ok("groq", "G revised position after challenge."),
        ],
    )

    log = orchestrator(cloudflare=cloudflare, groq=groq).debate(
        "Synthesize revisions",
        agents=["cloudflare", "groq"],
        mode="thinking",
        rounds=3,
    )

    judge_prompt = cloudflare.calls[4]["prompt"]
    assert "REVISIONS:" in judge_prompt
    assert "C revised position preserves dissent." in judge_prompt
    assert "G revised position after challenge." in judge_prompt
    assert "participant-1-cloudflare" in judge_prompt
    assert "participant-2-groq" in judge_prompt
    assert log["system_verdict"] == "participant-1-cloudflare"
    assert "Final answer uses revised evidence" in log["final_answer"]


def test_judge_failure_prefers_successful_revision_over_stale_candidate():
    cloudflare = ScriptedProvider(
        "cloudflare",
        responses=[
            ok("cloudflare", "Stale original candidate with enough detail."),
            ok("cloudflare", "Critique R2."),
            ok("cloudflare", "Critique R3."),
            ok("cloudflare", "Corrected revised candidate with enough detail for release."),
            fail("cloudflare", "judge_timeout"),
        ],
    )
    log = orchestrator(cloudflare=cloudflare).debate(
        "Prefer revision fallback",
        agents=["cloudflare"],
        mode="coding",
        rounds=3,
    )

    assert log["judge"]["status"] == "error"
    assert log["judge"]["fallback_source"] == "revision"
    assert "Corrected revised candidate" in log["final_answer"]
    assert "Stale original candidate" not in log["final_answer"]
