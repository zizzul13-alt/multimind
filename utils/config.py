"""
Global configuration
"""
import os
import re
from pathlib import Path


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

    EMPTY_API_KEYS = {
        "gemini_key": "",
        "deepseek_key": "",
        "groq_key": "",
        "cloudflare_key": "",
        "cloudflare_account_id": "",
        "openrouter_key": "",
        "huggingface_key": "",
    }

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
    def resolve_supplied_identity(cls, username):
        """Trim harmless UI whitespace, then validate the storage identity."""
        if not isinstance(username, str):
            raise InvalidUserIdError("User ID must be a string.")

        display_username = username.strip()
        if not display_username:
            raise InvalidUserIdError("Username tidak boleh kosong!")
        return display_username, cls.validate_user_id(display_username)

    @classmethod
    def get_api_keys(cls, user_id, secrets_source=None):
        """Resolve per-user/default API settings from a plain mapping or callable."""
        user_id = cls.validate_user_id(user_id)
        if secrets_source is None:
            return dict(cls.EMPTY_API_KEYS)

        try:
            source = secrets_source() if callable(secrets_source) else secrets_source
            all_secrets = dict(source or {})
            selected = all_secrets.get(user_id)
            if selected is None:
                selected = all_secrets.get("default")
            if selected is not None:
                return dict(selected)
        except Exception:
            pass

        return dict(cls.EMPTY_API_KEYS)

    @classmethod
    def get_db_path(cls, user_id):
        """Resolve a validated user's SQLite database within the user DB root."""
        user_id = cls.validate_user_id(user_id)
        users_root = (Path(cls.DB_DIR) / "users").resolve()
        users_root.mkdir(parents=True, exist_ok=True)
        candidate = (users_root / f"{user_id}.db").resolve()

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
