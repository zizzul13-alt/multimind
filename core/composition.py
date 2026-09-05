"""Presentation-independent composition for MultiMindApplication."""

from agents.cloudflare import CloudflareAgent
from agents.deepseek import DeepSeekAgent
from agents.gemini import GeminiAgent
from agents.groq import GroqAgent
from agents.huggingface import HuggingFaceAgent
from agents.openrouter import OpenRouterAgent
from agents.remote_agent import RemoteAgent
from agents.unified_agent import UnifiedAgent
from core.application import MultiMindApplication
from database.manager import DatabaseManager
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


def build_application_for_user(
    user_id,
    secrets_source=None,
    *,
    runtime_memories=None,
    runtime=None,
    db=None,
    agents=None,
    agents_factory=build_agents,
    database_factory=DatabaseManager,
):
    """Build one user-scoped application boundary for any presentation host."""
    user_id = Config.validate_user_id(user_id)

    if agents is None:
        api_keys = Config.get_api_keys(user_id, secrets_source=secrets_source)
        agents = agents_factory(api_keys)

    if db is None:
        db = database_factory(Config.get_db_path(user_id))

    return MultiMindApplication(
        agents=agents,
        runtime_memories=runtime_memories,
        runtime=runtime,
        db=db,
    )
