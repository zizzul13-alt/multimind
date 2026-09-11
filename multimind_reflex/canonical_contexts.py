"""Renderer-neutral semantic contexts for canonical Design-DNA proving.

These seven fixtures mirror the already-accepted MultiMind presentation
archetypes. They contain only stable presentation semantics: what each surface
makes primary and which four semantic slots the proving renderer must preserve.
They do not own application/session/provider/persistence truth and do not encode
any Design-DNA reference identity.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchetypeContext:
    id: str
    display_name: str
    primary_object: str
    context_title: str
    context_body: str
    work_title: str
    work_body: str
    action_title: str
    action_body: str
    state_title: str
    state_body: str
    auxiliary_title: str
    auxiliary_body: str


ARCHETYPE_CONTEXTS: tuple[ArchetypeContext, ...] = (
    ArchetypeContext(
        id="chat_first",
        display_name="Chat-first",
        primary_object="Conversation",
        context_title="Conversation context",
        context_body="Continuous conversation remains the primary reading object.",
        work_title="Conversation feed",
        work_body="Prompt, history, and synthesized answer remain a continuous readable thread.",
        action_title="Message composer",
        action_body="The next message action remains immediately discoverable without replacing conversation truth.",
        state_title="Conversation state",
        state_body="Mode, loading, success, warning, and failure remain explicit around the conversation.",
        auxiliary_title="Memory and session context",
        auxiliary_body="Session and memory metadata remain subordinate to the conversation itself.",
    ),
    ArchetypeContext(
        id="command_center",
        display_name="Command Center",
        primary_object="System / Operational State",
        context_title="Operational context",
        context_body="System state and comparative execution status own primary attention.",
        work_title="Agent comparison matrix",
        work_body="Real participant outputs and execution status are organized for operational comparison.",
        action_title="Control action",
        action_body="The primary operational action stays prominent without inventing execution authority.",
        state_title="System status board",
        state_body="Provider, gate, loading, warning, and failure state remain explicit and scannable.",
        auxiliary_title="Run metrics",
        auxiliary_body="Tokens, cost, session, and memory metrics support the operational picture.",
    ),
    ArchetypeContext(
        id="ai_workspace",
        display_name="AI Workspace",
        primary_object="Workspace Objects",
        context_title="Workspace context",
        context_body="Multiple active work objects are organized around one anchored working object.",
        work_title="Anchored workspace object",
        work_body="The active prompt/result artifact remains anchored while related objects stay available.",
        action_title="Workspace action",
        action_body="Create or continue work remains discoverable without changing persisted object truth.",
        state_title="Object state",
        state_body="Active, pending, complete, warning, and failure states remain attached to real workspace objects.",
        auxiliary_title="Orbiting context",
        auxiliary_body="Related details and supporting objects orbit the anchored work object rather than replacing it.",
    ),
    ArchetypeContext(
        id="ai_research_lab",
        display_name="AI Research Lab",
        primary_object="Evidence / Analysis / Synthesis",
        context_title="Research context",
        context_body="Evidence, findings, and synthesis form an explicit investigation hierarchy.",
        work_title="Synthesized thesis",
        work_body="The current conclusion is prominent while remaining traceable to actual underlying findings.",
        action_title="Research action",
        action_body="Continue analysis or investigation remains visible without fabricating evidence or citations.",
        state_title="Evidence state",
        state_body="Evidence availability, confidence, warnings, and failures remain explicit.",
        auxiliary_title="Underlying findings",
        auxiliary_body="Agent findings and analysis remain available as subordinate evidence traversal.",
    ),
    ArchetypeContext(
        id="agent_canvas",
        display_name="Agent Canvas",
        primary_object="Agent Topology & Workflow",
        context_title="Workflow topology",
        context_body="Actual agent roles and execution sequence are the primary navigable object.",
        work_title="Execution path",
        work_body="Trigger, real agent steps, gate, and synthesized output preserve actual workflow order.",
        action_title="Workflow action",
        action_body="The next valid workflow action remains discoverable without inventing hidden agents or steps.",
        state_title="Node state",
        state_body="Running, complete, warning, error, and gate state stay attached to real topology nodes.",
        auxiliary_title="Role and edge context",
        auxiliary_body="Agent role and relationship details support the topology without replacing it.",
    ),
    ArchetypeContext(
        id="terminal_hacker",
        display_name="Terminal / Hacker AI",
        primary_object="Instruction / Execution Stream",
        context_title="Execution stream",
        context_body="Instruction to execution to output remains a legible temporal sequence.",
        work_title="Output stream",
        work_body="Actual execution output remains primary and ordered rather than decorative terminal fiction.",
        action_title="Instruction action",
        action_body="The next instruction remains explicit while preserving execution boundaries.",
        state_title="Execution status",
        state_body="Running, success, warning, failure, and gate state remain visible in sequence.",
        auxiliary_title="Execution log context",
        auxiliary_body="Supporting logs and metadata remain available without overwhelming the main stream.",
    ),
    ArchetypeContext(
        id="minimal_saas",
        display_name="Minimal SaaS",
        primary_object="Primary Task / Direct Action",
        context_title="Task context",
        context_body="One restrained primary task dominates while detail is progressively disclosed.",
        work_title="Primary task",
        work_body="The current task/result remains focused with unnecessary context kept subordinate.",
        action_title="Primary call to action",
        action_body="The direct next action remains unmistakable and semantically primary.",
        state_title="Task status",
        state_body="Essential loading, success, warning, and failure state remains visible without dashboard noise.",
        auxiliary_title="Progressive details",
        auxiliary_body="Secondary metadata is available on demand without competing with the primary task.",
    ),
)

CANONICAL_ARCHETYPE_IDS: tuple[str, ...] = tuple(item.id for item in ARCHETYPE_CONTEXTS)
_CONTEXT_BY_ID = {item.id: item for item in ARCHETYPE_CONTEXTS}


def get_archetype_context(archetype_id: str) -> ArchetypeContext:
    """Resolve one accepted archetype fixture, falling back boringly to chat-first."""
    return _CONTEXT_BY_ID.get(str(archetype_id or ""), _CONTEXT_BY_ID["chat_first"])


__all__ = [
    "ARCHETYPE_CONTEXTS",
    "CANONICAL_ARCHETYPE_IDS",
    "ArchetypeContext",
    "get_archetype_context",
]
