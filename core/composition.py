"""Presentation-independent composition for MultiMindApplication."""

import os

from agents.cloudflare import CloudflareAgent
from agents.deepseek import DeepSeekAgent
from agents.gemini import GeminiAgent
from agents.groq import GroqAgent
from agents.huggingface import HuggingFaceAgent
from agents.openrouter import OpenRouterAgent
from agents.remote_agent import RemoteAgent
from agents.unified_agent import UnifiedAgent
from core.application import MultiMindApplication
from core.compressor import PromptCompressor
from core.debate import DebateOrchestrator
from core.file_handler import FileHandler
from core.memory import persist_chat_and_update_memory
from database.manager import DatabaseManager
from database.turso_manager import TursoDatabaseManager
from utils.config import Config


def build_agents(api_keys):
    """Construct the existing provider set without presentation dependencies."""
    unified = UnifiedAgent(api_keys)
    remote_url = api_keys.get("remote_url", "")
    remote = RemoteAgent(remote_url) if remote_url else None

    return {
        "unified": unified,
        "remote": remote,
        "gemini": GeminiAgent(api_keys.get("gemini_key", "")) if api_keys.get("gemini_key") else None,
        "deepseek": DeepSeekAgent(api_keys.get("deepseek_key", "")) if api_keys.get("deepseek_key") else None,
        "groq": GroqAgent(api_keys.get("groq_key", "")) if api_keys.get("groq_key") else None,
        "cloudflare": CloudflareAgent(
            api_keys.get("cloudflare_key", ""),
            api_keys.get("cloudflare_account_id", ""),
        ) if api_keys.get("cloudflare_key") else None,
        "openrouter": OpenRouterAgent(api_keys.get("openrouter_key", "")) if api_keys.get("openrouter_key") else None,
        "huggingface": HuggingFaceAgent(api_keys.get("huggingface_key", "")) if api_keys.get("huggingface_key") else None,
    }


def build_database_for_user(
    user_id,
    database_factory=DatabaseManager,
    *,
    environ=None,
    turso_factory=TursoDatabaseManager,
):
    """Construct validated user-scoped persistence.

    An explicit non-default ``database_factory`` remains authoritative for tests
    and bounded host seams. Otherwise SQLite is the zero-config fallback, while
    supplying both Turso runtime credentials selects remote durable persistence.
    Supplying only one Turso credential fails closed so an incomplete production
    configuration cannot silently fall back to ephemeral SQLite.
    """
    user_id = Config.validate_user_id(user_id)

    if database_factory is not DatabaseManager:
        return database_factory(Config.get_db_path(user_id))

    environ = os.environ if environ is None else environ
    turso_url = environ.get("TURSO_DATABASE_URL", "").strip()
    turso_token = environ.get("TURSO_AUTH_TOKEN", "").strip()

    if bool(turso_url) != bool(turso_token):
        raise RuntimeError(
            "TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must be configured together."
        )
    if turso_url and turso_token:
        return turso_factory(turso_url, turso_token, user_id)

    return database_factory(Config.get_db_path(user_id))


def build_application_for_user(
    user_id,
    secrets_source=None,
    *,
    runtime_memories=None,
    runtime=None,
    db=None,
    db_factory=None,
    agents=None,
    agents_factory=build_agents,
    database_factory=DatabaseManager,
    compressor=PromptCompressor,
    file_handler=FileHandler,
    debate_factory=DebateOrchestrator,
    persist_chat=persist_chat_and_update_memory,
):
    """Build one user-scoped application boundary for any presentation host.

    Generic callers get a concrete validated database by default. Hosts may
    supply a lazy ``db_factory`` when they need to preserve an existing
    lifecycle/cache seam; the application remains the only consumer of it.
    """
    user_id = Config.validate_user_id(user_id)

    if agents is None:
        api_keys = Config.get_api_keys(user_id, secrets_source=secrets_source)
        agents = agents_factory(api_keys)

    if db is None and db_factory is None:
        db = build_database_for_user(user_id, database_factory=database_factory)

    return MultiMindApplication(
        agents=agents,
        runtime_memories=runtime_memories,
        runtime=runtime,
        db=db,
        db_factory=db_factory,
        compressor=compressor,
        file_handler=file_handler,
        debate_factory=debate_factory,
        persist_chat=persist_chat,
    )
