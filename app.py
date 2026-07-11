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
from agents.unified_agent import UnifiedAgent
from core.debate import DebateOrchestrator
from core.compressor import PromptCompressor
from core.memory import SessionMemory
from core.file_handler import FileHandler
from core.release_gate import ReleaseGate
from core.skills_manager import SkillsManager
from core.templates import TemplateManager
from database.manager import DatabaseManager
from utils.token_counter import TokenCounter
from utils.error_handler import error_logger
from utils.config import Config

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

@st.cache_resource
def get_agents(user_id):
    api_keys = Config.get_api_keys(user_id)
    
    # Unified Agent (prioritas utama)
    unified = UnifiedAgent(api_keys)
    
    return {
        "unified": unified,
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
    st.title("🤖 MultiMind AI")
    st.markdown("### Multi-Agent AI Debate System")
    st.divider()
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
    st.info("💡 **Info:**\n\n- Masukkan username bebas (Izzul, Miko, atau nama lain)\n- Data kamu PRIVASI & terpisah dari user lain\n- API keys diatur oleh admin")

def show_sidebar():
    with st.sidebar:
        st.title("🤖 MultiMind")
        st.success(f"👤 {st.session_state.user}")
        st.divider()
        st.subheader("📂 Sessions")
        db = get_db_manager(st.session_state.user_id)
        sessions = db.get_sessions()
        for i, s in enumerate(sessions):
            unique_key = f"sidebar_session_{i}_{s['id'][:8]}"
            if st.button(f"📝 {s['name']}", key=unique_key):
                st.session_state.current_session = s
                if s['id'] not in st.session_state.memories:
                    st.session_state.memories[s['id']] = SessionMemory()
                st.rerun()
        with st.expander("➕ New Session"):
            new_name = st.text_input("Name", placeholder="Project API...", key="sidebar_new_session_name")
            new_mode = st.selectbox("Mode", ["coding", "research", "thinking"], key="sidebar_new_session_mode")
            if st.button("Create", key="sidebar_create_session_btn", use_container_width=True):
                if new_name:
                    session_id = str(uuid.uuid4())
                    db.create_session(session_id, new_name, new_mode)
                    st.success("Created!")
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
    st.title(f"💬 {session['name']}")
    st.caption(f"Mode: {session['mode']} | Created: {session['created_at'][:10]}")
    if memory:
        stats = memory.get_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Context Tokens", stats["context_tokens"])
        with col2:
            st.metric("Short-term Chats", stats["short_term_chats"])
        with col3:
            st.metric("Free Space", f"{stats['free_percent']}%")
    st.divider()
    db = get_db_manager(st.session_state.user_id)
    chats = db.get_session_chats(session['id'])
    for chat in chats:
        with st.chat_message("user"):
            mode_badge = "🧵" if chat.get('mode') == 'continue' else "📌"
            st.caption(f"{mode_badge} {chat.get('mode', 'continue').upper()}")
            st.write(chat['prompt'])
        with st.chat_message("assistant"):
            st.markdown(chat.get('final_answer', 'No response'))
            if chat.get('debate_data'):
                with st.expander("🔍 Debate Details"):
                    try:
                        debate = json.loads(chat['debate_data'])
                        gate_score = debate.get('gate_score')
                        if gate_score is not None:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.caption(f"🎯 Gate Score: {gate_score}/10")
                            with col2:
                                st.caption(f"{ReleaseGate.get_badge(gate_score)}")
                            st.divider()
                        responses = debate.get('responses', [])
                        if responses:
                            for i, r in enumerate(responses, 1):
                                agent = r.get('agent', 'Unknown')
                                text = r.get('text', '')
                                status = r.get('status', 'unknown')
                                if status == "success":
                                    st.success(f"✅ Round {i} - {agent}")
                                elif status == "error":
                                    st.error(f"❌ Round {i} - {agent}")
                                else:
                                    st.warning(f"⚠️ Round {i} - {agent}")
                                if text:
                                    st.markdown(text)
                                else:
                                    st.caption(f"(Status: {status})")
                        else:
                            st.caption("No debate data available")
                    except:
                        st.caption("Error loading debate details")
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"🔤 {chat.get('tokens_used', 0)} tokens")
            with col2:
                st.caption(f"💵 ${chat.get('cost', 0):.6f}")
    st.divider()
    if st.button("➕ New Chat", type="primary", key="new_chat_btn", use_container_width=True):
        st.session_state.new_chat = True
        st.rerun()

def show_new_chat():
    st.subheader("💭 New Chat")
    default_prompt = ""
    
    # Setup state tracker agar tidak menimpa ketikan manual user
    if "last_generated" not in st.session_state:
        st.session_state.last_generated = ""
    
    # ===== TEMPLATE SELECTOR =====
    templates_mgr = get_template_manager()
    template_list = [("", "No Template")] + templates_mgr.get_template_names()
    
    selected_template = st.selectbox(
        "📋 Template (optional)",
        [t[0] for t in template_list],
        format_func=lambda x: dict(template_list)[x] if x != "" else "No Template",
        key="template_selector",
        help="Pilih template untuk quick prompt"
    )
    
    # Template variables
    if selected_template and selected_template != "":
        template = templates_mgr.get_template(selected_template)
        if template:
            st.caption(f"📝 {template['description']}")
            
            # Deteksi variabel {{var}}
            import re
            variables = re.findall(r'\{\{(\w+)\}\}', template['prompt'])
            if variables:
                st.caption("🔧 Isi variabel:")
                vars_dict = {}
                cols = st.columns(min(len(variables), 3))
                for i, var in enumerate(variables):
                    with cols[i % 3]:
                        # Gunakan key spesifik per template agar tidak tabrakan
                        vars_dict[var] = st.text_input(f"{var}", key=f"var_{var}_{selected_template}")
                st.session_state.template_variables = vars_dict
            
            # Auto-update prompt
            result = templates_mgr.apply_template(
                selected_template,
                st.session_state.get("template_variables", {})
            )
            
            if result:
                new_prompt = result["prompt"]
                default_prompt = new_prompt # Perbaikan 1: Update default_prompt agar preview muncul
                
                # Perbaikan 2 & 3: Hanya inject ke text_area jika template/variabel benar-benar berubah
                if new_prompt != st.session_state.last_generated:
                    st.session_state.prompt_main = new_prompt
                    st.session_state.last_generated = new_prompt
    
    # ===== SHOW TEMPLATE PREVIEW =====
    if selected_template and selected_template != "" and default_prompt:
        st.info(f"📋 **Template Preview:**\n\n{default_prompt}")
        st.caption("👆 Prompt otomatis masuk ke kolom di bawah, bisa langsung diedit.")
    
    # ===== CHAT MODE =====
    chat_mode = st.radio("Chat Mode:", ["🧵 Continue (with history)", "📌 Standalone (fresh)"], horizontal=True, key="chat_mode_radio")
    context_mode = "continue" if "Continue" in chat_mode else "standalone"
    if context_mode == "continue":
        st.info("AI will see previous chats in this session")
    else:
        st.success("AI starts fresh - no history (SAVES TOKENS!)")

    # ===== PROMPT =====
    # Streamlit otomatis membaca dan menulis ke st.session_state.prompt_main melalui key ini
    prompt = st.text_area("Prompt:", height=150, placeholder="Paste template atau tulis bebas...", key="prompt_main")
    # ===== FILE UPLOAD =====
    uploaded_files = st.file_uploader(
        "📎 Files (optional)",
        accept_multiple_files=True,
        type=['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css', 'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx'],
        key="new_chat_files"
    )
    
    # ===== TOKEN ESTIMATION =====
    if prompt or uploaded_files:
        files_count = len(uploaded_files) if uploaded_files else 0
        session_mode = st.session_state.current_session.get('mode', 'coding') if st.session_state.current_session else 'coding'
        estimate = TokenCounter.estimate_total(prompt or "", files_count=files_count, mode=session_mode, rounds=st.session_state.debate_rounds, compressor_on=st.session_state.compressor_enabled)
        warning = TokenCounter.get_warning_level(estimate["total_estimate"])
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📝 Prompt", estimate["prompt_tokens"])
        with col2:
            st.metric("📎 Files", estimate["file_tokens"])
        with col3:
            st.metric("📊 Est. Total", estimate["total_estimate"])
        with col4:
            cost = TokenCounter.estimate_cost(estimate["total_estimate"])
            st.metric("💵 Est. Cost", f"${cost:.6f}")
        if warning["level"] == "high":
            st.warning(f"🔴 High token usage! Consider compressor.")
        elif warning["level"] == "medium":
            st.info(f"🟡 Moderate token usage.")
    
    # ===== SUBMIT =====
    col1, col2 = st.columns(2)
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
    gemini = agents.get("gemini")
    deepseek = agents.get("deepseek")
    groq = agents.get("groq")
    cloudflare = agents.get("cloudflare")
    openrouter = agents.get("openrouter")
    huggingface = agents.get("huggingface")

    with st.spinner("🤖 Agents debating..."):
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
            # Unified Agent (auto-failover semua)
            response = unified.generate(
                prompt=final_prompt,
                system_prompt=None,
                mode=session_mode
            )
            debate_result = {
                "responses": [response],
                "final_answer": response.get("text", ""),
                "total_tokens": response.get("tokens", 0),
                "total_cost": response.get("cost", 0),
                "status": response.get("status", "error")
            }
        else:
            # Agent individual (debate biasa)
            orchestrator = DebateOrchestrator(
                gemini_agent=gemini,
                deepseek_agent=deepseek,
                groq_agent=groq,
                cloudflare_agent=cloudflare,
                openrouter_agent=openrouter,
                huggingface_agent=huggingface
            )
            debate_result = orchestrator.debate(
                prompt=final_prompt,
                context=context[:3000],
                mode=session_mode,
                rounds=st.session_state.debate_rounds,
                agents=active,
                skill=st.session_state.get("selected_skill", "default")
            )

        # ===== SAVE TO MEMORY =====
        if st.session_state.current_session:
            memory = st.session_state.memories.get(st.session_state.current_session['id'])
            if not memory:
                memory = SessionMemory()
                st.session_state.memories[st.session_state.current_session['id']] = memory
            memory.add_chat(prompt, debate_result.get("final_answer", ""))

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
            db.save_chat(st.session_state.current_session['id'], chat_data)

        st.session_state.new_chat = False
        st.success("✅ Debate complete!")
        st.rerun()
        
def main():
    if st.session_state.user:
        with st.sidebar:
            with st.expander("🔧 Debug Info"):
                st.write("User:", st.session_state.user_id)
                agents = get_agents(st.session_state.user_id)
                st.write("Gemini:", "✅" if agents.get("gemini") else "❌")
                st.write("DeepSeek:", "✅" if agents.get("deepseek") else "❌")
                st.write("Groq:", "✅" if agents.get("groq") else "❌")
                st.write("Cloudflare:", "✅" if agents.get("cloudflare") else "❌")
                st.write("OpenRouter:", "✅" if agents.get("openrouter") else "❌")
                st.write("HuggingFace:", "✅" if agents.get("huggingface") else "❌")
    if st.session_state.user is None:
        show_login_page()
    else:
        show_sidebar()
        if st.session_state.current_session:
            if st.session_state.new_chat:
                show_new_chat()
            else:
                show_session()
        else:
            st.title("🤖 Welcome, " + st.session_state.user + "!")
            st.info("👈 Select or create a session in the sidebar to start")
            st.markdown("""
            ### Getting Started:
            1. Create a **New Session** in the sidebar
            2. Pick a **Template** (optional) for quick prompts
            3. Choose a **Skill** for agent behavior
            4. Select mode: **coding**, **research**, or **thinking**
            5. Start chatting with AI agents!

            ### Features:
            - 🤖 6 AI Agents (Gemini, Groq, Cloudflare, OpenRouter, HuggingFace, DeepSeek)
            - 📋 Prompt Templates (Debug, Research, Design, etc)
            - 🎯 Skills System (Code Reviewer, Researcher, Thinker)
            - 🎯 Release Gates (Quality check otomatis)
            - 💰 Token-efficient with compressor
            - 📎 File upload (PDF, Excel, Images, Code)
            - 🧠 Session memory (continue or standalone)
            - 👥 Multi-user with separate databases
            """)

if __name__ == "__main__":
    main()
