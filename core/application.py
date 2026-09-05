"""Frontend-independent application operations for MultiMind chat sessions."""
from dataclasses import dataclass, field
import json
import uuid

from agents.router import TERMINAL_PROVIDER_FAILURE_TEXT
from core.compressor import PromptCompressor
from core.debate import DebateOrchestrator
from core.file_handler import FileHandler
from core.memory import get_or_hydrate_session_memory, persist_chat_and_update_memory
from database.manager import RestoreOperationError, RestoreValidationError
from providers.base import BaseProvider
from utils.error_handler import error_logger


@dataclass
class ChatRequest:
    original_prompt: str
    uploads: list = field(default_factory=list)
    context_mode: str = "continue"
    session_id: str | None = None
    session_mode: str = "coding"
    compressor_enabled: bool = False
    active_agents: list = field(default_factory=list)
    debate_rounds: int = 1
    selected_skill: str = "default"


@dataclass
class ChatResult:
    status: str
    final_answer: str = ""
    debate_data: dict = field(default_factory=dict)
    tokens: int = 0
    cost: float = 0.0
    warnings: list[str] = field(default_factory=list)
    persisted: bool = False


@dataclass
class ApplicationRuntime:
    """Plain runtime state derived from the active user database."""
    current_session: object = None
    memories: dict = field(default_factory=dict)

    def invalidate_database_derived_state(self):
        self.current_session = None
        self.memories.clear()


@dataclass
class RestoreResult:
    status: str
    runtime_invalidated: bool = False


class MultiMindApplication:
    """Plain-Python seam for chat execution and session lifecycle."""

    def __init__(
        self, agents=None, runtime_memories=None, runtime=None, db=None, db_factory=None,
        compressor=PromptCompressor, file_handler=FileHandler,
        debate_factory=DebateOrchestrator,
        persist_chat=persist_chat_and_update_memory,
    ):
        self.agents = agents or {}
        self.runtime = runtime
        self.runtime_memories = (
            runtime.memories if runtime is not None
            else (runtime_memories if runtime_memories is not None else {})
        )
        self.db = db
        self.db_factory = db_factory
        self.compressor = compressor
        self.file_handler = file_handler
        self.debate_factory = debate_factory
        self.persist_chat = persist_chat

    def _database(self):
        if self.db is not None:
            return self.db
        if self.db_factory is None:
            raise RuntimeError("A database or database factory is required for persistence.")
        return self.db_factory()

    def create_session(self, name, mode="coding"):
        session_id = str(uuid.uuid4())
        self._database().create_session(session_id, name, mode)
        return session_id

    def list_sessions(self):
        """Return persisted sessions without mutating runtime memory."""
        return self._database().get_sessions()

    def get_session_chats(self, session_id, limit=50):
        """Return persisted chats without hydrating or mutating session memory."""
        return self._database().get_session_chats(session_id, limit=limit)

    def export_database(self):
        """Return an exportable snapshot through the persistence boundary."""
        return self._database().export_bytes()

    def select_session(self, session):
        """Hydrate the supplied persisted session into this runtime's memory."""
        get_or_hydrate_session_memory(self.runtime_memories, self._database(), session["id"])
        return session

    def restore_database(self, backup_bytes, runtime=None):
        """Restore a database and invalidate any runtime state derived from it."""
        active_runtime = runtime or self.runtime
        if active_runtime is None:
            active_runtime = ApplicationRuntime(memories=self.runtime_memories)

        try:
            self._database().restore_from_bytes(backup_bytes)
        except RestoreValidationError:
            return RestoreResult(status="invalid_backup")
        except RestoreOperationError as exc:
            if exc.database_replaced:
                active_runtime.invalidate_database_derived_state()
                return RestoreResult(status="operation_failed", runtime_invalidated=True)
            return RestoreResult(status="operation_failed")

        active_runtime.invalidate_database_derived_state()
        return RestoreResult(status="success", runtime_invalidated=True)

    def execute_chat(self, request: ChatRequest) -> ChatResult:
        gemini = self.agents.get("gemini")
        final_prompt = request.original_prompt
        warnings = []

        if request.compressor_enabled and gemini and request.original_prompt:
            try:
                final_prompt = self.compressor.compress(request.original_prompt, gemini)["compressed"]
            except Exception:
                final_prompt = request.original_prompt

        file_context = ""
        if request.uploads:
            try:
                file_results = self.file_handler.handle(request.uploads, gemini)
                for file_result in file_results.get("files", []):
                    if "content" in file_result:
                        file_context += "\n--- FILE: {} ---\n{}\n".format(
                            file_result["filename"], file_result["content"]
                        )
                    elif "error" in file_result:
                        warnings.append(f"{file_result['filename']}: {file_result['error']}")
            except Exception as exc:
                error_logger.log("FILE_UPLOAD_ERROR", f"File upload handling failed: {type(exc).__name__}")
                warnings.append("Files could not be processed. Please try again.")

        context = ""
        if request.context_mode == "continue" and request.session_id:
            memory = self.runtime_memories.get(request.session_id)
            if memory:
                context = memory.get_context()
        if file_context:
            context = file_context + "\n" + context

        result_data = self._route(request, final_prompt, context)
        if result_data.get("status") != "success":
            return ChatResult(status="error", debate_data=result_data, warnings=warnings)

        persisted = False
        if request.session_id:
            chat_data = {
                "id": str(uuid.uuid4()),
                "prompt": request.original_prompt,
                "prompt_compressed": json.dumps({"compressed": final_prompt}) if final_prompt != request.original_prompt else "",
                "mode": request.context_mode,
                "context_mode": request.context_mode,
                "final_answer": result_data.get("final_answer", ""),
                "debate_data": json.dumps(result_data),
                "tokens_used": result_data.get("total_tokens", 0),
                "cost": result_data.get("total_cost", 0),
            }
            try:
                persisted = self.persist_chat(self._database(), request.session_id, self.runtime_memories, chat_data)
            except Exception as exc:
                error_logger.log("CHAT_PERSISTENCE_ERROR", f"Chat persistence failed: {type(exc).__name__}")
                return ChatResult(status="error", debate_data=result_data, warnings=warnings + ["Chat could not be saved. Please try again."])
            if not persisted:
                return ChatResult(status="error", debate_data=result_data, warnings=warnings + ["Chat could not be saved. Please try again."])

        return ChatResult(
            status="success", final_answer=result_data.get("final_answer", ""),
            debate_data=result_data, tokens=result_data.get("total_tokens", 0),
            cost=result_data.get("total_cost", 0), warnings=warnings, persisted=persisted,
        )

    def _route(self, request, final_prompt, context):
        active = request.active_agents
        direct_runtime_prompt = final_prompt
        if context:
            direct_runtime_prompt = f"CONTEXT:\n{context[:3000]}\n\nTASK:\n{final_prompt}"

        if "unified" in active or "remote" in active:
            agent = self.agents.get("unified") if "unified" in active else self.agents.get("remote")
            try:
                response = agent.generate(
                    prompt=direct_runtime_prompt, system_prompt=None, mode=request.session_mode,
                )
            except Exception as exc:
                error_logger.log("DIRECT_AGENT_FAILURE", f"Direct execution failed: {type(exc).__name__}")
                response = {"status": "error", "tokens": 0, "cost": 0}
            response = response if isinstance(response, dict) else {"status": "error", "tokens": 0, "cost": 0}
            return {
                "responses": [response],
                "final_answer": response.get("text", "") if BaseProvider.has_usable_response(response) else TERMINAL_PROVIDER_FAILURE_TEXT,
                "total_tokens": response.get("tokens", 0), "total_cost": response.get("cost", 0),
                "status": response.get("status", "error"),
            }

        orchestrator = self.debate_factory(
            gemini_agent=self.agents.get("gemini"), deepseek_agent=self.agents.get("deepseek"),
            groq_agent=self.agents.get("groq"), cloudflare_agent=self.agents.get("cloudflare"),
            openrouter_agent=self.agents.get("openrouter"), huggingface_agent=self.agents.get("huggingface"),
        )
        try:
            return orchestrator.debate(
                prompt=final_prompt, context=context[:3000], mode=request.session_mode,
                rounds=request.debate_rounds, agents=active, skill=request.selected_skill,
            )
        except Exception as exc:
            error_logger.log("DEBATE_EXECUTION_FAILURE", f"Debate execution failed: {type(exc).__name__}")
            return {"status": "error", "responses": [], "total_tokens": 0, "total_cost": 0}
