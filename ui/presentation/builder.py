"""
MultiMind AI - Semantic Presentation Snapshot Builder

Adapts existing application/session/database state into read-only PresentationSnapshot instances.
Deterministic, free of side effects, non-mutating, safe on missing or corrupt inputs.
"""
import json
from typing import Dict, List, Any, Optional
from ui.presentation.models import (
    PresentationSnapshot,
    SessionMetadataSnapshot,
    MemorySummarySnapshot,
    ChatMessageSnapshot,
    DebateDetailSnapshot,
    DebateResponseSnapshot,
    DebateParticipantSnapshot,
)


def _safe_int(val: Any, default: int = 0) -> int:
    """Defensively parses integer values."""
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Defensively parses float values."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _user_verdict_id(debate_dict: Dict[str, Any]) -> str:
    verdict = debate_dict.get("user_verdict")
    if isinstance(verdict, dict):
        return str(verdict.get("participant_id") or "")
    return str(verdict or "")


def _build_session_metadata(session_dict: Dict[str, Any]) -> SessionMetadataSnapshot:
    """Safely builds SessionMetadataSnapshot from current session dict."""
    session_id = str(session_dict.get("id", ""))
    name = str(session_dict.get("name", "Untitled Session"))
    mode = str(session_dict.get("mode", "coding"))
    created_at = str(session_dict.get("created_at", ""))

    return SessionMetadataSnapshot(
        id=session_id,
        name=name,
        mode=mode,
        created_at=created_at,
    )


def _build_memory_summary(memory_obj: Any) -> Optional[MemorySummarySnapshot]:
    """Safely extracts memory metrics from session memory object if available."""
    if not memory_obj or not hasattr(memory_obj, "get_stats"):
        return None

    try:
        stats = memory_obj.get_stats()
        if not isinstance(stats, dict):
            return None
        return MemorySummarySnapshot(
            context_tokens=_safe_int(stats.get("context_tokens"), 0),
            short_term_chats=_safe_int(stats.get("short_term_chats"), 0),
            free_percent=_safe_int(stats.get("free_percent"), 0),
        )
    except Exception:
        return None


def _build_debate_detail(debate_raw: Any) -> Optional[DebateDetailSnapshot]:
    """Safely parse persisted debate_data without inventing application truth."""
    if not debate_raw:
        return None

    debate_dict = None
    if isinstance(debate_raw, dict):
        debate_dict = debate_raw
    elif isinstance(debate_raw, str):
        try:
            parsed = json.loads(debate_raw)
            if isinstance(parsed, dict):
                debate_dict = parsed
        except Exception:
            return DebateDetailSnapshot(gate_score=None, has_error=True)

    if not debate_dict:
        return DebateDetailSnapshot(gate_score=None, has_error=True)

    raw_gate_score = debate_dict.get("gate_score")
    gate_score = _safe_int(raw_gate_score, default=None) if raw_gate_score is not None else None

    responses = []
    raw_responses = debate_dict.get("responses", [])
    if isinstance(raw_responses, list):
        for idx, resp in enumerate(raw_responses, 1):
            if not isinstance(resp, dict):
                continue
            round_index = _safe_int(resp.get("round"), idx)
            responses.append(
                DebateResponseSnapshot(
                    round_index=round_index,
                    agent=str(resp.get("agent", "Unknown")),
                    text=str(resp.get("text", "")),
                    status=str(resp.get("status", "unknown")),
                    phase=str(resp.get("phase", "candidate")),
                    participant_id=str(resp.get("participant_id", "")),
                    actual_provider=str(resp.get("actual_provider", "")),
                )
            )

    participants = []
    raw_participants = debate_dict.get("participants", [])
    if isinstance(raw_participants, list):
        for participant in raw_participants:
            if not isinstance(participant, dict):
                continue
            participants.append(
                DebateParticipantSnapshot(
                    participant_id=str(participant.get("participant_id", "")),
                    requested_provider=str(participant.get("requested_provider", "")),
                    actual_provider=str(participant.get("actual_provider") or ""),
                    model=str(participant.get("model") or ""),
                    role=str(participant.get("role", "")),
                    status=str(participant.get("status", "unknown")),
                    text=str(participant.get("text", "")),
                    failure_category=str(participant.get("failure_category") or ""),
                )
            )

    judge = debate_dict.get("judge", {})
    judge_provider = ""
    if isinstance(judge, dict):
        judge_provider = str(judge.get("actual_provider") or "")

    raw_revisions = debate_dict.get("revisions", [])
    revision_count = 0
    if isinstance(raw_revisions, list):
        revision_count = sum(
            1 for item in raw_revisions
            if isinstance(item, dict) and item.get("status") == "success"
        )

    return DebateDetailSnapshot(
        gate_score=gate_score,
        responses=tuple(responses),
        participants=tuple(participants),
        system_verdict=str(debate_dict.get("system_verdict") or ""),
        user_verdict=_user_verdict_id(debate_dict),
        deliberation_depth=str(debate_dict.get("deliberation_depth") or ""),
        revision_count=revision_count,
        judge_provider=judge_provider,
        selected_participants=_safe_int(debate_dict.get("selected_participants"), len(participants)),
        successful_participants=_safe_int(
            debate_dict.get("successful_participants"),
            sum(1 for item in participants if item.status == "success"),
        ),
        has_error=False,
    )


def _build_chat_message(chat_dict: Dict[str, Any]) -> ChatMessageSnapshot:
    """Safely builds ChatMessageSnapshot from DB chat dictionary."""
    chat_id = str(chat_dict.get("id", ""))
    prompt = str(chat_dict.get("prompt", ""))
    mode = str(chat_dict.get("mode", "continue"))
    final_answer = str(chat_dict.get("final_answer", "No response"))
    tokens_used = _safe_int(chat_dict.get("tokens_used"), 0)
    cost = _safe_float(chat_dict.get("cost"), 0.0)

    raw_debate = chat_dict.get("debate_data")
    has_debate_data = bool(raw_debate)
    debate_detail = _build_debate_detail(raw_debate)

    return ChatMessageSnapshot(
        id=chat_id,
        prompt=prompt,
        mode=mode,
        final_answer=final_answer,
        tokens_used=tokens_used,
        cost=cost,
        has_debate_data=has_debate_data,
        debate_detail=debate_detail,
    )


def build_presentation_snapshot(
    session_dict: Dict[str, Any],
    chats_list: List[Dict[str, Any]],
    memory_obj: Optional[Any] = None,
) -> PresentationSnapshot:
    """Build a non-mutating, read-only presentation projection."""
    session_snapshot = _build_session_metadata(session_dict)
    memory_snapshot = _build_memory_summary(memory_obj)

    chat_snapshots = []
    if isinstance(chats_list, list):
        for chat in chats_list:
            if isinstance(chat, dict):
                chat_snapshots.append(_build_chat_message(chat))

    return PresentationSnapshot(
        session=session_snapshot,
        chats=tuple(chat_snapshots),
        memory=memory_snapshot,
    )
