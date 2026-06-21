"""
MultiMind AI - Multi-Agent Debate System
Main Streamlit Application
"""
import streamlit as st
import uuid
import json
import os
from datetime import datetime

# Import custom modules
from agents.gemini import GeminiAgent
from agents.deepseek import DeepSeekAgent
from core.debate import DebateOrchestrator
from core.compressor import PromptCompressor
from core.memory import SessionMemory
from core.file_handler import FileHandler
from database.manager import DatabaseManager
from utils.token_counter import TokenCounter
from utils.error_handler import error_logger
from utils.config import Config

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# INITIALIZE SESSION STATE
# ============================================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.current_session = None
    st.session_state.sessions = {}
    st.session_state.memories = {}
    st.session_state.new_chat = False
    st.session_state.chat_mode = "continue"
    st.session_state.compressor_enabled = True
    st.session_state.debate_rounds = 3
    st.session_state.active_agents = ["deepseek", "gemini"]

# ============================================
# API AGENTS CACHE
# ============================================
@st.cache_resource
def get_agents(user_id):
    """Get AI agents for user"""
    api_keys = Config.get_api_keys(user_id)
    gemini = GeminiAgent(api_keys.get("gemini_key", "")) if api_keys.get("gemini_key") else None
    deepseek = DeepSeekAgent(api_keys.get("deepseek_key", "")) if api_keys.get("deepseek_key") else None
    return {"gemini": gemini, "deepseek": deepseek}

# ============================================
# DATABASE MANAGERS CACHE
# ============================================
@st.cache_resource
def get_db_manager(user_id):
    """Get database manager for user"""
    db_path = Config.get_db_path(user_id)
    return DatabaseManager(db_path)

# ============================================
# LOGIN PAGE
# ============================================
def show_login_page():
    """Show login page"""
    st.title("🤖 MultiMind AI")
    st.markdown("### Multi-Agent AI Debate System")
    st.divider()
    
    st.subheader("🔐 Silakan Login")
    
    username = st.text_input(
        "Username",
        placeholder="Ketik username bebas...",
        key="login_input"
    )
    
    if st.button("🚀 Masuk", type="primary", use_container_width=True):
        if username and username.strip():
            st.session_state.user = username.strip()
            st.session_state.user_id = username.strip().lower()
            st.rerun()
        else:
            st.error("Username tidak boleh kosong!")
    
    st.divider()
    st.info(
        "💡 **Info:**\n\n"
        "- Masukkan username bebas (Ali, Budi, atau nama lain)\n"
        "- Data kamu PRIVASI & terpisah dari user lain\n"
        "- API keys diatur oleh admin"
    )

# ============================================
# SIDEBAR
# ============================================
def show_sidebar():
    """Show sidebar for logged-in user"""
    with st.sidebar:
        st.title("🤖 MultiMind")
        st.success(f"👤 {st.session_state.user}")
        st.divider()
        
        # Session management
        st.subheader("📂 Sessions")
        
        db = get_db_manager(st.session_state.user_id)
        sessions = db.get_sessions()
        
        for s in sessions:
            if st.button(f"📝 {s['name']}", key=f"sess_{s['id']}"):
                st.session_state.current_session = s
                if s['id'] not in st.session_state.memories:
                    st.session_state.memories[s['id']] = SessionMemory()
                st.rerun()
        
        # New session
        with st.expander("➕ New Session"):
            new_name = st.text_input("Name", placeholder="Project API...")
            new_mode = st.selectbox("Mode", ["coding", "research", "thinking"])
            if st.button("Create", use_container_width=True):
                if new_name:
                    session_id = str(uuid.uuid4())
                    db.create_session(session_id, new_name, new_mode)
                    st.success("Created!")
                    st.rerun()
        
        st.divider()
        
        # Settings
        with st.expander("⚙️ Settings"):
            st.session_state.compressor_enabled = st.toggle("🗜️ Compressor", value=True)
            st.session_state.debate_rounds = st.slider("Debate Rounds", 1, 5, 3)
            st.session_state.active_agents = st.multiselect(
                "Agents",
                ["deepseek", "gemini"],
                default=["deepseek", "gemini"]
            )
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.user_id = None
            st.session_state.current_session = None
            st.rerun()

# ============================================
# SESSION VIEW
# ============================================
def show_session():
    """Show selected session"""
    session = st.session_state.current_session
    memory = st.session_state.memories.get(session['id'])
    
    st.title(f"💬 {session['name']}")
    st.caption(f"Mode: {session['mode']} | Created: {session['created_at'][:10]}")
    
    # Memory stats
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
    
    # Chat history
    db = get_db_manager(st.session_state.user_id)
    chats = db.get_session_chats(session['id'])
    
    for chat in chats:
        with st.chat_message("user"):
            mode_badge = "🧵" if chat.get('mode') == 'continue' else "📌"
            st.caption(f"{mode_badge} {chat.get('mode', 'continue').upper()}")
            st.write(chat['prompt'][:500])
        
        with st.chat_message("assistant"):
            st.write(chat.get('final_answer', 'No response')[:1000])
            
            if chat.get('debate_data'):
                with st.expander("🔍 Debate Details"):
                    try:
                        debate = json.loads(chat['debate_data'])
                        for i, r in enumerate(debate.get('responses', []), 1):
                            st.caption(f"Round {i} - {r.get('agent', 'Unknown')}")
                            st.write(r.get('text', '')[:500])
                    except:
                        pass
            
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"🔤 {chat.get('tokens_used', 0)} tokens")
            with col2:
                st.caption(f"💵 ${chat.get('cost', 0):.6f}")
    
    st.divider()
    
    # New chat button
    if st.button("➕ New Chat", type="primary", use_container_width=True):
        st.session_state.new_chat = True
        st.rerun()

# ============================================
# NEW CHAT FORM
# ============================================
def show_new_chat():
    """Show new chat form"""
    st.subheader("💭 New Chat")
    
    # Mode selection
    chat_mode = st.radio(
        "Chat Mode:",
        ["🧵 Continue (with history)", "📌 Standalone (fresh)"],
        horizontal=True
    )
    context_mode = "continue" if "Continue" in chat_mode else "standalone"
    
    if context_mode == "continue":
        st.info("AI will see previous chats in this session")
    else:
        st.success("AI starts fresh - no history (SAVES TOKENS!)")
    
    # Prompt
    prompt = st.text_area("Prompt:", height=150, placeholder="Ask anything...")
    
    # File upload
    uploaded_files = st.file_uploader(
        "📎 Files (optional)",
        accept_multiple_files=True,
        type=['txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html', 'css',
              'json', 'pdf', 'xlsx', 'xls', 'docx', 'jpg', 'png', 'jpeg', 'pptx']
    )
    
    # Token estimation
    if prompt or uploaded_files:
        files_count = len(uploaded_files) if uploaded_files else 0
        estimate = TokenCounter.estimate_total(
            prompt or "",
            files_count=files_count,
            mode=st.session_state.current_session.get('mode', 'coding'),
            rounds=st.session_state.debate_rounds,
            compressor_on=st.session_state.compressor_enabled
        )
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
            st.warning(f"🔴 {warning['icon']} High token usage! Consider compressor.")
        elif warning["level"] == "medium":
            st.info(f"🟡 {warning['icon']} Moderate token usage.")
    
    # Submit
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Send", type="primary", use_container_width=True):
            if prompt or uploaded_files:
                process_chat(prompt, uploaded_files, context_mode)
            else:
                st.error("Please enter a prompt or upload files")
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.new_chat = False
            st.rerun()

# ============================================
# PROCESS CHAT
# ============================================
def process_chat(prompt, uploaded_files, context_mode):
    """Process chat with debate"""
    agents = get_agents(st.session_state.user_id)
    gemini = agents.get("gemini")
    deepseek = agents.get("deepseek")
    
    if not gemini and not deepseek:
        st.error("No AI agents configured! Check API keys in secrets.")
        return
    
    with st.spinner("🤖 Agents debating..."):
        # Compress prompt
        final_prompt = prompt
        if st.session_state.compressor_enabled and gemini and prompt:
        try:
             compression = PromptCompressor.compress(prompt, gemini)
             final_prompt = compression.get("compressed", prompt)
        except:
             # Compressor error? Pakai original aja
             final_prompt = prompt
        pass

        
        # Process files
        file_context = ""
        if uploaded_files:
            file_results = FileHandler.handle(uploaded_files, gemini)
            for f in file_results.get("files", []):
                if "content" in f:
                    file_context += f"\n--- FILE: {f['filename']} ---\n{f['content']}\n"
        
        # Get context from memory
        context = ""
        if context_mode == "continue":
            memory = st.session_state.memories.get(st.session_state.current_session['id'])
            if memory:
                context = memory.get_context()
        
        if file_context:
            context = file_context + "\n" + context
        
        # Run debate
        orchestrator = DebateOrchestrator(gemini, deepseek)
        debate_result = orchestrator.debate(
            prompt=final_prompt,
            context=context[:3000],
            mode=st.session_state.current_session.get('mode', 'coding'),
            rounds=st.session_state.debate_rounds,
            agents=st.session_state.active_agents
        )
        
        # Save to memory
        memory = st.session_state.memories.get(st.session_state.current_session['id'])
        if not memory:
            memory = SessionMemory()
            st.session_state.memories[st.session_state.current_session['id']] = memory
        memory.add_chat(prompt, debate_result.get("final_answer", ""))
        
        # Save to database
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
        
        # Reset
        st.session_state.new_chat = False
        st.success("✅ Debate complete!")
        st.rerun()

# ============================================
# MAIN APP
# ============================================
def main():
    """Main application"""
    
    # Show login if not logged in
    if st.session_state.user is None:
        show_login_page()
    else:
        # Show sidebar
        show_sidebar()
        
        # Show main content
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
            2. Choose mode: **coding**, **research**, or **thinking**
            3. Start chatting with AI agents!
            
            ### Features:
            - 🤖 Multi-agent debate (DeepSeek + Gemini)
            - 💰 Token-efficient with compressor
            - 📎 File upload (PDF, Excel, Images, Code)
            - 🧠 Session memory (continue or standalone)
            - 👥 Multi-user with separate databases
            """)

if __name__ == "__main__":
    main()
