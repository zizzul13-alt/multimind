"""
MultiMind AI - Archetype Registry & Composition Resolver (S7.5)

Provides canonical registry of recognized MultiMind UI archetypes, ID-to-renderer mapping,
safe fallback resolution, and unified rendering entry point.
"""
from typing import Dict, List, Callable, NamedTuple, Tuple, Optional
import logging
from ui.presentation.models import PresentationSnapshot

logger = logging.getLogger(__name__)


class ArchetypeDefinition(NamedTuple):
    """Canonical metadata definition for a MultiMind UI archetype."""
    id: str
    display_name: str
    description: str
    primary_object: str
    renderer: Callable[[PresentationSnapshot], None]


# Delay importing renderers until module load to prevent circular imports if any
def _get_archetype_registry() -> Dict[str, ArchetypeDefinition]:
    from ui.presentation.projections import (
        render_chat_first,
        render_command_center,
        render_ai_workspace,
        render_ai_research_lab,
        render_agent_canvas,
        render_terminal_hacker,
        render_minimal_saas,
    )

    return {
        "chat_first": ArchetypeDefinition(
            id="chat_first",
            display_name="💬 Chat-first",
            description="Continuous conversation is the primary interaction object.",
            primary_object="Conversation",
            renderer=render_chat_first,
        ),
        "command_center": ArchetypeDefinition(
            id="command_center",
            display_name="🎛️ Command Center",
            description="System metrics, agent state, and debate performance are primary.",
            primary_object="System / Operational State",
            renderer=render_command_center,
        ),
        "ai_workspace": ArchetypeDefinition(
            id="ai_workspace",
            display_name="💼 AI Workspace",
            description="Multi-object organization & structured workspace views are primary.",
            primary_object="Workspace Objects",
            renderer=render_ai_workspace,
        ),
        "ai_research_lab": ArchetypeDefinition(
            id="ai_research_lab",
            display_name="🔬 AI Research Lab",
            description="Evidence, agent findings, analysis, and synthesis are primary.",
            primary_object="Evidence / Analysis / Synthesis",
            renderer=render_ai_research_lab,
        ),
        "agent_canvas": ArchetypeDefinition(
            id="agent_canvas",
            display_name="🎨 Agent Canvas",
            description="Agent relationships, roles, and execution workflow step topology are primary.",
            primary_object="Agent Topology & Workflow",
            renderer=render_agent_canvas,
        ),
        "terminal_hacker": ArchetypeDefinition(
            id="terminal_hacker",
            display_name="🖥️ Terminal / Hacker AI",
            description="Instruction -> execution progression -> output stream sequence is primary.",
            primary_object="Instruction / Execution Stream",
            renderer=render_terminal_hacker,
        ),
        "minimal_saas": ArchetypeDefinition(
            id="minimal_saas",
            display_name="⚡ Minimal SaaS",
            description="Restrained primary task focus with progressive disclosure of details.",
            primary_object="Primary Task / Direct Action",
            renderer=render_minimal_saas,
        ),
    }


# Canonical list of exact 7 archetypes in standard display order
CANONICAL_ARCHETYPE_IDS: Tuple[str, ...] = (
    "chat_first",
    "command_center",
    "ai_workspace",
    "ai_research_lab",
    "agent_canvas",
    "terminal_hacker",
    "minimal_saas",
)

FALLBACK_ARCHETYPE_ID = "chat_first"


def list_archetypes() -> List[Tuple[str, str]]:
    """
    Returns list of (archetype_id, display_name) tuples for UI selectbox bindings.
    Guarantees stable canonical order.
    """
    registry = _get_archetype_registry()
    return [(arch_id, registry[arch_id].display_name) for arch_id in CANONICAL_ARCHETYPE_IDS if arch_id in registry]


def get_archetype_definition(archetype_id: Optional[str]) -> ArchetypeDefinition:
    """
    Retrieves ArchetypeDefinition for given ID. Safely falls back to Chat-first if invalid or unknown.
    """
    registry = _get_archetype_registry()
    if archetype_id and isinstance(archetype_id, str) and archetype_id in registry:
        return registry[archetype_id]

    if archetype_id is not None and archetype_id != FALLBACK_ARCHETYPE_ID:
        logger.warning("Unknown archetype ID '%s'. Falling back to '%s'.", archetype_id, FALLBACK_ARCHETYPE_ID)

    return registry[FALLBACK_ARCHETYPE_ID]


def resolve_archetype(archetype_id: Optional[str]) -> Callable[[PresentationSnapshot], None]:
    """
    Resolves archetype ID to its render function.
    Unknown/invalid values safely fall back to render_chat_first.
    """
    definition = get_archetype_definition(archetype_id)
    return definition.renderer


def render_archetype(archetype_id: Optional[str], snapshot: PresentationSnapshot) -> None:
    """
    Single canonical entry point to resolve and render an archetype projection for a given snapshot.
    """
    renderer = resolve_archetype(archetype_id)
    renderer(snapshot)
