"""Presentation and pre-send observability contracts for deliberation semantics."""

import json

from multimind_reflex.deliberation_projection import (
    critique_snapshots,
    history_snapshots,
    participant_snapshots,
    revision_snapshots,
    run_summary,
)
from ui.presentation.builder import build_presentation_snapshot
from utils.token_counter import TokenCounter


def _debate_data():
    return {
        "deliberation_depth": "deep_debate",
        "participants": [
            {
                "participant_id": "participant-1-gemini",
                "requested_provider": "gemini",
                "actual_provider": "gemini-model",
                "model": "gemini-model",
                "role": "Researcher",
                "status": "success",
                "text": "Gemini contribution",
            },
            {
                "participant_id": "participant-2-groq",
                "requested_provider": "groq",
                "actual_provider": "groq",
                "model": "groq-model",
                "role": "Analyst",
                "status": "error",
                "text": "",
                "failure_category": "timeout",
            },
        ],
        "deliberation": [
            {
                "round": 2,
                "participant_id": "participant-1-gemini",
                "requested_provider": "gemini",
                "actual_provider": "gemini-model",
                "status": "success",
                "text": "A concise critique",
            }
        ],
        "revisions": [
            {
                "round": 3,
                "participant_id": "participant-1-gemini",
                "requested_provider": "gemini",
                "actual_provider": "gemini-model",
                "model": "gemini-model",
                "status": "success",
                "text": "A traceable revised answer",
            }
        ],
        "responses": [
            {
                "round": 2,
                "participant_id": "participant-1-gemini",
                "agent": "Researcher (gemini-model)",
                "actual_provider": "gemini-model",
                "phase": "critique",
                "status": "success",
                "text": "A concise critique",
            }
        ],
        "judge": {"status": "success", "actual_provider": "cloudflare-model"},
        "system_verdict": "participant-1-gemini",
        "user_verdict": "participant-1-gemini",
        "selected_participants": 2,
        "successful_participants": 1,
        "gate_score": 9,
    }


def test_streamlit_presentation_snapshot_preserves_participant_and_judge_provenance():
    debate = _debate_data()
    snapshot = build_presentation_snapshot(
        {"id": "s1", "name": "Session", "mode": "research", "created_at": "now"},
        [
            {
                "id": "c1",
                "prompt": "prompt",
                "mode": "standalone",
                "final_answer": "final",
                "tokens_used": 10,
                "cost": 0,
                "debate_data": json.dumps(debate),
            }
        ],
    )

    detail = snapshot.chats[0].debate_detail
    assert detail is not None
    assert detail.selected_participants == 2
    assert detail.successful_participants == 1
    assert detail.system_verdict == "participant-1-gemini"
    assert detail.judge_provider == "cloudflare-model"
    assert [item.participant_id for item in detail.participants] == [
        "participant-1-gemini",
        "participant-2-groq",
    ]
    assert detail.participants[1].status == "error"
    assert detail.participants[1].failure_category == "timeout"
    assert detail.responses[0].phase == "critique"
    assert detail.responses[0].actual_provider == "gemini-model"


def test_reflex_projection_uses_persisted_truth_without_reassigning_identity():
    debate = _debate_data()
    participants = participant_snapshots(debate)
    critiques = critique_snapshots(debate)
    revisions = revision_snapshots(debate)
    summary = run_summary(debate)

    assert participants[0]["requested_provider"] == "gemini"
    assert participants[0]["actual_provider"] == "gemini-model"
    assert participants[1]["requested_provider"] == "groq"
    assert participants[1]["status"] == "error"
    assert critiques[0]["participant_id"] == "participant-1-gemini"
    assert revisions[0]["participant_id"] == "participant-1-gemini"
    assert revisions[0]["round"] == "3"
    assert summary == {
        "selected": 2,
        "successful": 1,
        "deliberation_depth": "deep_debate",
        "system_verdict": "participant-1-gemini",
        "user_verdict": "participant-1-gemini",
        "judge_provider": "cloudflare-model",
        "judge_status": "success",
        "revision_count": 1,
    }


def test_reflex_history_rehydrates_deliberation_provenance_from_json():
    rows = [
        {
            "id": "c1",
            "prompt": "prompt",
            "final_answer": "final",
            "debate_data": json.dumps(_debate_data()),
        }
    ]
    projected = history_snapshots(rows)[0]

    assert "participant-1-gemini=success:gemini-model" in projected["participant_summary"]
    assert "participant-2-groq=error:groq" in projected["participant_summary"]
    assert projected["system_verdict"] == "participant-1-gemini"
    assert projected["user_verdict"] == "participant-1-gemini"
    assert projected["deliberation_depth"] == "deep_debate"
    assert projected["revision_count"] == "1"
    assert projected["judge_provider"] == "cloudflare-model"


def test_malformed_persisted_debate_data_fails_boring_in_reflex_projection():
    projected = history_snapshots(
        [{"id": "c1", "prompt": "p", "final_answer": "f", "debate_data": "{broken"}]
    )[0]
    assert projected["participant_summary"] == ""
    assert projected["system_verdict"] == ""
    assert projected["user_verdict"] == ""
    assert projected["judge_provider"] == ""


def test_token_estimate_tracks_real_participant_round_call_graph():
    one = TokenCounter.estimate_total("meaningful prompt", rounds=1, participants=1, compressor_on=False)
    six = TokenCounter.estimate_total("meaningful prompt", rounds=1, participants=6, compressor_on=False)
    deeper = TokenCounter.estimate_total("meaningful prompt", rounds=3, participants=6, compressor_on=False)

    assert one["provider_calls_estimate"] == 2  # 1 candidate + 1 judge
    assert six["provider_calls_estimate"] == 7  # 6 candidates + 1 judge
    assert deeper["provider_calls_estimate"] == 25  # 6 candidates + 12 critiques + 6 revisions + judge
    assert deeper["revision_calls_estimate"] == 6
    assert one["total_estimate"] < six["total_estimate"] < deeper["total_estimate"]