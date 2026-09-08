"""Pure Reflex-facing projection helpers for persisted/runtime deliberation truth.

This module never decides participants, winners, fallback, or application behavior.
It only normalizes application-owned debate_data for presentation.
"""

from __future__ import annotations

import json


def _as_debate_dict(raw):
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
        except (TypeError, ValueError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def participant_snapshots(raw):
    debate = _as_debate_dict(raw)
    snapshots = []
    for item in debate.get("participants", []) if isinstance(debate.get("participants"), list) else []:
        if not isinstance(item, dict):
            continue
        snapshots.append(
            {
                "participant_id": str(item.get("participant_id", "")),
                "requested_provider": str(item.get("requested_provider", "")),
                "actual_provider": str(item.get("actual_provider") or ""),
                "model": str(item.get("model") or ""),
                "role": str(item.get("role", "")),
                "status": str(item.get("status", "unknown")),
                "text": str(item.get("text", "")),
                "failure_category": str(item.get("failure_category") or ""),
            }
        )
    return snapshots


def critique_snapshots(raw):
    debate = _as_debate_dict(raw)
    snapshots = []
    for item in debate.get("deliberation", []) if isinstance(debate.get("deliberation"), list) else []:
        if not isinstance(item, dict):
            continue
        snapshots.append(
            {
                "round": str(item.get("round", "")),
                "participant_id": str(item.get("participant_id", "")),
                "requested_provider": str(item.get("requested_provider", "")),
                "actual_provider": str(item.get("actual_provider") or ""),
                "status": str(item.get("status", "unknown")),
                "text": str(item.get("text", "")),
            }
        )
    return snapshots


def run_summary(raw):
    debate = _as_debate_dict(raw)
    judge = debate.get("judge", {}) if isinstance(debate.get("judge"), dict) else {}
    participants = participant_snapshots(debate)
    selected = debate.get("selected_participants", len(participants))
    successful = debate.get(
        "successful_participants",
        sum(1 for item in participants if item["status"] == "success"),
    )
    try:
        selected = int(selected)
    except (TypeError, ValueError):
        selected = len(participants)
    try:
        successful = int(successful)
    except (TypeError, ValueError):
        successful = sum(1 for item in participants if item["status"] == "success")

    return {
        "selected": selected,
        "successful": successful,
        "system_verdict": str(debate.get("system_verdict") or ""),
        "judge_provider": str(judge.get("actual_provider") or ""),
        "judge_status": str(judge.get("status") or ""),
    }


def history_snapshots(rows):
    snapshots = []
    for row in rows or []:
        debate = _as_debate_dict(row.get("debate_data")) if isinstance(row, dict) else {}
        summary = run_summary(debate)
        participants = participant_snapshots(debate)
        participant_summary = "; ".join(
            f"{item['participant_id']}={item['status']}:{item['actual_provider'] or item['requested_provider']}"
            for item in participants
        )
        snapshots.append(
            {
                "id": str(row.get("id", "")),
                "prompt": str(row.get("prompt", "")),
                "final_answer": str(row.get("final_answer", "")),
                "participant_summary": participant_summary,
                "system_verdict": summary["system_verdict"],
                "judge_provider": summary["judge_provider"],
            }
        )
    return snapshots
