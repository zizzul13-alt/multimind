"""
Global configuration
"""
import os
import re
from pathlib import Path
import streamlit as st


class InvalidUserIdError(ValueError):
    """Raised when a supplied identity cannot safely name a user namespace."""


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
    FALLBACK_AGENTS = ["gemini", "groq", "cloudflare", "openrouter", "huggingface"]
    DEBATE_ROUNDS_DEFAULT = 1
    
    COMPRESSOR_ENABLED = False
    COMPRESSOR_MODEL = "gemini-flash-latest"

    # User IDs form a storage namespace.  Keep this deliberately smaller than
    # arbitrary display text so an ID can never be interpreted as a path.
    USER_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

    @classmethod
    def validate_user_id(cls, user_id):
        """Return the canonical ID or fail closed without path sanitisation."""
        if not isinstance(user_id, str):
            raise InvalidUserIdError("User ID must be a string.")

        canonical_user_id = user_id.lower()
        if (
            not cls.USER_ID_PATTERN.fullmatch(canonical_user_id)
            or ".." in canonical_user_id
        ):
            raise InvalidUserIdError(
                "User ID must use 1-64 letters, numbers, dots, hyphens, or "
                "underscores; path-like values are not allowed."
            )
        return canonical_user_id
    
    @classmethod
    def get_api_keys(cls, user_id):
        """Get API keys for user"""
        user_id = cls.validate_user_id(user_id)
        try:
            all_secrets = dict(st.secrets)
            
            if user_id in all_secrets:
                return dict(st.secrets[user_id])
            
            if "default" in all_secrets:
                return dict(st.secrets["default"])
            
        except Exception:
            pass
        
        return {
            "gemini_key": "",
            "deepseek_key": "",
            "groq_key": "",
            "cloudflare_key": "",
            "cloudflare_account_id": "",
            "openrouter_key": "",
            "huggingface_key": ""
        }
    
    @classmethod
    def get_db_path(cls, user_id):
        """Resolve a validated user's SQLite database within the user DB root."""
        user_id = cls.validate_user_id(user_id)
        users_root = (Path(cls.DB_DIR) / "users").resolve()
        users_root.mkdir(parents=True, exist_ok=True)
        candidate = (users_root / f"{user_id}.db").resolve()

        # Validation is necessary but not sufficient: preserve this canonical
        # containment check at the resolver boundary for all callers.
        try:
            candidate.relative_to(users_root)
        except ValueError as exc:
            raise InvalidUserIdError("User database path escapes the user DB root.") from exc

        return str(candidate)
    
    @classmethod
    def get_pool_db_path(cls):
        """Get shared pool database path"""
        os.makedirs(f"{cls.DB_DIR}/shared", exist_ok=True)
        return f"{cls.DB_DIR}/shared/pool.db"
