"""
Global configuration
"""
import os
import streamlit as st

class Config:
    """App configuration"""
    
    # App info
    APP_NAME = "MultiMind AI"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Multi-Agent AI Debate System"
    
    # Database paths
    DB_DIR = "data"
    
    # API settings
    API_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    
    # Token limits
    MAX_PROMPT_LENGTH = 5000
    MAX_CONTEXT_TOKENS = 800
    MAX_FILE_SIZE = 10_000_000  # 10MB
    
    # Rate limits (per user)
    RATE_LIMIT_MINUTE = 10
    RATE_LIMIT_HOUR = 100
    RATE_LIMIT_DAY = 500
    
    # Agent settings
    DEFAULT_AGENTS = ["deepseek", "gemini"]
    FALLBACK_AGENTS = ["gemini", "deepseek", "groq"]
    DEBATE_ROUNDS_MAX = 5
    DEBATE_ROUNDS_DEFAULT = 3
    
    # Compressor
    COMPRESSOR_ENABLED = True
    COMPRESSOR_MODEL = "gemini-flash"  # GRATIS
    
    # Memory
    MEMORY_SHORT_TERM_CHATS = 3
    MEMORY_LONG_TERM_MAX_TOKENS = 300
    
    @classmethod
    def get_api_keys(cls, user_id):
        """Get API keys for user"""
        try:
            return st.secrets[user_id]
        except:
            return {}
    
    @classmethod
    def get_db_path(cls, user_id):
        """Get database path for user"""
        os.makedirs(f"{cls.DB_DIR}/users", exist_ok=True)
        return f"{cls.DB_DIR}/users/{user_id}.db"
    
    @classmethod
    def get_pool_db_path(cls):
        """Get shared pool database path"""
        os.makedirs(f"{cls.DB_DIR}/shared", exist_ok=True)
        return f"{cls.DB_DIR}/shared/pool.db"