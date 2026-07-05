"""
Global configuration
"""
import os
import streamlit as st

class Config:
    """App configuration"""
    
    APP_NAME = "MultiMind AI"
    APP_VERSION = "1.0.0"
    DB_DIR = "data"
    
    API_TIMEOUT = 30
    MAX_RETRIES = 3
    MAX_PROMPT_LENGTH = 5000
    MAX_CONTEXT_TOKENS = 800
    
    DEFAULT_AGENTS = ["gemini"]
    FALLBACK_AGENTS = ["gemini", "groq"]
    DEBATE_ROUNDS_DEFAULT = 1
    
    COMPRESSOR_ENABLED = False
    COMPRESSOR_MODEL = "gemini-flash-latest"
    
    @classmethod
    def get_api_keys(cls, user_id):
        """Get API keys for user"""
        try:
            all_secrets = dict(st.secrets)
            
            if user_id in all_secrets:
                return dict(st.secrets[user_id])
            
            if "default" in all_secrets:
                return dict(st.secrets["default"])
            
        except Exception:
            pass
        
        return {"gemini_key": "", "deepseek_key": "", "groq_key": ""}
    
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
