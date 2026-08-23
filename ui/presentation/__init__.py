"""
MultiMind AI - Presentation Layer Package
"""
from ui.presentation.models import (
    PresentationSnapshot,
    SessionMetadataSnapshot,
    MemorySummarySnapshot,
    ChatMessageSnapshot,
    DebateDetailSnapshot,
    DebateResponseSnapshot,
)
from ui.presentation.builder import build_presentation_snapshot
from ui.presentation.resolver import (
    list_archetypes,
    resolve_archetype,
    get_archetype_definition,
    render_archetype,
    CANONICAL_ARCHETYPE_IDS,
    FALLBACK_ARCHETYPE_ID,
)
from ui.presentation.brand import render_brand_identity

__all__ = [
    "PresentationSnapshot",
    "SessionMetadataSnapshot",
    "MemorySummarySnapshot",
    "ChatMessageSnapshot",
    "DebateDetailSnapshot",
    "DebateResponseSnapshot",
    "build_presentation_snapshot",
    "list_archetypes",
    "resolve_archetype",
    "get_archetype_definition",
    "render_archetype",
    "CANONICAL_ARCHETYPE_IDS",
    "FALLBACK_ARCHETYPE_ID",
    "render_brand_identity",
]
