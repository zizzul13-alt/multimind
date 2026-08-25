"""
MultiMind AI - Multi-Agent Debate System
Main Streamlit Application
"""
import streamlit as st
import uuid
import json
import os
from datetime import datetime

from agents.gemini import GeminiAgent
from agents.deepseek import DeepSeekAgent
from agents.groq import GroqAgent
from agents.cloudflare import CloudflareAgent
from agents.openrouter import OpenRouterAgent
from agents.huggingface import HuggingFaceAgent
from agents.remote_agent import RemoteAgent
from agents.unified_agent import UnifiedAgent
from core.debate import DebateOrchestrator
from core.compressor import PromptCompressor
from core.memory import get_or_hydrate_session_memory, persist_chat_and_update_memory
from core.file_handler import FileHandler
from core.release_gate import ReleaseGate
from core.skills_manager import SkillsManager
from core.templates import TemplateManager
from database.manager import DatabaseManager
from utils.token_counter import TokenCounter
from utils.error_handler import error_logger
from utils.config import Config
from ui.foundation import load_css, render_status_badge, card_container
from ui.presentation import build_presentation_snapshot, render_archetype, list_archetypes, render_brand_identity
from ui.dna.bootstrap import ensure_proof_dna_and_themes_registered
from ui.themes import list_themes
from ui.theme_studio.surface import render_theme_studio_surface

# Ensure S6.2 proof Design DNA and themes are registered prior to runtime selector
ensure_proof_dna_and_themes_registered()

st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.current_session = None
    st.session_state.sessions = {}
    st.session_state.memories = {}
    st.session_state.new_chat = False
    st.session_state.chat_mode = "continue"
    st.session_state.compressor_enabled = False
    st.session_state.debate_rounds = 1
    st.session_state.active_agents = ["gemini"]
    st.session_state.selected_skill = "default"
    st.session_state.selected_template = None
    st.session_state.template_variables = {}
    st.session_state.prompt_text = ""

if "active_navigation" not in st.session_state:
    st.session_state.active_navigation = "workspace"

if "active_theme" not in st.session_state:
    qp_theme = st.query_params.get("theme", None)
    st.session_state.active_theme = qp_theme if qp_theme else "default"
else:
    qp_theme = st.query_params.get("theme", None)
    if qp_theme and isinstance(qp_theme, str) and qp_theme != st.session_state.active_theme:
        st.session_state.active_theme = qp_theme

if "active_archetype" not in st.session_state:
    qp_arch = st.query_params.get("archetype", None)
    if qp_arch and isinstance(qp_arch, str):
        from ui.presentation.resolver import CANONICAL_ARCHETYPE_IDS, FALLBACK_ARCHETYPE_ID
        st.session_state.active_archetype = qp_arch if qp_arch in CANONICAL_ARCHETYPE_IDS else FALLBACK_ARCHETYPE_ID
    else:
        st.session_state.active_archetype = "chat_first"

load_css(st.session_state.get("active_theme", "default"))

@st.cache_resource
def get_agents(user_id):
    api_keys = Config.get_api_keys(user_id)
    
    # Unified Agent (prioritas utama)
    unified = UnifiedAgent(api_keys)
    
    # Remote Agent (PythonAnywhere)
    remote_url = api_keys.get("remote_url", "")
    remote = RemoteAgent(remote_url) if remote_url else None
    
    return {
        "unified": unified,
        "remote": remote,
        "gemini": GeminiAgent(api_keys.get("gemini_key", "")) if api_keys.get("gemini_key") else None,
        "deepseek": DeepSeekAgent(api_keys.get("deepseek_key", "")) if api_keys.get("deepseek_key") else None,
        "groq": GroqAgent(api_keys.get("groq_key", "")) if api_keys.get("groq_key") else None,
        "cloudflare": CloudflareAgent(api_keys.get("cloudflare_key", ""), api_keys.get("cloudflare_account_id", "")) if api_keys.get("cloudflare_key") else None,
        "openrouter": OpenRouterAgent(api_keys.get("openrouter_key", "")) if api_keys.get("openrouter_key") else None,
        "huggingface": HuggingFaceAgent(api_keys.get("huggingface_key", "")) if api_keys.get("huggingface_key") else None,
    }

def get_db_manager(user_id):
    db_path = Config.get_db_path(user_id)
    return DatabaseManager(db_path)

@st.cache_resource
def get_skills_manager():
    return SkillsManager()

@st.cache_resource
def get_template_manager():
    return TemplateManager()

def show_login_page():
    card_container(
        "<div class='mm-typo-display'>🤖 MultiMind AI</div>"
        "<div class='mm-typo-subheading mm-text-muted'>Multi-Agent AI Debate System</div>",
        variant="elevated"
    )
    st.subheader("🔐 Silakan Login")
    username = st.text_input("Username", placeholder="Ketik username bebas...", key="login_username_input")
    if st.button("🚀 Masuk", type="primary", key="login_button"):
        if username and username.strip():
            st.session_state.user = username.strip()
            st.session_state.user_id = username.strip().lower()
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

        # Main Navigation Surface Selector
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

        db = get_db_manager(st.session_state.user_id)

        # Prominent New Session creation control at the top
        with st.expander("➕ New Session", expanded=False):
            new_name = st.text_input("Name", placeholder="Project API...", key="sidebar_new_session_name")
            new_mode = st.selectbox("Mode", ["coding", "research", "thinking"], key="sidebar_new_session_mode")
            if st.button("Create", key="sidebar_create_session_btn", use_container_width=True):
                if new_name:
                    session_id = str(uuid.uuid4())
                    db.create_session(session_id, new_name, new_mode)
                    st.success("Created!")
                    st.rerun()

        st.caption("📂 SESSIONS")
        sessions = db.get_sessions()
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
                get_or_hydrate_session_memory(st.session_state.memories, db, s['id'])
                # Switch to workspace view when selecting a session
                st.session_state.active_navigation = "workspace"
                st.rerun()

        st.divider()
        
        # ===== SETTINGS =====
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
            
            # Skill Selector
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
            
            # Agent Selector
            st.session_state.active_agents = st.multiselect(
                "Agents",
                ["unified", "remote", "cloudflare", "groq", "gemini", "openrouter", "huggingface", "deepseek"],
                default=st.session_state.active_agents,
                key="settings_agents"
            )

            # Theme Selector
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

            # Archetype Projection Selector (S7.5 Composition Resolver)
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
       
        # ===== BACKUP/RESTORE =====
        with st.expander("💾 Backup & Restore"):
            st.caption("Database SQLite")
            
            db_path = Config.get_db_path(st.session_state.user_id)
            
            # Download backup
            if os.path.exists(db_path):
                with open(db_path, "rb") as f:
                    st.download_button(
                        "📥 Download Backup",
                        f,
                        file_name=f"multimind_backup_{datetime.now():%Y%m%d}.db",
                        mime="application/octet-stream",
                        key="download_db_btn",
                        use_container_width=True
                    )
            
            # Upload restore
            uploaded_db = st.file_uploader("📤 Restore Backup", type=["db"], key="restore_db_uploader")
            if uploaded_db:
                if st.button("🔄 Restore", key="restore_db_btn", use_container_width=True):
                    with open(db_path, "wb") as f:
                        f.write(uploaded_db.read())
                    st.success("✅ Database restored! Refresh page.")
                    st.rerun()
        
        st.divider()
        if st.button("🚪 Logout", key="sidebar_logout_btn", use_container_width=True):
            st.session_state.user = None
            st.session_state.user_id = None
            st.session_state.current_session = None
            st.rerun()

def show_session():
    session = st.session_state.current_session
    memory = st.session_state.memories.get(session['id'])
    db = get_db_manager(st.session_state.user_id)
    chats = db.get_session_chats(session['id'])

    snapshot = build_presentation_snapshot(session, chats, memory)

    active_archetype = st.session_state.get("active_archetype", "chat_first")
    render_archetype(active_archetype, snapshot)

def show_new_chat():
    st.markdown("<div class='mm-typo-heading' style='margin-bottom: var(--mm-space-md);'>💭 New Chat</div>", unsafe_allow_html=True)
    default_prompt = ""
    
    # Setup state tracker agar tidak menimpa ketikan manual user
    if "last_generated" not in st.session_state:
        st.session_state.last_generated = ""
    
    # ===== CONTROLS ROW: TEMPLATE & MODE =====
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

    # Template variables
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
    
    # ===== SHOW TEMPLATE PREVIEW =====
    if selected_template and selected_template != "" and default_prompt:
        card_container(
            f"<div class='mm-typo-label'>📋 Template Preview:</div>"
            f"<pre class='mm-typo-mono'>{default_prompt}</pre>"
            f"<div class='mm-typo-caption mm-text-muted'>👆 Prompt otomatis masuk ke kolom di bawah, bisa langsung diedit.</div>",
            variant="muted"
        )

    # ===== PROMPT =====
    prompt = st.text_area("Prompt:", height=150, placeholder="Paste template atau tulis bebas...", key="prompt_main")

    # ===== FILE UPLOAD =====
    uploaded_files = st.file_uploader(
        "📎 Files (optional)",
        accept_multiple_files=True,
        type=['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css', 'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx'],
        key="new_chat_files"
    )
    
    # ===== TOKEN ESTIMATION METRICS =====
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
    
    # ===== ACTION BUTTONS =====
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
    agents = get_agents(st.session_state.user_id)
    unified = agents.get("unified")
    remote = agents.get("remote")
    gemini = agents.get("gemini")
    deepseek = agents.get("deepseek")
    groq = agents.get("groq")
    cloudflare = agents.get("cloudflare")
    openrouter = agents.get("openrouter")
    huggingface = agents.get("huggingface")

    final_prompt = prompt
    if st.session_state.compressor_enabled and gemini and prompt:
        try:
            compression = PromptCompressor.compress(prompt, gemini)
            final_prompt = compression["compressed"]
        except:
            final_prompt = prompt

    file_context = ""
    if uploaded_files:
        try:
            file_results = FileHandler.handle(uploaded_files, gemini)
            for f in file_results.get("files", []):
                if "content" in f:
                    file_context += f"\n--- FILE: {f['filename']} ---\n{f['content']}\n"
        except:
            pass

    context = ""
    if context_mode == "continue" and st.session_state.current_session:
        memory = st.session_state.memories.get(st.session_state.current_session['id'])
        if memory:
            context = memory.get_context()
    if file_context:
        context = file_context + "\n" + context

    session_mode = st.session_state.current_session.get('mode', 'coding') if st.session_state.current_session else 'coding'
    active = st.session_state.active_agents

    # ===== AGENT ROUTING =====
    if "unified" in active:
        response = unified.generate(prompt=final_prompt, system_prompt=None, mode=session_mode)
        debate_result = {
            "responses": [response],
            "final_answer": response.get("text", ""),
            "total_tokens": response.get("tokens", 0),
            "total_cost": response.get("cost", 0),
            "status": response.get("status", "error")
        }
    elif "remote" in active:
        response = remote.generate(prompt=final_prompt, system_prompt=None, mode=session_mode)
        debate_result = {
            "responses": [response],
            "final_answer": response.get("text", ""),
            "total_tokens": response.get("tokens", 0),
            "total_cost": response.get("cost", 0),
            "status": response.get("status", "error")
        }
    else:
        orchestrator = DebateOrchestrator(
            gemini_agent=gemini, deepseek_agent=deepseek, groq_agent=groq,
            cloudflare_agent=cloudflare, openrouter_agent=openrouter,
            huggingface_agent=huggingface
        )
        debate_result = orchestrator.debate(
            prompt=final_prompt, context=context[:3000], mode=session_mode,
            rounds=st.session_state.debate_rounds, agents=active,
            skill=st.session_state.get("selected_skill", "default")
        )

    # ===== SAVE TO DATABASE =====
    if st.session_state.current_session:
        db = get_db_manager(st.session_state.user_id)
        chat_data = {
            "id": str(uuid.uuid4()),
            "prompt": prompt,
            "prompt_compressed": json.dumps({"compressed": final_prompt}) if final_prompt != prompt else "",
            "mode": context_mode,
            "context_mode": context_mode,
            "final_answer": debate_result.get("final_answer", ""),
            "debate_data": json.dumps(debate_result),
            "tokens_used": debate_result.get("total_tokens", 0),
            "cost": debate_result.get("total_cost", 0)
        }
        persist_chat_and_update_memory(
            db,
            st.session_state.current_session['id'],
            st.session_state.memories,
            chat_data
        )

    st.session_state.new_chat = False
    st.success("✅ Debate complete!")
    st.rerun()

def main():
    if st.session_state.user:
        with st.sidebar:
            with st.expander("🔧 Debug Info"):
                st.write("User:", st.session_state.user_id)
                agents = get_agents(st.session_state.user_id)
                
                unified = agents.get("unified")

                # Unified Agent Stats
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

                # S7.1 Dev Spike Integration
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
            render_theme_studio_surface()
        elif st.session_state.current_session:
            session = st.session_state.current_session
            memory = st.session_state.memories.get(session['id'])
            db = get_db_manager(st.session_state.user_id)
            chats = db.get_session_chats(session['id'])

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
