"""
MultiMind AI - Read-only Semantic Presentation Models

Provides pure presentation snapshots representing the state consumed by UI renderers.
Independent of theme styling, database persistence, and orchestration logic.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


@dataclass(frozen=True)
class SessionMetadataSnapshot:
    """Read-only presentation snapshot of session header details."""
    id: str
    name: str
    mode: str
    created_at: str


@dataclass(frozen=True)
class MemorySummarySnapshot:
    """Read-only presentation snapshot of session memory metrics."""
    context_tokens: int
    short_term_chats: int
    free_percent: int


@dataclass(frozen=True)
class DebateResponseSnapshot:
    """Read-only presentation snapshot of an individual agent response in debate."""
    round_index: int
    agent: str
    text: str
    status: str
    badge_variant: str  # "success", "danger", "warning", "info"


@dataclass(frozen=True)
class DebateDetailSnapshot:
    """Read-only presentation snapshot of debate metrics and agent responses."""
    gate_score: Optional[int]
    gate_badge: Optional[str]
    responses: List[DebateResponseSnapshot] = field(default_factory=list)


@dataclass(frozen=True)
class ChatMessageSnapshot:
    """Read-only presentation snapshot of a chat prompt & response entry."""
    id: str
    prompt: str
    mode: str  # 'continue' or 'standalone'
    mode_badge: str  # "🧵" or "📌"
    final_answer: str
    tokens_used: int
    cost: float
    debate_detail: Optional[DebateDetailSnapshot] = None


@dataclass(frozen=True)
class PresentationSnapshot:
    """Root read-only semantic presentation snapshot for current active session path."""
    session: SessionMetadataSnapshot
    chats: List[ChatMessageSnapshot] = field(default_factory=list)
    memory: Optional[MemorySummarySnapshot] = None
