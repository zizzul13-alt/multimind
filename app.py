"""
MultiMind AI - Multi-Agent Debate System
Main Streamlit Application
"""
import streamlit as st
import os
from html import escape
from datetime import datetime

from agents.router import TERMINAL_PROVIDER_FAILURE_TEXT
from core.application import ApplicationRuntime, ChatRequest
from core.compressor import PromptCompressor
from core.debate import DebateOrchestrator
from core.file_handler import FileHandler
from core.memory import persist_chat_and_update_memory
from core.composition import build_agents, build_application_for_user, build_database_for_user
from core.release_gate import ReleaseGate
from core.skills_manager import SkillsManager
from core.templates import TemplateManager
from utils.token_counter import TokenCounter
from utils.config import Config, InvalidUserIdError
from utils.identity_state import initialize_identity_state, reset_identity_bound_state
from ui.dna_bridge import ensure_optional_dna_registered, render_optional_theme_studio
from ui.foundation import load_css, render_status_badge, card_container
from ui.presentation import build_presentation_snapshot, render_archetype, list_archetypes, render_brand_identity
from ui.themes import list_themes

# Optional DNA enrichments are registered when the quarantined package is present.
# Public runtime remains on the canonical safe/default theme when it is absent.
ensure_optional_dna_registered()

st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "initialized" not in st.session_state:
    st.session_state.initialized = True

initialize_identity_state(st.session_state)

if "active_navigation" not in st.session_state:
    st.session_state.active_navigation = "workspace"

if "active_theme" not in st.session_state:
    st.session_state.active_theme = "default"

if "active_archetype" not in st.session_state:
    qp_arch = st.query_params.get("archetype", None)
    if qp_arch and isinstance(qp_arch, str):
        from ui.presentation.resolver import CANONICAL_ARCHETYPE_IDS, FALLBACK_ARCHETYPE_ID
        st.session_state.active_archetype = qp_arch if qp_arch in CANONICAL_ARCHETYPE_IDS else FALLBACK_ARCHETYPE_ID
    else:
        st.session_state.active_archetype = "chat_first"

load_css(st.session_state.get("active_theme", "default"))


def get_streamlit_secrets():
    """Presentation-edge adapter for Streamlit's secrets object."""
    try:
        return dict(st.secrets)
    except Exception:
        return {}


@st.cache_resource
def get_agents(user_id):
    api_keys = Config.get_api_keys(user_id, secrets_source=get_streamlit_secrets)
    return build_agents(api_keys)


def get_db_manager(user_id):
    """Compatibility lifecycle seam; presentation data access stays in the application."""
    return build_database_for_user(user_id)


@st.cache_resource
def get_skills_manager():
    return SkillsManager()


@st.cache_resource
def get_template_manager():
    return TemplateManager()


def get_application(user_id, agents=None, db=None, runtime=None):
    """Use the shared plain-Python composition path from the Streamlit edge."""
    return build_application_for_user(
        user_id,
        secrets_source=get_streamlit_secrets,
        runtime_memories=st.session_state.memories,
        runtime=runtime,
        db=db,
        db_factory=None if db is not None else lambda: get_db_manager(user_id),
        agents=get_agents(user_id) if agents is None else agents,
        compressor=PromptCompressor,
        file_handler=FileHandler,
        debate_factory=DebateOrchestrator,
        persist_chat=persist_chat_and_update_memory,
    )


def show_login_page():
    card_container(
        "<div class='mm-typo-display'>🤖 MultiMind AI</div>"
        "<div class='mm-typo-subheading mm-text-muted'>Multi-Agent AI Debate System</div>",
        variant="elevated"
    )
    st.subheader("🔐 Silakan Login")
    username = st.text_input("Username", placeholder="Ketik username bebas...", key="login_username_input")
    if st.button("🚀 Masuk", type="primary", key="login_button"):
        if username:
            try:
                display_username, user_id = Config.resolve_supplied_identity(username)
            except InvalidUserIdError as exc:
                st.error(str(exc))
                return

            if st.session_state.user_id != user_id:
                reset_identity_bound_state(st.session_state)
            st.session_state.user = display_username
            st.session_state.user_id = user_id
            st.rerun()
        else:
            st.error("Username tidak boleh kosong!")
    st.divider()
    card_container(
        "<div class='mm-typo-label'>💡 Info:</div>"
        "<ul class='mm-typo-body-small mm-text-muted' style='margin-bottom:0; padding-left: 1.2rem;'>"
        "<li>Masukkan username bebas (Izzul, Miko, atau nama lain)</li>"
        "<li>Data kamu PRIVASI & terpisah dari user lain</li>"
        "<li>API keys diatur oleh admin</li>"
        "</ul>",
        variant="muted"
    )


def show_sidebar():
    with st.sidebar:
        render_brand_identity(
            st.session_state.get("active_theme", "default"),
            user_label=str(st.session_state.user or ""),
            container_kind="sidebar"
        )

        curr_nav = st.session_state.get("active_navigation", "workspace")
        view_mode = st.radio(
            "📍 Navigation View",
            ["💬 Main Workspace", "🎨 Theme Studio"],
            index=0 if curr_nav == "workspace" else 1,
            key="sidebar_navigation_view"
        )
        new_nav = "theme_studio" if "Theme Studio" in str(view_mode) else "workspace"
        if new_nav != curr_nav:
            st.session_state.active_navigation = new_nav
            st.rerun()

        st.divider()
        application = get_application(st.session_state.user_id)

        with st.expander("➕ New Session", expanded=False):
            new_name = st.text_input("Name", placeholder="Project API...", key="sidebar_new_session_name")
            new_mode = st.selectbox("Mode", ["coding", "research", "thinking"], key="sidebar_new_session_mode")
            if st.button("Create", key="sidebar_create_session_btn", use_container_width=True):
                if new_name:
                    application.create_session(new_name, new_mode)
                    st.success("Created!")
                    st.rerun()

        st.caption("📂 SESSIONS")
        sessions = application.list_sessions()
        curr_session_id = st.session_state.current_session['id'] if st.session_state.current_session else None

        for i, s in enumerate(sessions):
            unique_key = f"sidebar_session_{i}_{s['id'][:8]}"
            is_active = (s['id'] == curr_session_id)
            s_name = s['name']
            truncated_name = s_name if len(s_name) <= 22 else f"{s_name[:19]}..."
            label = f"📌 {truncated_name}" if is_active else f"📝 {truncated_name}"
            btn_kind = "primary" if is_active else "secondary"
            if st.button(label, key=unique_key, use_container_width=True, type=btn_kind, help=s_name):
                st.session_state.current_session = s
                application.select_session(s)
                st.session_state.active_navigation = "workspace"
                st.rerun()

        st.divider()

        with st.expander("⚙️ Settings"):
            st.session_state.compressor_enabled = st.toggle(
                "🗜️ Compressor",
                value=st.session_state.compressor_enabled,
                key="settings_compressor"
            )
            st.session_state.debate_rounds = st.slider(
                "Debate Rounds",
                1, 5,
                st.session_state.debate_rounds,
                key="settings_rounds"
            )

            skills_mgr = get_skills_manager()
            skill_list = ["default"] + skills_mgr.list_skills()
            current_skill = st.session_state.get("selected_skill", "default")
            if current_skill not in skill_list:
                current_skill = "default"
            st.session_state.selected_skill = st.selectbox(
                "🎯 Skill",
                skill_list,
                index=skill_list.index(current_skill),
                key="settings_skill"
            )

            st.session_state.active_agents = st.multiselect(
                "Agents",
                ["unified", "remote", "cloudflare", "groq", "gemini", "openrouter", "huggingface", "deepseek"],
                default=st.session_state.active_agents,
                key="settings_agents"
            )

            available_themes = list_themes()
            current_theme_id = st.session_state.get("active_theme", "default")
            theme_ids = [t.id for t in available_themes]
            if current_theme_id not in theme_ids:
                current_theme_id = "default"
            theme_index = theme_ids.index(current_theme_id)

            selected_theme = st.selectbox(
                "🎨 Theme",
                available_themes,
                index=theme_index,
                format_func=lambda t: getattr(t, "display_name", str(t)),
                key="settings_theme"
            )
            selected_theme_id = getattr(selected_theme, "id", str(selected_theme)) if selected_theme else "default"
            if selected_theme_id != st.session_state.get("active_theme"):
                st.session_state.active_theme = selected_theme_id
                st.rerun()

            archetype_options = list_archetypes()
            arch_keys = [opt[0] for opt in archetype_options]
            arch_dict = dict(archetype_options)
            curr_arch = st.session_state.get("active_archetype", "chat_first")
            arch_index = arch_keys.index(curr_arch) if curr_arch in arch_keys else 0

            selected_arch = st.selectbox(
                "📐 Archetype View",
                arch_keys,
                index=arch_index,
                format_func=lambda k: arch_dict.get(k, k),
                key="settings_archetype"
            )
            if selected_arch != curr_arch:
                st.session_state.active_archetype = selected_arch
                st.rerun()

        st.divider()

        with st.expander("💾 Backup & Restore"):
            st.caption("Database SQLite")
            backup_bytes = application.export_database()
            st.download_button(
                "📥 Download Backup",
                backup_bytes,
                file_name=f"multimind_backup_{datetime.now():%Y%m%d}.db",
                mime="application/octet-stream",
                key="download_db_btn",
                use_container_width=True
            )

            uploaded_db = st.file_uploader("📤 Restore Backup", type=["db"], key="restore_db_uploader")
            if uploaded_db:
                if st.button("🔄 Restore", key="restore_db_btn", use_container_width=True):
                    runtime = ApplicationRuntime(
                        current_session=st.session_state.current_session,
                        memories=st.session_state.memories,
                    )
                    restore_result = get_application(
                        st.session_state.user_id, runtime=runtime,
                    ).restore_database(uploaded_db.getvalue())
                    if restore_result.runtime_invalidated:
                        st.session_state.current_session = runtime.current_session
                        st.session_state.memories = runtime.memories

                    if restore_result.status == "invalid_backup":
                        st.error("Backup tidak valid atau tidak kompatibel.")
                    elif restore_result.status == "operation_failed":
                        st.error("Database restore could not be completed. Please try again.")
                    else:
                        st.success("✅ Database restored! Refresh page.")
                        st.rerun()

        st.divider()
        if st.button("🚪 Logout", key="sidebar_logout_btn", use_container_width=True):
            reset_identity_bound_state(st.session_state)
            st.rerun()


def show_session():
    session = st.session_state.current_session
    memory = st.session_state.memories.get(session['id'])
    chats = get_application(st.session_state.user_id).get_session_chats(session['id'])

    snapshot = build_presentation_snapshot(session, chats, memory)

    active_archetype = st.session_state.get("active_archetype", "chat_first")
    render_archetype(active_archetype, snapshot)


def show_new_chat():
    st.markdown("<div class='mm-typo-heading' style='margin-bottom: var(--mm-space-md);'>💭 New Chat</div>", unsafe_allow_html=True)
    default_prompt = ""

    if "last_generated" not in st.session_state:
        st.session_state.last_generated = ""

    ctrl_col1, ctrl_col2 = st.columns([1, 1.2])

    with ctrl_col1:
        templates_mgr = get_template_manager()
        template_list = [("", "No Template")] + templates_mgr.get_template_names()

        selected_template = st.selectbox(
            "📋 Template (optional)",
            [t[0] for t in template_list],
            format_func=lambda x: dict(template_list)[x] if x != "" else "No Template",
            key="template_selector",
            help="Pilih template untuk quick prompt"
        )

    with ctrl_col2:
        chat_mode = st.radio("Chat Mode:", ["🧵 Continue (with history)", "📌 Standalone (fresh)"], horizontal=True, key="chat_mode_radio")
        context_mode = "continue" if "Continue" in chat_mode else "standalone"
        if context_mode == "continue":
            render_status_badge("AI will see previous chats in this session", variant="info")
        else:
            render_status_badge("AI starts fresh - no history (SAVES TOKENS!)", variant="success")

    if selected_template and selected_template != "":
        template = templates_mgr.get_template(selected_template)
        if template:
            st.caption(f"📝 {template['description']}")

            import re
            variables = re.findall(r'\{\{(\w+)\}\}', template['prompt'])
            if variables:
                st.caption("🔧 Isi variabel:")
                vars_dict = {}
                cols = st.columns(min(len(variables), 3))
                for i, var in enumerate(variables):
                    with cols[i % 3]:
                        vars_dict[var] = st.text_input(f"{var}", key=f"var_{var}_{selected_template}")
                st.session_state.template_variables = vars_dict

            result = templates_mgr.apply_template(
                selected_template,
                st.session_state.get("template_variables", {})
            )

            if result:
                new_prompt = result["prompt"]
                default_prompt = new_prompt

                if new_prompt != st.session_state.last_generated:
                    st.session_state.prompt_main = new_prompt
                    st.session_state.last_generated = new_prompt

    if selected_template and selected_template != "" and default_prompt:
        card_container(
            f"<div class='mm-typo-label'>📋 Template Preview:</div>"
            f"<pre class='mm-typo-mono'>{escape(default_prompt)}</pre>"
            f"<div class='mm-typo-caption mm-text-muted'>👆 Prompt otomatis masuk ke kolom di bawah, bisa langsung diedit.</div>",
            variant="muted"
        )

    prompt = st.text_area("Prompt:", height=150, placeholder="Paste template atau tulis bebas...", key="prompt_main")

    uploaded_files = st.file_uploader(
        "📎 Files (optional)",
        accept_multiple_files=True,
        type=['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css', 'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx'],
        key="new_chat_files"
    )

    if prompt or uploaded_files:
        files_count = len(uploaded_files) if uploaded_files else 0
        session_mode = st.session_state.current_session.get('mode', 'coding') if st.session_state.current_session else 'coding'
        estimate = TokenCounter.estimate_total(prompt or "", files_count=files_count, mode=session_mode, rounds=st.session_state.debate_rounds, compressor_on=st.session_state.compressor_enabled)
        warning = TokenCounter.get_warning_level(estimate["total_estimate"])

        cost = TokenCounter.estimate_cost(estimate["total_estimate"])
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

    st.markdown("<div class='mm-spacer-md'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🚀 Send", type="primary", key="send_chat_btn", use_container_width=True):
            if prompt or uploaded_files:
                process_chat(prompt, uploaded_files, context_mode)
            else:
                st.error("Please enter a prompt or upload files")
    with col2:
        if st.button("❌ Cancel", key="cancel_chat_btn", use_container_width=True):
            st.session_state.new_chat = False
            st.rerun()


def process_chat(prompt, uploaded_files, context_mode):
    """Render semantic application results for the current Streamlit host."""
    session = st.session_state.current_session
    result = get_application(st.session_state.user_id).execute_chat(ChatRequest(
        original_prompt=prompt,
        uploads=uploaded_files or [],
        context_mode=context_mode,
        session_id=session["id"] if session else None,
        session_mode=session.get("mode", "coding") if session else "coding",
        compressor_enabled=st.session_state.compressor_enabled,
        active_agents=st.session_state.active_agents,
        debate_rounds=st.session_state.debate_rounds,
        selected_skill=st.session_state.get("selected_skill", "default"),
    ))
    for warning in result.warnings:
        st.warning(warning)
    if result.status != "success":
        st.error(TERMINAL_PROVIDER_FAILURE_TEXT)
        return
    st.session_state.new_chat = False
    st.success("✅ Debate complete!")
    st.rerun()


def _render_theme_studio_unavailable() -> None:
    """Public safe fallback when optional private Theme Studio is unavailable."""
    card_container(
        "<div class='mm-typo-heading'>🎨 Theme Studio unavailable</div>"
        "<div class='mm-typo-body-small mm-text-muted'>"
        "This build is using the safe default presentation. Core workspace, sessions, "
        "and chat remain available.</div>",
        variant="muted",
    )


def main():
    if st.session_state.user:
        with st.sidebar:
            with st.expander("🔧 Debug Info"):
                st.write("User:", st.session_state.user_id)
                agents = get_agents(st.session_state.user_id)

                unified = agents.get("unified")

                if unified:
                    st.subheader("📊 Agent Stats")
                    stats = unified.get_stats()
                    for name, data in stats.items():
                        total = data["success"] + data["error"]
                        if total > 0:
                            success_rate = (data["success"] / total) * 100
                            status = "🟢" if not data["rate_limited"] else "🔴"
                            st.write(f"{status} {name}: {success_rate:.0f}% ({data['success']}/{total})")
                        else:
                            st.write(f"⚪ {name}: No data")

                st.divider()
                st.write("Gemini:", "✅" if agents.get("gemini") else "❌")
                st.write("DeepSeek:", "✅" if agents.get("deepseek") else "❌")
                st.write("Groq:", "✅" if agents.get("groq") else "❌")
                st.write("Cloudflare:", "✅" if agents.get("cloudflare") else "❌")
                st.write("OpenRouter:", "✅" if agents.get("openrouter") else "❌")
                st.write("HuggingFace:", "✅" if agents.get("huggingface") else "❌")
                st.write("Remote:", "✅" if agents.get("remote") else "❌")

                if os.getenv("MULTIMIND_DEV_SPIKE", "false").lower() in ("true", "1"):
                    st.divider()
                    with st.expander("⚡ Theme Preview Spike (Dev Only)", expanded=False):
                        try:
                            from ui.components.theme_preview_spike.preview_spike import render_theme_preview_spike
                            spike_result = render_theme_preview_spike(key="sidebar_dev_spike")
                            st.caption("Returned to Python:")
                            st.json(spike_result)
                        except Exception as e:
                            st.error(f"Spike load error: {e}")
    if st.session_state.user is None:
        show_login_page()
    else:
        show_sidebar()
        active_nav = st.session_state.get("active_navigation", "workspace")

        if active_nav == "theme_studio":
            render_optional_theme_studio(fallback=_render_theme_studio_unavailable)
        elif st.session_state.current_session:
            session = st.session_state.current_session
            memory = st.session_state.memories.get(session['id'])
            chats = get_application(st.session_state.user_id).get_session_chats(session['id'])

            snapshot = build_presentation_snapshot(session, chats, memory)
            active_archetype = st.session_state.get("active_archetype", "chat_first")

            from ui.presentation.models import SessionMetadataSnapshot, InteractionContext
            from ui.presentation.shell import render_interaction_shell

            session_meta = SessionMetadataSnapshot(
                id=session['id'],
                name=session.get('name', 'Untitled'),
                mode=session.get('mode', 'coding'),
                created_at=str(session.get('created_at', ''))
            )

            ctx = InteractionContext(
                active_archetype=active_archetype,
                new_chat_active=st.session_state.get("new_chat", False),
                session=session_meta,
                prompt_text=st.session_state.get("prompt_main", ""),
                selected_template=st.session_state.get("selected_template"),
                chat_mode=st.session_state.get("chat_mode", "continue"),
                is_processing=False
            )

            def handle_send(prompt, files, context_mode):
                from ui.presentation.shell import get_processing_label
                label = get_processing_label(active_archetype)
                with st.status(label, expanded=True):
                    process_chat(prompt, files, context_mode)

            def handle_cancel():
                st.session_state.new_chat = False
                st.rerun()

            templates_mgr = get_template_manager()
            render_interaction_shell(ctx, snapshot, templates_mgr, handle_send, handle_cancel)
        else:
            card_container(
                f"<div class='mm-typo-display'>🤖 Welcome, {st.session_state.user}!</div>"
                f"<div class='mm-typo-subheading mm-text-muted mm-subtitle-margin'>"
                f"Multi-Agent AI Debate & Collaboration Surface</div>"
                f"<div class='mm-spacer-md'>"
                f"<span class='mm-badge mm-badge-info'>👈 Select or create a session in the sidebar to start</span>"
                f"</div>",
                variant="elevated"
            )
            col1, col2 = st.columns(2)
            with col1:
                card_container(
                    "<div class='mm-section-title mm-typo-heading'>🚀 Getting Started</div>"
                    "<ol class='mm-list-styled mm-typo-body-small mm-text-muted'>"
                    "<li>Create a <b>New Session</b> in the sidebar</li>"
                    "<li>Pick a <b>Template</b> (optional) for quick prompts</li>"
                    "<li>Choose a <b>Skill</b> for specialized agent behavior</li>"
                    "<li>Select mode: <b>coding</b>, <b>research</b>, or <b>thinking</b></li>"
                    "<li>Start chatting with multi-agent debate!</li>"
                    "</ol>",
                    variant="default"
                )
            with col2:
                card_container(
                    "<div class='mm-section-title mm-typo-heading'>✨ Core Capabilities</div>"
                    "<ul class='mm-list-styled mm-typo-body-small mm-text-muted'>"
                    "<li>🤖 <b>6 AI Agents</b> (Gemini, Groq, Cloudflare, OpenRouter, HuggingFace, DeepSeek)</li>"
                    "<li>📋 <b>Prompt Templates & Skills System</b></li>"
                    "<li>🎯 <b>Release Gates</b> (Automated quality check)</li>"
                    "<li>💰 <b>Token Compressor</b> & File Analysis</li>"
                    "<li>🧠 <b>Session Memory</b> (Continue or Standalone)</li>"
                    "</ul>",
                    variant="default"
                )


if __name__ == "__main__":
    main()
