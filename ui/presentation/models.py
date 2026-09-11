"""
MultiMind AI - Read-only Semantic Presentation Models

Provides pure presentation snapshots representing the state consumed by UI renderers.
Independent of theme styling, database persistence, and orchestration logic.
"""
from dataclasses import dataclass
from typing import Tuple, Optional


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
    """Read-only presentation snapshot of one recorded deliberation response."""
    round_index: int
    agent: str
    text: str
    status: str
    phase: str = "candidate"
    participant_id: str = ""
    actual_provider: str = ""


@dataclass(frozen=True)
class DebateParticipantSnapshot:
    """Read-only participant attempt preserving selected and actual provenance."""
    participant_id: str
    requested_provider: str
    actual_provider: str
    model: str
    role: str
    status: str
    text: str
    failure_category: str = ""


@dataclass(frozen=True)
class DebateDetailSnapshot:
    """Read-only presentation snapshot of deliberation truth."""
    gate_score: Optional[int]
    responses: Tuple[DebateResponseSnapshot, ...] = ()
    participants: Tuple[DebateParticipantSnapshot, ...] = ()
    system_verdict: str = ""
    user_verdict: str = ""
    deliberation_depth: str = ""
    revision_count: int = 0
    judge_provider: str = ""
    selected_participants: int = 0
    successful_participants: int = 0
    has_error: bool = False


@dataclass(frozen=True)
class ChatMessageSnapshot:
    """Read-only presentation snapshot of a chat prompt & response entry."""
    id: str
    prompt: str
    mode: str  # 'continue' or 'standalone'
    final_answer: str
    tokens_used: int
    cost: float
    has_debate_data: bool = False
    debate_detail: Optional[DebateDetailSnapshot] = None


@dataclass(frozen=True)
class PresentationSnapshot:
    """Root read-only semantic presentation snapshot for current active session path."""
    session: SessionMetadataSnapshot
    chats: Tuple[ChatMessageSnapshot, ...] = ()
    memory: Optional[MemorySummarySnapshot] = None


@dataclass(frozen=True)
class InteractionContext:
    """Read-only presentation context for interaction shell rendering."""
    active_archetype: str
    new_chat_active: bool
    session: Optional[SessionMetadataSnapshot] = None
    prompt_text: str = ""
    selected_template: Optional[str] = None
    chat_mode: str = "continue"
    uploaded_files_count: int = 0
    uploaded_file_names: Tuple[str, ...] = ()
    is_processing: bool = False
    estimated_tokens: int = 0
    estimated_cost: float = 0.0