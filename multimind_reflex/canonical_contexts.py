"""Renderer-neutral semantic fixtures for canonical EQ4 cross-context proving.

These fixtures mirror the seven accepted MultiMind presentation archetypes but
contain no provider, persistence, application, or Design-DNA truth. They provide
four stable semantic roles so the same canonical DNA host machinery can be
exercised against different product contexts without duplicating business logic.
"""
from __future__ import annotations

from dataclasses import dataclass

from ui.presentation.resolver import CANONICAL_ARCHETYPE_IDS


@dataclass(frozen=True)
class CanonicalContextFixture:
    archetype_id: str
    display_name: str
    mental_model: str
    primary_object: str
    work_title: str
    work_body: str
    action_title: str
    action_body: str
    state_title: str
    state_body: str
    auxiliary_title: str
    auxiliary_body: str


_CONTEXTS = {
    "chat_first": CanonicalContextFixture(
        "chat_first",
        "Chat-first",
        "Ongoing conversation with MultiMind",
        "Conversation",
        "Conversation stream",
        "Prompt, history, and synthesized answer remain the primary reading object.",
        "New conversation",
        "The primary conversational action stays discoverable without replacing history.",
        "Conversation state",
        "Generation, debate, success, warning, and failure state remain explicit.",
        "Conversation context",
        "Memory, mode, tokens, and supporting metadata stay subordinate to the reading stream.",
    ),
    "command_center": CanonicalContextFixture(
        "command_center",
        "Command Center",
        "Observe and control MultiMind operation",
        "System / Operational State",
        "Operational matrix",
        "Agent execution state, comparative outputs, and gate condition are the operational focus.",
        "Dispatch action",
        "The primary execution control remains explicit beside operational state.",
        "System telemetry",
        "Running, waiting, success, warning, failure, and gate state remain immediately legible.",
        "Mission context",
        "Prompt, resource, cost, and session metadata support the operational matrix without replacing it.",
    ),
    "ai_workspace": CanonicalContextFixture(
        "ai_workspace",
        "AI Workspace",
        "Work with multiple active objects",
        "Workspace Objects",
        "Active workspace object",
        "The current prompt, artifact, or result is anchored as the primary work object.",
        "Run workspace task",
        "The primary task action stays attached to the active object rather than global decoration.",
        "Workspace state",
        "Object readiness, generation, warning, and failure state remain visible across the workspace.",
        "Orbiting resources",
        "Files, memory, agent detail, and related objects remain available as supporting context.",
    ),
    "ai_research_lab": CanonicalContextFixture(
        "ai_research_lab",
        "AI Research Lab",
        "Investigate evidence and build conclusions",
        "Evidence / Analysis / Synthesis",
        "Evidence workspace",
        "Claims, findings, source relationships, and synthesis remain distinguishable without fabricated evidence.",
        "Synthesize findings",
        "The synthesis action remains primary while source/evidence traversal stays inspectable.",
        "Research state",
        "Evidence availability, uncertainty, progress, warning, and failure remain explicit.",
        "Source context",
        "Agent findings, source metadata, confidence, and supporting notes remain subordinate to the thesis.",
    ),
    "agent_canvas": CanonicalContextFixture(
        "agent_canvas",
        "Agent Canvas",
        "Work with agent relationships and execution flow",
        "Agent Topology & Workflow",
        "Execution topology",
        "Trigger, agent nodes, gate, and synthesized output remain a truthful workflow sequence.",
        "Dispatch workflow",
        "The primary workflow action remains discoverable without inventing topology or agents.",
        "Agent state",
        "Per-agent running, waiting, success, warning, and failure state remain attached to real nodes.",
        "Topology context",
        "Roles, round detail, tools, and workflow metadata support the graph without replacing it.",
    ),
    "terminal_hacker": CanonicalContextFixture(
        "terminal_hacker",
        "Terminal / Hacker AI",
        "Follow instruction, execution, and output progression",
        "Instruction / Execution Stream",
        "Execution stream",
        "Instruction, execution progression, and result remain ordered as one inspectable stream.",
        "Execute instruction",
        "The primary command action remains explicit and does not masquerade as generated output.",
        "Process state",
        "Queued, running, completed, warning, and failure state remain distinct from output text.",
        "Session metadata",
        "Mode, resources, tokens, and diagnostic context remain available without polluting the execution stream.",
    ),
    "minimal_saas": CanonicalContextFixture(
        "minimal_saas",
        "Minimal SaaS",
        "Complete the primary task with restrained disclosure",
        "Primary Task / Direct Action",
        "Primary task",
        "The current user task and result stay dominant while optional detail remains progressively disclosed.",
        "Submit primary task",
        "One obvious primary action remains discoverable without competing controls.",
        "Product state",
        "Loading, success, warning, and failure remain explicit with minimal visual overhead.",
        "Progressive detail",
        "Memory, agent, cost, and technical detail remain available only as supporting disclosure.",
    ),
}


if tuple(_CONTEXTS) != tuple(CANONICAL_ARCHETYPE_IDS):
    raise RuntimeError("canonical EQ4 context fixture membership/order drift")


def list_context_ids() -> tuple[str, ...]:
    return tuple(CANONICAL_ARCHETYPE_IDS)


def get_context_fixture(archetype_id: str) -> CanonicalContextFixture:
    try:
        return _CONTEXTS[str(archetype_id)]
    except KeyError as exc:
        raise ValueError(f"unsupported canonical archetype: {archetype_id}") from exc


__all__ = ["CanonicalContextFixture", "get_context_fixture", "list_context_ids"]
