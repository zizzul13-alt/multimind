"""
MultiMind AI - Semantic Presentation Snapshot Builder

Adapts existing application/session/database state into read-only PresentationSnapshot instances.
Deterministic, free of side effects, non-mutating, safe on missing or corrupt inputs.
"""
import json
from typing import Dict, List, Any, Optional
from core.release_gate import ReleaseGate
from ui.presentation.models import (
    PresentationSnapshot,
    SessionMetadataSnapshot,
    MemorySummarySnapshot,
    ChatMessageSnapshot,
    DebateDetailSnapshot,
    DebateResponseSnapshot,
)


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
            context_tokens=int(stats.get("context_tokens", 0)),
            short_term_chats=int(stats.get("short_term_chats", 0)),
            free_percent=int(stats.get("free_percent", 0)),
        )
    except Exception:
        return None


def _build_debate_detail(debate_raw: Any) -> Optional[DebateDetailSnapshot]:
    """Safely parses debate_data (dict or JSON string) into structured DebateDetailSnapshot."""
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
            return None

    if not debate_dict:
        return None

    gate_score = debate_dict.get("gate_score")
    gate_badge = None
    if gate_score is not None:
        try:
            gate_score = int(gate_score)
            gate_badge = ReleaseGate.get_badge(gate_score)
        except Exception:
            gate_score = None

    responses = []
    raw_responses = debate_dict.get("responses", [])
    if isinstance(raw_responses, list):
        for idx, resp in enumerate(raw_responses, 1):
            if isinstance(resp, dict):
                agent = str(resp.get("agent", "Unknown"))
                text = str(resp.get("text", ""))
                status = str(resp.get("status", "unknown"))

                badge_variant = "success" if status == "success" else ("danger" if status == "error" else "warning")
                responses.append(
                    DebateResponseSnapshot(
                        round_index=idx,
                        agent=agent,
                        text=text,
                        status=status,
                        badge_variant=badge_variant,
                    )
                )

    return DebateDetailSnapshot(
        gate_score=gate_score,
        gate_badge=gate_badge,
        responses=responses,
    )


def _build_chat_message(chat_dict: Dict[str, Any]) -> ChatMessageSnapshot:
    """Safely builds ChatMessageSnapshot from DB chat dictionary."""
    chat_id = str(chat_dict.get("id", ""))
    prompt = str(chat_dict.get("prompt", ""))
    mode = str(chat_dict.get("mode", "continue"))
    mode_badge = "🧵" if mode == "continue" else "📌"
    final_answer = str(chat_dict.get("final_answer", "No response"))
    tokens_used = int(chat_dict.get("tokens_used", 0))

    cost_val = chat_dict.get("cost", 0.0)
    try:
        cost = float(cost_val)
    except (ValueError, TypeError):
        cost = 0.0

    debate_detail = _build_debate_detail(chat_dict.get("debate_data"))

    return ChatMessageSnapshot(
        id=chat_id,
        prompt=prompt,
        mode=mode,
        mode_badge=mode_badge,
        final_answer=final_answer,
        tokens_used=tokens_used,
        cost=cost,
        debate_detail=debate_detail,
    )


def build_presentation_snapshot(
    session_dict: Dict[str, Any],
    chats_list: List[Dict[str, Any]],
    memory_obj: Optional[Any] = None,
) -> PresentationSnapshot:
    """
    Builds a read-only PresentationSnapshot from existing application state.

    Guarantees:
    - Non-mutating (input objects remain unchanged)
    - Safe execution against malformed/missing fields
    - Fully read-only, structured presentation output
    """
    session_snapshot = _build_session_metadata(session_dict)
    memory_snapshot = _build_memory_summary(memory_obj)

    chat_snapshots = []
    if isinstance(chats_list, list):
        for chat in chats_list:
            if isinstance(chat, dict):
                chat_snapshots.append(_build_chat_message(chat))

    return PresentationSnapshot(
        session=session_snapshot,
        chats=chat_snapshots,
        memory=memory_snapshot,
    )
