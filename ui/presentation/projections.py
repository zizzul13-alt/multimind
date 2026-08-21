"""
MultiMind AI - Canonical Archetype Projections (S7.5 / Semantic Composition Refactor)

Pure UI renderers projecting a single read-only PresentationSnapshot into
distinct archetype views with explicit semantic composition policies,
native container hooks, reading sanctuary protection, and responsive transformation hooks.

Recognized Archetypes (Exactly 7):
1. Chat-first (`render_chat_first`): Continuous conversation is primary.
2. Command Center (`render_command_center`): Operational state and metrics are primary.
3. AI Workspace (`render_ai_workspace`): Multi-object organization & anchored work context.
4. AI Research Lab (`render_ai_research_lab`): Evidence, findings, & synthesis hierarchy.
5. Agent Canvas (`render_agent_canvas`): Agent roles, topology, & execution workflow step flow.
6. Terminal / Hacker AI (`render_terminal_hacker`): Instruction -> execution -> output sequence stream.
7. Minimal SaaS (`render_minimal_saas`): Restrained primary task focus with progressive disclosure.
"""
import streamlit as st
from ui.presentation.models import PresentationSnapshot
from ui.foundation import render_status_badge, semantic_zone
from core.release_gate import ReleaseGate


def render_chat_first(snapshot: PresentationSnapshot) -> None:
    """
    Renders Chat-first Archetype Projection.

    Primary Mental Model: "I am having an ongoing conversation with MultiMind."
    Primary Object: Conversation (continuous reading sanctuary).
    Composition Policy:
    - Central reading column owns continuous perceptual gravity (`mm-zone-primary mm-zone-reading`).
    - Subordinate memory metrics and session state housed in compact utility zone (`mm-zone-utility`).
    - Message composer trigger (New Chat) is immediately discoverable.
    """
    # Zone 1: Subordinate Metadata & Memory Utility
    with st.container(key="chat_first_meta_container"):
        col_title, col_meta = st.columns([3, 1])
        with col_title:
            st.subheader(f"💬 {snapshot.session.name}")
        with col_meta:
            st.caption(f"Mode: {snapshot.session.mode} | Created: {snapshot.session.created_at[:10]}")

        if snapshot.memory:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Context Tokens", snapshot.memory.context_tokens)
            with col2:
                st.metric("Short-term Chats", snapshot.memory.short_term_chats)
            with col3:
                st.metric("Free Space", f"{snapshot.memory.free_percent}%")

    st.divider()

    # Zone 2: Continuous Conversation Feed (Dominant Primary Content & Reading Sanctuary)
    with st.container(key="chat_first_feed_container"):
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

    # Zone 3: Primary Action
    with st.container(key="chat_first_action_container"):
        if st.button("➕ New Chat", type="primary", key="chat_first_new_chat_btn", use_container_width=True):
            st.session_state.new_chat = True
            st.rerun()


def render_command_center(snapshot: PresentationSnapshot) -> None:
    """
    Renders Command Center Archetype Projection.

    Primary Mental Model: "I am observing and controlling MultiMind's operation."
    Primary Object: Operational State & Comparative Agent Matrix (`mm-zone-operational`).
    Composition Policy:
    - System metrics and active agent comparison grid dominate prominence (`mm-zone-status`, `mm-zone-activity`).
    - Gate score and error flags organize the operational attention hierarchy (`mm-zone-operational`).
    - Conversation content subordinated to contextual side-panel or collapsible detail.
    """
    # Zone 1: Command Header & System Operational Metrics
    with st.container(key="command_center_header_container"):
        col_title, col_meta = st.columns([3, 1])
        with col_title:
            st.subheader(f"🎛️ Command Center — {snapshot.session.name}")
        with col_meta:
            st.caption(f"Mode: {snapshot.session.mode} | ID: {snapshot.session.id[:8]}")

        st.markdown("#### ⚡ System Operational Status")
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

    # Zone 2: Primary Operational Focus - Agent Comparison Matrix & Execution Status
    with st.container(key="command_center_matrix_container"):
        st.markdown("#### 🤖 Agent Operational Comparison Matrix")

        if not snapshot.chats:
            st.info("No execution/debate data logged in this session yet.")
        else:
            for idx, chat in enumerate(snapshot.chats, 1):
                with st.expander(f"Execution Log #{idx} (ID: {chat.id[:8]}) — {chat.tokens_used} tokens, ${chat.cost:.6f}", expanded=(idx == len(snapshot.chats))):
                    st.caption(f"**Trigger Prompt:** {chat.prompt}")

                    if chat.has_debate_data and chat.debate_detail:
                        d_detail = chat.debate_detail
                        if d_detail.has_error:
                            st.error("⚠️ Debate details contain errors or unparseable data.")
                        else:
                            if d_detail.gate_score is not None:
                                badge = ReleaseGate.get_badge(d_detail.gate_score)
                                st.markdown(f"**Gate Verdict Score:** `{d_detail.gate_score}/10` ({badge})")

                            if d_detail.responses:
                                st.markdown("##### Parallel Agent Output Comparison")
                                agent_cols = st.columns(min(len(d_detail.responses), 4))
                                for col_i, resp in enumerate(d_detail.responses):
                                    with agent_cols[col_i % len(agent_cols)]:
                                        badge_variant = "success" if resp.status == "success" else ("danger" if resp.status == "error" else "warning")
                                        render_status_badge(f"R{resp.round_index}: {resp.agent} ({resp.status.upper()})", variant=badge_variant)
                                        if resp.text:
                                            st.markdown(resp.text)
                                        else:
                                            st.caption("(No output)")
                            else:
                                st.caption("No individual agent responses logged.")
                    else:
                        st.caption("Standalone chat response (No debate orchestration data).")

                    st.markdown("##### Synthesized Result Output Context")
                    st.markdown(chat.final_answer)

    st.divider()

    # Zone 3: Primary Operational Action
    with st.container(key="command_center_action_container"):
        if st.button("➕ New Chat", type="primary", key="cmd_center_new_chat_btn", use_container_width=True):
            st.session_state.new_chat = True
            st.rerun()


def render_ai_workspace(snapshot: PresentationSnapshot) -> None:
    """
    Renders AI Workspace Archetype Projection.

    Primary Mental Model: "I work with multiple active objects."
    Primary Object: Workspace Objects (`mm-zone-primary`).
    Composition Policy:
    - Dual-pane layout: Anchored active workspace item on left/top (`mm-zone-primary`), orbiting contextual surfaces on right/bottom (`mm-zone-utility`).
    - Preserve work identity without destroying active context.
    """
    with st.container(key="ai_workspace_header_container"):
        col_title, col_meta = st.columns([3, 1])
        with col_title:
            st.subheader(f"💼 Workspace Overview — {snapshot.session.name}")
        with col_meta:
            st.caption(f"Mode: {snapshot.session.mode} | Created: {snapshot.session.created_at[:10]}")

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

    # Organized Workspace Objects (Dual Pane Anchor)
    with st.container(key="ai_workspace_objects_container"):
        st.markdown("#### 📂 Active Workspace Objects")
        if not snapshot.chats:
            st.info("Workspace is currently empty. Create a new item below.")
        else:
            for idx, chat in enumerate(snapshot.chats, 1):
                with st.container():
                    st.markdown(f"##### Workspace Item #{idx} · Mode: `{chat.mode.upper()}` · Tokens: `{chat.tokens_used}`")
                    col_prompt, col_answer = st.columns([1, 1])
                    with col_prompt:
                        st.markdown("**Anchored Prompt Object:**")
                        st.write(chat.prompt)
                    with col_answer:
                        st.markdown("**Generated Workspace Artifact:**")
                        st.markdown(chat.final_answer)

                    if chat.has_debate_data and chat.debate_detail:
                        with st.expander(f"⚙️ Orbiting Context Details (Item #{idx})"):
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

    with st.container(key="ai_workspace_action_container"):
        if st.button("➕ New Chat", type="primary", key="ai_workspace_new_chat_btn", use_container_width=True):
            st.session_state.new_chat = True
            st.rerun()


def render_ai_research_lab(snapshot: PresentationSnapshot) -> None:
    """
    Renders AI Research Lab Archetype Projection.

    Primary Mental Model: "I investigate evidence and build conclusions."
    Primary Object: Evidence / Findings / Synthesis Hierarchy (`mm-zone-primary`, `mm-zone-evidence`).
    Composition Policy:
    - Synthesized conclusion dominates as the primary thesis (`mm-zone-primary`).
    - Relational claim/evidence traversal maps synthesis directly to underlying agent findings (`mm-zone-evidence`).
    - EVIDENCE TRUTH: Never fabricate non-existent citations or external sources.
    """
    with st.container(key="ai_research_lab_header_container"):
        col_title, col_meta = st.columns([3, 1])
        with col_title:
            st.subheader(f"🔬 AI Research Lab — {snapshot.session.name}")
        with col_meta:
            st.caption(f"Mode: {snapshot.session.mode} | ID: {snapshot.session.id[:8]}")

        if snapshot.memory:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Research Context Tokens", snapshot.memory.context_tokens)
            with col2:
                st.metric("Analyzed Queries", snapshot.memory.short_term_chats)
            with col3:
                st.metric("Memory Capacity", f"{snapshot.memory.free_percent}%")

    st.divider()

    with st.container(key="ai_research_lab_findings_container"):
        st.markdown("#### 🧪 Research Findings & Relational Evidence Traversal")

        if not snapshot.chats:
            st.info("No research items or findings in this session yet.")
        else:
            for idx, chat in enumerate(snapshot.chats, 1):
                st.markdown(f"### Research Query #{idx}")
                st.caption(f"**Research Prompt:** {chat.prompt}")

                # Zone 1: Synthesized Conclusion Banner (Primary Thesis)
                st.markdown("##### 🔍 Synthesized Conclusion (Primary Thesis)")
                st.markdown(chat.final_answer)

                # Zone 2: Agent Evidence & Findings Relational Traversal
                if chat.has_debate_data and chat.debate_detail:
                    d_detail = chat.debate_detail
                    if d_detail.has_error:
                        st.error("⚠️ Evidence breakdown contains corrupted data.")
                    else:
                        st.markdown("##### 📄 Underlying Agent Evidence & Analysis Traversal")
                        if d_detail.gate_score is not None:
                            badge = ReleaseGate.get_badge(d_detail.gate_score)
                            st.caption(f"Release Gate Quality Confidence: **{d_detail.gate_score}/10** ({badge})")

                        if d_detail.responses:
                            # Use tabs to provide clear relational traversal between agent findings
                            tab_names = [f"Finding: {r.agent}" for r in d_detail.responses]
                            tabs = st.tabs(tab_names)
                            for t_idx, resp in enumerate(d_detail.responses):
                                with tabs[t_idx]:
                                    badge_variant = "success" if resp.status == "success" else ("danger" if resp.status == "error" else "warning")
                                    render_status_badge(f"Round {resp.round_index} - Agent {resp.agent} ({resp.status.upper()})", variant=badge_variant)
                                    if resp.text:
                                        st.markdown(resp.text)
                                    else:
                                        st.caption("(No output recorded for this agent node)")
                        else:
                            st.caption("No individual agent evidence records present.")
                else:
                    st.caption("Standalone analysis result (No multi-agent debate evidence recorded).")

                st.caption(f"Analysis Tokens: {chat.tokens_used} | Cost: ${chat.cost:.6f}")
                st.divider()

    with st.container(key="ai_research_lab_action_container"):
        if st.button("➕ New Chat", type="primary", key="ai_research_lab_new_chat_btn", use_container_width=True):
            st.session_state.new_chat = True
            st.rerun()


def render_agent_canvas(snapshot: PresentationSnapshot) -> None:
    """
    Renders Agent Canvas Archetype Projection.

    Primary Mental Model: "I work with agent relationships and execution flow topology."
    Primary Object: Agent Execution Flow Topology (`mm-zone-topology`).
    Composition Policy:
    - Sequential workflow topology graph step nodes (`mm-zone-topology`).
    - TOPOLOGY TRUTH: Only express actual execution path (Prompt Trigger -> Agent Debate Responses -> Gate Decision -> Synthesized Result Node).
    - Mobile / Narrow Viewport: Navigable step topology explorer using tabs/containers.
    """
    with st.container(key="agent_canvas_header_container"):
        col_title, col_meta = st.columns([3, 1])
        with col_title:
            st.subheader(f"🎨 Agent Canvas — {snapshot.session.name}")
        with col_meta:
            st.caption(f"Mode: {snapshot.session.mode} | Session ID: {snapshot.session.id[:8]}")

    st.divider()

    with st.container(key="agent_canvas_topology_container"):
        st.markdown("#### 🧬 Workflow Sequence & Agent Topology Flow")

        if not snapshot.chats:
            st.info("No active agent canvas entries in this session.")
        else:
            for idx, chat in enumerate(snapshot.chats, 1):
                st.markdown(f"#### Workflow Node #{idx}")
                st.caption(f"**Trigger Input Node:** {chat.prompt}")

                # Sequential Topology Nodes
                if chat.has_debate_data and chat.debate_detail and not chat.debate_detail.has_error:
                    d_detail = chat.debate_detail
                    st.markdown("##### 🔄 Parallel Agent Step Flow Nodes")

                    if d_detail.responses:
                        # Render step topology cards
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
                        st.markdown(f"**🎯 Release Gate Decision Node:** Score `{d_detail.gate_score}/10` ({badge})")
                elif chat.debate_detail and chat.debate_detail.has_error:
                    st.error("⚠️ Topology step failed due to corrupted debate data.")
                else:
                    st.caption("Direct execution path (Single model, no debate topology).")

                st.markdown("##### 🏁 Synthesized Output Node")
                st.markdown(chat.final_answer)

                st.caption(f"Node Metrics: {chat.tokens_used} tokens | ${chat.cost:.6f}")
                st.divider()

    with st.container(key="agent_canvas_action_container"):
        if st.button("➕ New Chat", type="primary", key="agent_canvas_new_chat_btn", use_container_width=True):
            st.session_state.new_chat = True
            st.rerun()


def render_terminal_hacker(snapshot: PresentationSnapshot) -> None:
    """
    Renders Terminal / Hacker AI Archetype Projection.

    Primary Mental Model: "I issue instructions and observe execution stream chronology."
    Primary Object: Causal Execution Chronology Stream (`mm-zone-chronology`).
    Composition Policy:
    - Sequential operational log stream: `intent` -> `execution/activity` -> `observable state` -> `result`.
    - Operational sys logs use monospaced code font (`var(--mm-font-mono)`).
    - READING SANCTUARY PRESERVATION: Sustained final answer text transitions into proportional typography (`var(--mm-font-base)`) for reading comfort (`mm-zone-reading`).
    """
    with st.container(key="terminal_hacker_header_container"):
        col_title, col_meta = st.columns([3, 1])
        with col_title:
            st.subheader(f"🖥️ Terminal / Operational Stream — {snapshot.session.name}")
        with col_meta:
            st.caption(f"SYS_MODE: {snapshot.session.mode.upper()} | UUID: {snapshot.session.id[:8]}")

        if snapshot.memory:
            st.text(f"[SYS_METRICS] CTX_TOKENS={snapshot.memory.context_tokens} | SHORT_TERM_CHATS={snapshot.memory.short_term_chats} | FREE_MEM={snapshot.memory.free_percent}%")

    st.divider()

    with st.container(key="terminal_hacker_stream_container"):
        st.markdown("#### 📜 Operational Execution Stream")

        if not snapshot.chats:
            st.info("[STREAM_EMPTY] No instruction records in buffer.")
        else:
            for idx, chat in enumerate(snapshot.chats, 1):
                st.text(f"--- [EXECUTION_SEQUENCE #{idx}] ID: {chat.id[:8]} MODE: {chat.mode.upper()} ---")

                # Step 1: Intent / Instruction
                st.markdown(f"**$ USER_INSTRUCTION:** `{chat.prompt}`")

                # Step 2: Execution Progression & Activity
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

                # Step 3: Result / Output Stream in Reading Sanctuary
                st.markdown("**[SYSTEM_OUTPUT] (Reading Sanctuary):**")
                st.markdown(chat.final_answer)

                st.text(f"[STREAM_END] TOKENS={chat.tokens_used} COST=${chat.cost:.6f}\n")
                st.divider()

    with st.container(key="terminal_hacker_action_container"):
        if st.button("➕ New Chat", type="primary", key="terminal_hacker_new_chat_btn", use_container_width=True):
            st.session_state.new_chat = True
            st.rerun()


def render_minimal_saas(snapshot: PresentationSnapshot) -> None:
    """
    Renders Minimal SaaS Archetype Projection.

    Primary Mental Model: "I complete the current active task without unnecessary clutter."
    Primary Object: Direct Task Action & Active Result (`mm-zone-primary`).
    Composition Policy:
    - High contrast active task card dominates screen.
    - Historical chats and secondary debate details are hidden behind progressive disclosure (`st.expander`), NOT rendered as an ongoing continuous chat feed.
    """
    with st.container(key="minimal_saas_header_container"):
        col_title, col_meta = st.columns([3, 1])
        with col_title:
            st.subheader(f"⚡ {snapshot.session.name}")
        with col_meta:
            st.caption(f"Mode: {snapshot.session.mode}")

    st.divider()

    with st.container(key="minimal_saas_task_container"):
        if not snapshot.chats:
            st.info("No active tasks in this session. Start below.")
        else:
            # Active primary task prominently presented
            latest_chat = snapshot.chats[-1]
            st.markdown("#### 🎯 Active Task")
            st.caption(f"**Prompt:** {latest_chat.prompt}")

            st.markdown("##### Task Result")
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

            # Progressive disclosure for prior conversation history (Separates from Chat First)
            if len(snapshot.chats) > 1:
                st.divider()
                with st.expander(f"📜 Prior Task History ({len(snapshot.chats) - 1} previous items)", expanded=False):
                    for prev_idx, prev_chat in enumerate(snapshot.chats[:-1], 1):
                        st.caption(f"**Task #{prev_idx}:** {prev_chat.prompt}")
                        st.markdown(prev_chat.final_answer)
                        st.divider()

    st.divider()

    with st.container(key="minimal_saas_action_container"):
        if st.button("➕ New Chat", type="primary", key="minimal_saas_new_chat_btn", use_container_width=True):
            st.session_state.new_chat = True
            st.rerun()
