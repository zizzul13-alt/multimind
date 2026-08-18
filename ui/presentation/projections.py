"""
MultiMind AI - Archetype Projections (S7.4 Archetype Projection Proof)

Pure UI renderers projecting a single read-only PresentationSnapshot into
distinct archetype views without reading database, session persistence, or core state.

Archetypes:
1. Chat-first: Conversation remains the dominant work object.
2. Command Center: System and agent operational state are visually primary.
"""
import streamlit as st
from ui.presentation.models import PresentationSnapshot
from ui.foundation import render_status_badge, card_container
from core.release_gate import ReleaseGate


def render_chat_first(snapshot: PresentationSnapshot) -> None:
    """
    Renders Chat-first Archetype Projection.

    Mental model: "I am having an ongoing conversation with MultiMind."
    Primary object: Conversation.
    Invariants:
    - User prompt and final answer remain visually central.
    - Message composer trigger (New Chat) is immediately discoverable.
    - System/debate details remain subordinate to conversation context.
    """
    # Session Header Title & Metadata
    st.markdown(
        f"<div class='mm-flex-between'>"
        f"  <div class='mm-typo-heading'>💬 {snapshot.session.name}</div>"
        f"  <div>"
        f"    <span class='mm-badge mm-badge-info'>Mode: {snapshot.session.mode}</span> "
        f"    <span class='mm-typo-caption mm-text-muted'>Created: {snapshot.session.created_at[:10]}</span>"
        f"  </div>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Subordinate Memory Metrics Bar
    if snapshot.memory:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Context Tokens", snapshot.memory.context_tokens)
        with col2:
            st.metric("Short-term Chats", snapshot.memory.short_term_chats)
        with col3:
            st.metric("Free Space", f"{snapshot.memory.free_percent}%")

    st.divider()

    # Conversation Feed (Dominant Primary Work Object)
    if not snapshot.chats:
        st.info("No messages in this session yet. Start a conversation below.")
    else:
        for chat in snapshot.chats:
            with st.chat_message("user"):
                mode_badge = "🧵" if chat.mode == 'continue' else "📌"
                st.caption(f"{mode_badge} {chat.mode.upper()}")
                st.write(chat.prompt)
            with st.chat_message("assistant"):
                st.markdown(chat.final_answer)
                if chat.has_debate_data:
                    with st.expander("🔍 Debate Details"):
                        if chat.debate_detail and chat.debate_detail.has_error:
                            st.caption("Error loading debate details")
                        elif chat.debate_detail:
                            if chat.debate_detail.gate_score is not None:
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.caption(f"🎯 Gate Score: {chat.debate_detail.gate_score}/10")
                                with col2:
                                    st.caption(f"{ReleaseGate.get_badge(chat.debate_detail.gate_score)}")
                                st.divider()
                            if chat.debate_detail.responses:
                                for r in chat.debate_detail.responses:
                                    badge_variant = "success" if r.status == "success" else ("danger" if r.status == "error" else "warning")
                                    render_status_badge(f"Round {r.round_index} - {r.agent} ({r.status})", variant=badge_variant)
                                    if r.text:
                                        st.markdown(r.text)
                                    else:
                                        st.caption(f"(Status: {r.status})")
                            else:
                                st.caption("No debate data available")
                        else:
                            st.caption("Error loading debate details")
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"🔤 {chat.tokens_used} tokens")
                with col2:
                    st.caption(f"💵 ${chat.cost:.6f}")

    st.divider()
    if st.button("➕ New Chat", type="primary", key="chat_first_new_chat_btn", use_container_width=True):
        st.session_state.new_chat = True
        st.rerun()


def render_command_center(snapshot: PresentationSnapshot) -> None:
    """
    Renders Command Center Archetype Projection.

    Mental model: "I am observing and controlling MultiMind's operation."
    Primary object: System / Agent operational state.
    Invariants:
    - Agent and debate operational information is visually primary and comparable.
    - Gate score and success/error status are immediately visible.
    - Conversation content remains accessible as secondary context.
    - Uses exact same PresentationSnapshot instance without backend queries.
    """
    # Command Center Header
    st.markdown(
        f"<div class='mm-flex-between'>"
        f"  <div class='mm-typo-heading'>🎛️ Command Center — {snapshot.session.name}</div>"
        f"  <div>"
        f"    <span class='mm-badge mm-badge-info'>Mode: {snapshot.session.mode}</span> "
        f"    <span class='mm-typo-caption mm-text-muted'>ID: {snapshot.session.id[:8]}</span>"
        f"  </div>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # Operational System & Memory Status Section
    st.markdown("#### ⚡ System & Memory Status")
    if snapshot.memory:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Context Tokens", snapshot.memory.context_tokens)
        with col2:
            st.metric("Short-term Chats", snapshot.memory.short_term_chats)
        with col3:
            st.metric("Free Space", f"{snapshot.memory.free_percent}%")
        with col4:
            st.metric("Total Chats", len(snapshot.chats))
    else:
        st.info("Memory status snapshot unavailable.")

    st.divider()

    # Primary Operational Focus: Agent Responses & Debate Performance
    st.markdown("#### 🤖 Agent Operational State & Debate Responses")

    if not snapshot.chats:
        st.info("No execution/debate data logged in this session yet.")
    else:
        for idx, chat in enumerate(snapshot.chats, 1):
            with st.expander(f"Debate Entry #{idx} (ID: {chat.id[:8]}) — {chat.tokens_used} tokens, ${chat.cost:.6f}", expanded=(idx == len(snapshot.chats))):
                st.caption(f"**Prompt:** {chat.prompt}")

                if chat.has_debate_data and chat.debate_detail:
                    d_detail = chat.debate_detail
                    if d_detail.has_error:
                        st.error("⚠️ Debate details contain errors or unparseable data.")
                    else:
                        # Prominent Gate Score Summary
                        if d_detail.gate_score is not None:
                            badge = ReleaseGate.get_badge(d_detail.gate_score)
                            st.markdown(f"**Gate Score:** `{d_detail.gate_score}/10` ({badge})")

                        # Agent Responses Comparison Grid
                        if d_detail.responses:
                            st.markdown("##### Agent Output Comparison")
                            agent_cols = st.columns(min(len(d_detail.responses), 4))
                            for col_i, resp in enumerate(d_detail.responses):
                                with agent_cols[col_i % len(agent_cols)]:
                                    variant = "success" if resp.status == "success" else ("danger" if resp.status == "error" else "warning")
                                    badge_variant = "success" if resp.status == "success" else ("danger" if resp.status == "error" else "warning")
                                    render_status_badge(f"Round {resp.round_index} - {resp.agent} ({resp.status.upper()})", variant=badge_variant)
                                    if resp.text:
                                        st.markdown(resp.text)
                                    else:
                                        st.caption("(No output)")
                        else:
                            st.caption("No individual agent responses logged.")
                else:
                    st.caption("Standalone chat response (No debate orchestration data).")

                st.markdown("##### Final Answer Context")
                st.markdown(chat.final_answer)

    st.divider()
    if st.button("➕ New Chat", type="primary", key="cmd_center_new_chat_btn", use_container_width=True):
        st.session_state.new_chat = True
        st.rerun()
