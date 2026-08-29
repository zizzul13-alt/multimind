"""
MultiMind AI - Archetype-Aware Interaction Shell Presentation Layer (S7.6)

Provides pure presentation entry points and composition policy for interaction
surfaces (composer morphology, processing feedback metadata, and turn lifecycle)
across all 7 canonical MultiMind archetypes.
"""
from typing import Dict, Any, Callable, Optional, Tuple
from html import escape
import streamlit as st

from ui.presentation.models import PresentationSnapshot, InteractionContext
from ui.presentation.resolver import resolve_archetype, CANONICAL_ARCHETYPE_IDS, FALLBACK_ARCHETYPE_ID
from ui.foundation import card_container, render_status_badge


# Truthful, presentation-only processing labels per canonical archetype
_PROCESSING_STATUS_MAP: Dict[str, str] = {
    "chat_first": "💬 Agents debating in conversation stream...",
    "command_center": "🎛️ Executing multi-agent operational debate...",
    "ai_workspace": "💼 Synthesizing response within active workspace...",
    "ai_research_lab": "🔬 Analyzing query context and synthesizing findings...",
    "agent_canvas": "🎨 Triggering agent workflow topology execution...",
    "terminal_hacker": "🖥️ [SYS_EXEC] Executing agent debate process...",
    "minimal_saas": "⚡ Processing task...",
}


def get_processing_label(active_archetype: str) -> str:
    """
    Returns presentation-only truthful status label for the active archetype.
    Used by execution handler without embedding archetype branch logic inside backend code.
    """
    return _PROCESSING_STATUS_MAP.get(active_archetype, "🤖 Agents debating...")


def _render_shared_controls(
    templates_mgr: Any,
    archetype: str
) -> Tuple[Optional[str], str]:
    """
    Renders existing template and chat mode controls with archetype-appropriate grouping.
    Returns (selected_template_id, context_mode_string).
    """
    template_list = [("", "No Template")] + (templates_mgr.get_template_names() if templates_mgr else [])

    if archetype in ("minimal_saas", "chat_first"):
        col1, col2 = st.columns([1, 1.2])
        with col1:
            selected_template = st.selectbox(
                "📋 Template (optional)",
                [t[0] for t in template_list],
                format_func=lambda x: dict(template_list).get(x, "No Template") if x != "" else "No Template",
                key="shell_selected_template",
                help="Select template for quick prompt"
            )
        with col2:
            chat_mode = st.radio(
                "Chat Mode:",
                ["🧵 Continue (with history)", "📌 Standalone (fresh)"],
                horizontal=True,
                key="shell_chat_mode"
            )
    else:
        c1, c2 = st.columns([1, 1])
        with c1:
            selected_template = st.selectbox(
                "📋 Prompt Template",
                [t[0] for t in template_list],
                format_func=lambda x: dict(template_list).get(x, "No Template") if x != "" else "No Template",
                key="shell_selected_template"
            )
        with c2:
            chat_mode = st.radio(
                "Context Strategy",
                ["🧵 Continue (with history)", "📌 Standalone (fresh)"],
                horizontal=True,
                key="shell_chat_mode"
            )

    context_mode = "continue" if "Continue" in chat_mode else "standalone"
    return selected_template, context_mode


def _render_template_variables_and_preview(templates_mgr: Any, selected_template: Optional[str]) -> str:
    """Renders template variable inputs and template preview if selected."""
    default_prompt = ""
    if selected_template and selected_template != "" and templates_mgr:
        template = templates_mgr.get_template(selected_template)
        if template:
            st.caption(f"📝 {template.get('description', '')}")
            import re
            variables = re.findall(r'\{\{(\w+)\}\}', template.get('prompt', ''))
            if variables:
                st.caption("🔧 Fill variables:")
                vars_dict = {}
                cols = st.columns(min(len(variables), 3))
                for i, var in enumerate(variables):
                    with cols[i % 3]:
                        vars_dict[var] = st.text_input(f"{var}", key=f"shell_var_{var}_{selected_template}")
                st.session_state.template_variables = vars_dict

            result = templates_mgr.apply_template(
                selected_template,
                st.session_state.get("template_variables", {})
            )
            if result:
                new_prompt = result.get("prompt", "")
                default_prompt = new_prompt
                if new_prompt != st.session_state.get("last_generated", ""):
                    st.session_state.prompt_main = new_prompt
                    st.session_state.last_generated = new_prompt

        if default_prompt:
            card_container(
                f"<div class='mm-typo-label'>📋 Template Preview:</div>"
                f"<pre class='mm-typo-mono'>{escape(default_prompt)}</pre>",
                variant="muted"
            )
    return default_prompt



def _render_token_estimation_metrics(prompt: str, uploaded_files: Any, archetype: str) -> None:
    """Restores Token/Cost estimation metrics from CURRENT MAIN."""
    if prompt or uploaded_files:
        from utils.token_counter import TokenCounter
        files_count = len(uploaded_files) if uploaded_files else 0
        session_mode = st.session_state.current_session.get('mode', 'coding') if st.session_state.get('current_session') else 'coding'
        rounds = st.session_state.get('debate_rounds', 1)
        compressor_on = st.session_state.get('compressor_enabled', False)

        estimate = TokenCounter.estimate_total(
            prompt or '',
            files_count=files_count,
            mode=session_mode,
            rounds=rounds,
            compressor_on=compressor_on
        )
        warning = TokenCounter.get_warning_level(estimate['total_estimate'])
        cost = TokenCounter.estimate_cost(estimate['total_estimate'])

        card_container(
            f"<div class='mm-flex-between' style='margin-bottom:0;'>"
            f"  <span class='mm-typo-label'>📊 Estimated Usage:</span>"
            f"  <span class='mm-typo-body-small'>"
            f"    <b>Prompt:</b> {estimate['prompt_tokens']} tok | "
            f"    <b>Files:</b> {estimate['file_tokens']} tok | "
            f"    <b>Total:</b> {estimate['total_estimate']} tok "
            f"    <span class='mm-badge mm-badge-info' style='margin-left:0.4rem;'>${cost:.6f}</span>"
            f"  </span>"
            f"</div>",
            variant="muted"
        )

        if warning["level"] == "high":
            render_status_badge("🔴 High token usage! Consider compressor.", variant="danger")
        elif warning["level"] == "medium":
            render_status_badge("🟡 Moderate token usage.", variant="warning")


def _render_action_buttons(
    archetype: str,
    on_send: Callable[[str, Any, str], None],
    on_cancel: Callable[[], None],
    prompt: str,
    uploaded_files: Any,
    context_mode: str
) -> None:
    """Renders primary Send and Cancel triggers."""
    col1, col2 = st.columns([3, 1])
    send_label = "🚀 Send Command" if archetype == "terminal_hacker" else ("🚀 Execute Action" if archetype in ("command_center", "agent_canvas") else "🚀 Send")
    with col1:
        if st.button(send_label, type="primary", key=f"shell_send_btn_{archetype}", use_container_width=True):
            if prompt or uploaded_files:
                on_send(prompt, uploaded_files, context_mode)
            else:
                st.error("Please enter a prompt or upload files")
    with col2:
        if st.button("❌ Cancel", key=f"shell_cancel_btn_{archetype}", use_container_width=True):
            on_cancel()


def _render_composer_surface(
    ctx: InteractionContext,
    templates_mgr: Any,
    on_send: Callable[[str, Any, str], None],
    on_cancel: Callable[[], None]
) -> None:
    """
    Renders archetype-specific composer surface morphology using existing capabilities on CURRENT MAIN.
    """
    archetype = ctx.active_archetype if ctx.active_archetype in CANONICAL_ARCHETYPE_IDS else FALLBACK_ARCHETYPE_ID

    if archetype == "chat_first":
        # Conversation-attached composer directly in document flow
        st.markdown("<div class='mm-typo-heading' style='margin-top: var(--mm-space-lg); margin-bottom: var(--mm-space-xs);'>💬 New Conversation Turn</div>", unsafe_allow_html=True)
        selected_template, context_mode = _render_shared_controls(templates_mgr, archetype)
        _render_template_variables_and_preview(templates_mgr, selected_template)
        prompt = st.text_area("Prompt:", height=120, placeholder="Type your message...", key="prompt_main")
        uploaded_files = st.file_uploader("📎 Files (optional)", accept_multiple_files=True, type=['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css', 'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx'], key="new_chat_files")
        _render_token_estimation_metrics(prompt, uploaded_files, archetype)
        _render_action_buttons(archetype, on_send, on_cancel, prompt, uploaded_files, context_mode)

    elif archetype == "command_center":
        # Operational Action Surface
        with st.container():
            st.markdown("<div class='mm-typo-heading' style='margin-bottom: var(--mm-space-xs);'>🎛️ Operational Action Surface</div>", unsafe_allow_html=True)
            with st.expander("⚙️ Mission Configuration", expanded=True):
                selected_template, context_mode = _render_shared_controls(templates_mgr, archetype)
                _render_template_variables_and_preview(templates_mgr, selected_template)
            prompt = st.text_area("Operational Instruction / Prompt:", height=120, placeholder="Enter operational objective...", key="prompt_main")
            uploaded_files = st.file_uploader("📎 Context Documents / Files", accept_multiple_files=True, type=['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css', 'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx'], key="new_chat_files")
            _render_token_estimation_metrics(prompt, uploaded_files, archetype)
            _render_action_buttons(archetype, on_send, on_cancel, prompt, uploaded_files, context_mode)

    elif archetype == "ai_workspace":
        # Anchored Work Session Pane
        st.markdown("<div class='mm-typo-heading' style='margin-top: var(--mm-space-md);'>💼 Work Session Composer</div>", unsafe_allow_html=True)
        selected_template, context_mode = _render_shared_controls(templates_mgr, archetype)
        _render_template_variables_and_preview(templates_mgr, selected_template)
        prompt = st.text_area("Workspace Task Prompt:", height=130, placeholder="Describe task or document update...", key="prompt_main")
        uploaded_files = st.file_uploader("📎 Workspace File Attachments", accept_multiple_files=True, type=['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css', 'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx'], key="new_chat_files")
        _render_token_estimation_metrics(prompt, uploaded_files, archetype)
        _render_action_buttons(archetype, on_send, on_cancel, prompt, uploaded_files, context_mode)

    elif archetype == "ai_research_lab":
        # Research Query Initiation Surface
        st.markdown("<div class='mm-typo-heading' style='margin-top: var(--mm-space-md);'>🔬 Research Query Initiation</div>", unsafe_allow_html=True)
        selected_template, context_mode = _render_shared_controls(templates_mgr, archetype)
        _render_template_variables_and_preview(templates_mgr, selected_template)
        prompt = st.text_area("Research Question / Hypothesis:", height=140, placeholder="State research topic or inquiry...", key="prompt_main")
        uploaded_files = st.file_uploader("📎 Research Evidence Files", accept_multiple_files=True, type=['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css', 'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx'], key="new_chat_files")
        _render_token_estimation_metrics(prompt, uploaded_files, archetype)
        _render_action_buttons(archetype, on_send, on_cancel, prompt, uploaded_files, context_mode)

    elif archetype == "agent_canvas":
        # Input Trigger Node Composer
        st.markdown("<div class='mm-typo-heading' style='margin-top: var(--mm-space-md);'>🎨 Workflow Execution Trigger Node</div>", unsafe_allow_html=True)
        selected_template, context_mode = _render_shared_controls(templates_mgr, archetype)
        _render_template_variables_and_preview(templates_mgr, selected_template)
        prompt = st.text_area("Node Input Trigger Prompt:", height=120, placeholder="Enter input prompt for agent workflow step...", key="prompt_main")
        uploaded_files = st.file_uploader("📎 Node Data Attachments", accept_multiple_files=True, type=['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css', 'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx'], key="new_chat_files")
        _render_token_estimation_metrics(prompt, uploaded_files, archetype)
        _render_action_buttons(archetype, on_send, on_cancel, prompt, uploaded_files, context_mode)

    elif archetype == "terminal_hacker":
        # Monospaced Command Console Surface
        st.markdown("<div class='mm-typo-mono' style='font-size: 1.1rem; font-weight: bold; margin-top: var(--mm-space-md);'>🖥️ $ MM_EXEC --init-turn</div>", unsafe_allow_html=True)
        with st.expander("CONSOLE OPTIONS", expanded=False):
            selected_template, context_mode = _render_shared_controls(templates_mgr, archetype)
            _render_template_variables_and_preview(templates_mgr, selected_template)
            uploaded_files = st.file_uploader("📎 CONSOLE_UPLOADS", accept_multiple_files=True, type=['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css', 'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx'], key="new_chat_files")
        if "selected_template" not in locals():
            selected_template, context_mode = "", "continue"
        if "uploaded_files" not in locals():
            uploaded_files = None
        prompt = st.text_area("COMMAND_PROMPT >", height=110, placeholder="Enter command prompt...", key="prompt_main")
        _render_token_estimation_metrics(prompt, uploaded_files, archetype)
        _render_action_buttons(archetype, on_send, on_cancel, prompt, uploaded_files, context_mode)

    elif archetype == "minimal_saas":
        # Direct Task Input Surface with Progressive Disclosure
        st.markdown("<div class='mm-typo-heading' style='margin-top: var(--mm-space-sm);'>⚡ Direct Task Entry</div>", unsafe_allow_html=True)
        prompt = st.text_area("Task Description:", height=100, placeholder="What would you like to solve?", key="prompt_main")
        with st.expander("⚙️ Advanced Options (Template, Mode, Files)", expanded=False):
            selected_template, context_mode = _render_shared_controls(templates_mgr, archetype)
            _render_template_variables_and_preview(templates_mgr, selected_template)
            uploaded_files = st.file_uploader("📎 Attachments", accept_multiple_files=True, type=['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css', 'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx'], key="new_chat_files")
        if "selected_template" not in locals():
            selected_template, context_mode = "", "continue"
        if "uploaded_files" not in locals():
            uploaded_files = None
        _render_token_estimation_metrics(prompt, uploaded_files, archetype)
        _render_action_buttons(archetype, on_send, on_cancel, prompt, uploaded_files, context_mode)


def render_interaction_shell(
    ctx: InteractionContext,
    snapshot: PresentationSnapshot,
    templates_mgr: Any,
    on_send: Callable[[str, Any, str], None],
    on_cancel: Callable[[], None]
) -> None:
    """
    Authoritative interaction shell entry point.
    Renders active archetype projection and attaches the archetype-specific composer
    morphology when new_chat turn initiation is active.
    """
    archetype = ctx.active_archetype if ctx.active_archetype in CANONICAL_ARCHETYPE_IDS else FALLBACK_ARCHETYPE_ID

    # 1. Render active session projection surface
    renderer = resolve_archetype(archetype)
    renderer(snapshot)

    # 2. Attach archetype composer morphology if initiating new turn
    if ctx.new_chat_active:
        _render_composer_surface(ctx, templates_mgr, on_send, on_cancel)
