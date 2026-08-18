"""
MultiMind AI - Canonical Archetype Projections (S7.5)

Pure UI renderers projecting a single read-only PresentationSnapshot into
distinct archetype views without reading database, session persistence, or core state.

Recognized Archetypes (Exactly 7):
1. Chat-first (`render_chat_first`): Continuous conversation is primary.
2. Command Center (`render_command_center`): Operational state and metrics are primary.
3. AI Workspace (`render_ai_workspace`): Multi-object organization & workspace view.
4. AI Research Lab (`render_ai_research_lab`): Evidence, analysis, & synthesis hierarchy.
5. Agent Canvas (`render_agent_canvas`): Agent roles, topology, & execution workflow.
6. Terminal / Hacker AI (`render_terminal_hacker`): Instruction -> execution -> output sequence.
7. Minimal SaaS (`render_minimal_saas`): Restrained primary task focus with progressive disclosure.
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


def render_ai_workspace(snapshot: PresentationSnapshot) -> None:
    """
    Renders AI Workspace Archetype Projection.

    Mental model: "I work with multiple objects."
    Primary object: Workspace objects.
    Invariants:
    - Multiple work objects (chats/session/debate items) are simultaneously organized and navigable.
    - Preserves exact underlying semantics (does not fabricate unrepresented task state).
    """
    st.markdown(
        f"<div class='mm-flex-between'>"
        f"  <div class='mm-typo-heading'>💼 Workspace Overview — {snapshot.session.name}</div>"
        f"  <div>"
        f"    <span class='mm-badge mm-badge-info'>Mode: {snapshot.session.mode}</span> "
        f"    <span class='mm-typo-caption mm-text-muted'>Created: {snapshot.session.created_at[:10]}</span>"
        f"  </div>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Workspace Summary Dashboard
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Workspace Objects", len(snapshot.chats))
    with col2:
        st.metric("Context Tokens", snapshot.memory.context_tokens if snapshot.memory else 0)
    with col3:
        st.metric("Memory Available", f"{snapshot.memory.free_percent}%" if snapshot.memory else "N/A")
    with col4:
        total_cost = sum(c.cost for c in snapshot.chats)
        st.metric("Total Cost", f"${total_cost:.4f}")

    st.divider()

    # Organized Workspace Objects View
    st.markdown("#### 📂 Workspace Items")
    if not snapshot.chats:
        st.info("Workspace is currently empty. Create a new item below.")
    else:
        # Display items in a structured workspace grid / card layout
        for idx, chat in enumerate(snapshot.chats, 1):
            with st.container():
                st.markdown(f"##### Item #{idx} · Mode: `{chat.mode.upper()}` · Tokens: `{chat.tokens_used}`")
                col_prompt, col_answer = st.columns(2)
                with col_prompt:
                    st.markdown("**Prompt Context:**")
                    st.write(chat.prompt)
                with col_answer:
                    st.markdown("**Generated Output:**")
                    st.markdown(chat.final_answer)

                if chat.has_debate_data and chat.debate_detail:
                    with st.expander(f"⚙️ Workspace Details (Item #{idx})"):
                        d_detail = chat.debate_detail
                        if d_detail.has_error:
                            st.caption("Error loading item details")
                        else:
                            if d_detail.gate_score is not None:
                                badge = ReleaseGate.get_badge(d_detail.gate_score)
                                st.caption(f"🎯 Quality Gate Score: {d_detail.gate_score}/10 ({badge})")
                            for resp in d_detail.responses:
                                badge_variant = "success" if resp.status == "success" else ("danger" if resp.status == "error" else "warning")
                                render_status_badge(f"Agent: {resp.agent} ({resp.status})", variant=badge_variant)
                                if resp.text:
                                    st.markdown(resp.text)
                st.divider()

    if st.button("➕ New Chat", type="primary", key="ai_workspace_new_chat_btn", use_container_width=True):
        st.session_state.new_chat = True
        st.rerun()


def render_ai_research_lab(snapshot: PresentationSnapshot) -> None:
    """
    Renders AI Research Lab Archetype Projection.

    Mental model: "I investigate evidence and build conclusions."
    Primary object: Evidence / Analysis / Synthesis hierarchy.
    Invariants:
    - Synthesized conclusion (final answer) is prominent.
    - Agent debate outputs are structured as investigative findings/evidence items.
    - Does not fabricate non-existent source citations.
    """
    st.markdown(
        f"<div class='mm-flex-between'>"
        f"  <div class='mm-typo-heading'>🔬 AI Research Lab — {snapshot.session.name}</div>"
        f"  <div>"
        f"    <span class='mm-badge mm-badge-info'>Mode: {snapshot.session.mode}</span> "
        f"    <span class='mm-typo-caption mm-text-muted'>ID: {snapshot.session.id[:8]}</span>"
        f"  </div>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.divider()

    if snapshot.memory:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Research Context Tokens", snapshot.memory.context_tokens)
        with col2:
            st.metric("Analyzed Queries", snapshot.memory.short_term_chats)
        with col3:
            st.metric("Memory Capacity", f"{snapshot.memory.free_percent}%")

    st.divider()

    st.markdown("#### 🧪 Research Findings & Synthesis")

    if not snapshot.chats:
        st.info("No research items or findings in this session yet.")
    else:
        for idx, chat in enumerate(snapshot.chats, 1):
            st.markdown(f"### Research Query #{idx}")
            st.caption(f"**Research Prompt:** {chat.prompt}")

            # Prominent Synthesis Section
            st.markdown("##### 🔍 Synthesized Conclusion")
            st.markdown(chat.final_answer)

            # Evidence & Agent Findings Breakdown
            if chat.has_debate_data and chat.debate_detail:
                d_detail = chat.debate_detail
                if d_detail.has_error:
                    st.error("⚠️ Evidence breakdown contains corrupted data.")
                else:
                    st.markdown("##### 📄 Agent Findings & Evidence Analysis")
                    if d_detail.gate_score is not None:
                        badge = ReleaseGate.get_badge(d_detail.gate_score)
                        st.caption(f"Gate Score Confidence: **{d_detail.gate_score}/10** ({badge})")

                    if d_detail.responses:
                        for resp in d_detail.responses:
                            badge_variant = "success" if resp.status == "success" else ("danger" if resp.status == "error" else "warning")
                            render_status_badge(f"Finding from {resp.agent} (Round {resp.round_index})", variant=badge_variant)
                            if resp.text:
                                st.markdown(resp.text)
                            else:
                                st.caption("(No findings recorded)")
                    else:
                        st.caption("No individual agent evidence records present.")
            else:
                st.caption("Standalone analysis result (No multi-agent debate evidence recorded).")

            st.caption(f"Analysis Tokens: {chat.tokens_used} | Cost: ${chat.cost:.6f}")
            st.divider()

    if st.button("➕ New Chat", type="primary", key="ai_research_lab_new_chat_btn", use_container_width=True):
        st.session_state.new_chat = True
        st.rerun()


def render_agent_canvas(snapshot: PresentationSnapshot) -> None:
    """
    Renders Agent Canvas Archetype Projection.

    Mental model: "I work with entities and relationships."
    Primary object: Agent relationships, roles, and execution workflow step topology.
    Invariants:
    - Agent topology and execution flow steps are primary.
    - Expresses available debate responses and roles as step sequences and entity nodes.
    """
    st.markdown(
        f"<div class='mm-flex-between'>"
        f"  <div class='mm-typo-heading'>🎨 Agent Canvas — {snapshot.session.name}</div>"
        f"  <div>"
        f"    <span class='mm-badge mm-badge-info'>Mode: {snapshot.session.mode}</span> "
        f"    <span class='mm-typo-caption mm-text-muted'>Session ID: {snapshot.session.id[:8]}</span>"
        f"  </div>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # Active Workflow Topology Summary
    st.markdown("#### 🧬 Workflow Sequence & Agent Roles Topology")

    if not snapshot.chats:
        st.info("No active agent canvas entries in this session.")
    else:
        for idx, chat in enumerate(snapshot.chats, 1):
            st.markdown(f"#### Workflow Node #{idx}")
            st.caption(f"**Trigger Input Prompt:** {chat.prompt}")

            # Execution Step Topology Representation
            if chat.has_debate_data and chat.debate_detail and not chat.debate_detail.has_error:
                d_detail = chat.debate_detail
                st.markdown("##### 🔄 Agent Execution Step Flow")

                if d_detail.responses:
                    cols = st.columns(min(len(d_detail.responses), 4))
                    for c_idx, resp in enumerate(d_detail.responses):
                        with cols[c_idx % len(cols)]:
                            badge_variant = "success" if resp.status == "success" else ("danger" if resp.status == "error" else "warning")
                            st.markdown(f"**Step {resp.round_index}: Node `{resp.agent}`**")
                            render_status_badge(resp.status.upper(), variant=badge_variant)
                            if resp.text:
                                st.markdown(resp.text)

                if d_detail.gate_score is not None:
                    badge = ReleaseGate.get_badge(d_detail.gate_score)
                    st.markdown(f"**🎯 Release Gate Node:** Score `{d_detail.gate_score}/10` ({badge})")
            elif chat.debate_detail and chat.debate_detail.has_error:
                st.error("⚠️ Topology step failed due to corrupted debate data.")
            else:
                st.caption("Direct execution path (Single model, no debate topology).")

            st.markdown("##### 🏁 Synthesized Output Node")
            st.markdown(chat.final_answer)

            st.caption(f"Node Metrics: {chat.tokens_used} tokens | ${chat.cost:.6f}")
            st.divider()

    if st.button("➕ New Chat", type="primary", key="agent_canvas_new_chat_btn", use_container_width=True):
        st.session_state.new_chat = True
        st.rerun()


def render_terminal_hacker(snapshot: PresentationSnapshot) -> None:
    """
    Renders Terminal / Hacker AI Archetype Projection.

    Mental model: "I issue instructions and observe execution."
    Primary object: Instruction -> execution progression -> output stream sequence.
    Invariants:
    - Sequential operational log stream model.
    - Not a visual costume: emphasizes instruction prompt -> execution state -> final output stream sequence.
    """
    st.markdown(
        f"<div class='mm-flex-between'>"
        f"  <div class='mm-typo-heading'>🖥️ Terminal / Operational Stream — {snapshot.session.name}</div>"
        f"  <div>"
        f"    <span class='mm-badge mm-badge-info'>SYS_MODE: {snapshot.session.mode.upper()}</span> "
        f"    <span class='mm-typo-caption mm-text-muted'>UUID: {snapshot.session.id[:8]}</span>"
        f"  </div>"
        f"</div>",
        unsafe_allow_html=True
    )

    if snapshot.memory:
        st.text(f"[SYS_METRICS] CTX_TOKENS={snapshot.memory.context_tokens} | SHORT_TERM_CHATS={snapshot.memory.short_term_chats} | FREE_MEM={snapshot.memory.free_percent}%")

    st.divider()

    st.markdown("#### 📜 Operational Execution Stream")

    if not snapshot.chats:
        st.info("[STREAM_EMPTY] No instruction records in buffer.")
    else:
        for idx, chat in enumerate(snapshot.chats, 1):
            st.text(f"--- [EXECUTION_SEQUENCE #{idx}] ID: {chat.id[:8]} MODE: {chat.mode.upper()} ---")

            # Step 1: Instruction
            st.markdown(f"**$ USER_INSTRUCTION:** `{chat.prompt}`")

            # Step 2: Execution Progression
            if chat.has_debate_data and chat.debate_detail:
                d_detail = chat.debate_detail
                if d_detail.has_error:
                    st.text("[EXEC_ERR] Debate details contain parse errors.")
                else:
                    if d_detail.gate_score is not None:
                        badge = ReleaseGate.get_badge(d_detail.gate_score)
                        st.text(f"[GATE_VERDICT] SCORE={d_detail.gate_score}/10 | VERDICT={badge}")
                    if d_detail.responses:
                        for resp in d_detail.responses:
                            st.text(f"[AGENT_LOG] ROUND={resp.round_index} AGENT={resp.agent} STATUS={resp.status.upper()}")
                            if resp.text:
                                st.markdown(resp.text)
            else:
                st.text("[EXEC_DIRECT] Standalone execution (No debate agent orchestration).")

            # Step 3: Output / State Result
            st.markdown("**[SYSTEM_OUTPUT]:**")
            st.markdown(chat.final_answer)

            st.text(f"[STREAM_END] TOKENS={chat.tokens_used} COST=${chat.cost:.6f}\n")
            st.divider()

    if st.button("➕ New Chat", type="primary", key="terminal_hacker_new_chat_btn", use_container_width=True):
        st.session_state.new_chat = True
        st.rerun()


def render_minimal_saas(snapshot: PresentationSnapshot) -> None:
    """
    Renders Minimal SaaS Archetype Projection.

    Mental model: "I complete the current task without unnecessary complexity."
    Primary object: Primary task / direct action.
    Invariants:
    - Restrained focus, minimal visual noise, clear primary action.
    - Uses progressive disclosure (expanders) for secondary/historical details.
    """
    st.markdown(
        f"<div class='mm-flex-between'>"
        f"  <div class='mm-typo-heading'>⚡ {snapshot.session.name}</div>"
        f"  <div class='mm-typo-caption mm-text-muted'>Mode: {snapshot.session.mode}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.divider()

    if not snapshot.chats:
        st.info("No active tasks in this session. Start below.")
    else:
        # Latest / Active primary task prominently presented
        latest_chat = snapshot.chats[-1]
        st.markdown("#### 🎯 Active Task")
        st.caption(f"**Prompt:** {latest_chat.prompt}")

        st.markdown("##### Result")
        st.markdown(latest_chat.final_answer)

        # Progressive disclosure for debate breakdown
        if latest_chat.has_debate_data and latest_chat.debate_detail:
            with st.expander("Show Quality & Agent Details", expanded=False):
                d_detail = latest_chat.debate_detail
                if d_detail.has_error:
                    st.caption("Error reading debate details.")
                else:
                    if d_detail.gate_score is not None:
                        badge = ReleaseGate.get_badge(d_detail.gate_score)
                        st.caption(f"Gate Score: {d_detail.gate_score}/10 ({badge})")
                    for resp in d_detail.responses:
                        st.caption(f"Agent {resp.agent} ({resp.status})")
                        if resp.text:
                            st.markdown(resp.text)

        # Progressive disclosure for prior conversation history
        if len(snapshot.chats) > 1:
            st.divider()
            with st.expander(f"📜 Prior Task History ({len(snapshot.chats) - 1} previous items)", expanded=False):
                for prev_idx, prev_chat in enumerate(snapshot.chats[:-1], 1):
                    st.caption(f"**Task #{prev_idx}:** {prev_chat.prompt}")
                    st.markdown(prev_chat.final_answer)
                    st.divider()

    st.divider()
    if st.button("➕ New Chat", type="primary", key="minimal_saas_new_chat_btn", use_container_width=True):
        st.session_state.new_chat = True
        st.rerun()
