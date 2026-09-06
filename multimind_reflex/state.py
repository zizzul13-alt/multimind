"""RJ-3 Reflex state for production presentation parity.

Presentation state stays host-owned. Application/provider/persistence truth remains
behind MultiMindApplication and the shared composition root.
"""

from __future__ import annotations

import asyncio
import json
import re

import reflex as rx

from core.application import ChatRequest
from core.file_handler import FileHandler
from core.templates import TemplateManager
from multimind_reflex.bridge import BufferedUpload, build_host_application
from ui.dna_bridge import dna_available, ensure_dna_registered, theme_studio_available
from utils.config import Config, InvalidUserIdError
from utils.token_counter import TokenCounter


ARCHETYPES = [
    "chat_first",
    "command_center",
    "ai_workspace",
    "ai_research_lab",
    "agent_canvas",
    "terminal_hacker",
    "minimal_saas",
]
AGENT_OPTIONS = ["gemini", "deepseek", "groq", "cloudflare", "openrouter", "huggingface"]
SKILL_OPTIONS = ["default", "coding", "research", "thinking"]
_TEMPLATE_MANAGER = TemplateManager()
TEMPLATE_OPTIONS = [""] + [item[0] for item in _TEMPLATE_MANAGER.get_template_names()]
_TEMPLATE_VARIABLE_RE = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")


def _session_snapshots(rows):
    return [
        {
            "id": str(row.get("id", "")),
            "name": str(row.get("name", "Session")),
            "mode": str(row.get("mode", "coding")),
        }
        for row in rows
    ]


def _history_snapshots(rows):
    return [
        {
            "id": str(row.get("id", "")),
            "prompt": str(row.get("prompt", "")),
            "final_answer": str(row.get("final_answer", "")),
        }
        for row in rows
    ]


class HostState(rx.State):
    """Reflex presentation state implementing the frozen RJ-3 denominator."""

    # Identity / navigation.
    username: str = ""
    display_username: str = ""
    user_id: str = ""
    logged_in: bool = False
    current_surface: str = "theme"  # theme | workspace

    # Theme Studio presentation state. Draft never changes application truth.
    theme_studio_open: bool = True
    dna_runtime_available: bool = False
    private_theme_studio_available: bool = False
    draft_archetype: str = "chat_first"
    active_archetype: str = "chat_first"
    draft_identity_dna: str = ""
    draft_web_dna: str = ""
    draft_density: str = "comfortable"
    draft_radius: str = "medium"
    active_identity_dna: str = ""
    active_web_dna: str = ""
    active_density: str = "comfortable"
    active_radius: str = "medium"
    theme_status: str = "Safe neutral presentation"

    # Session lifecycle.
    sessions: list[dict[str, str]] = []
    new_session_name: str = ""
    new_session_mode: str = "coding"
    current_session_id: str = ""
    current_session_name: str = ""
    current_session_mode: str = "coding"
    history: list[dict[str, str]] = []

    # Composer / template / execution controls.
    prompt: str = ""
    selected_template: str = ""
    template_description: str = ""
    template_variables: list[str] = []
    template_variables_json: str = "{}"
    template_preview: str = ""
    context_mode: str = "continue"
    compressor_enabled: bool = Config.COMPRESSOR_ENABLED
    active_agents: list[str] = list(Config.DEFAULT_AGENTS)
    debate_rounds: int = Config.DEBATE_ROUNDS_DEFAULT
    selected_skill: str = "default"

    # Pre-send usage feedback.
    estimated_prompt_tokens: int = 0
    estimated_file_tokens: int = 0
    estimated_total_tokens: int = 0
    estimated_cost: float = 0.0
    token_warning_level: str = "low"

    # Execution/result state.
    busy: bool = False
    status_message: str = ""
    error_message: str = ""
    success_message: str = ""
    final_answer: str = ""
    warnings: list[str] = []
    upload_names: list[str] = []
    restore_name: str = ""

    _runtime_memories: dict = {}
    _pending_uploads: list[dict] = []
    _pending_restore: bytes = b""

    def _application(self):
        if not self.user_id:
            raise RuntimeError("A validated user identity is required.")
        return build_host_application(self.user_id, self._runtime_memories)

    def _refresh_sessions(self):
        self.sessions = _session_snapshots(self._application().list_sessions())

    def _refresh_history(self):
        if not self.current_session_id:
            self.history = []
            return
        self.history = _history_snapshots(
            self._application().get_session_chats(self.current_session_id, limit=50)
        )

    def _refresh_estimate(self):
        estimate = TokenCounter.estimate_total(
            self.prompt or "",
            files_count=len(self._pending_uploads),
            mode=self.current_session_mode or self.new_session_mode,
            rounds=self.debate_rounds,
            compressor_on=self.compressor_enabled,
        )
        self.estimated_prompt_tokens = int(estimate["prompt_tokens"])
        self.estimated_file_tokens = int(estimate["file_tokens"])
        self.estimated_total_tokens = int(estimate["total_estimate"])
        self.estimated_cost = float(TokenCounter.estimate_cost(self.estimated_total_tokens))
        self.token_warning_level = TokenCounter.get_warning_level(self.estimated_total_tokens)["level"]

    @rx.event
    def set_username(self, value: str):
        self.username = value

    @rx.event
    def set_new_session_name(self, value: str):
        self.new_session_name = value

    @rx.event
    def set_new_session_mode(self, value: str):
        self.new_session_mode = value
        self._refresh_estimate()

    @rx.event
    def set_prompt(self, value: str):
        self.prompt = value
        self._refresh_estimate()

    @rx.event
    def set_context_mode(self, value: str):
        self.context_mode = value

    @rx.event
    def set_compressor_enabled(self, value: bool):
        self.compressor_enabled = bool(value)
        self._refresh_estimate()

    @rx.event
    def set_debate_rounds(self, value: str):
        try:
            self.debate_rounds = max(1, min(5, int(value)))
        except (TypeError, ValueError):
            self.debate_rounds = Config.DEBATE_ROUNDS_DEFAULT
        self._refresh_estimate()

    @rx.event
    def set_selected_skill(self, value: str):
        self.selected_skill = value or "default"

    @rx.event
    def set_agent_enabled(self, agent: str, enabled: bool):
        if agent not in AGENT_OPTIONS:
            return
        selected = list(self.active_agents)
        if enabled and agent not in selected:
            selected.append(agent)
        elif not enabled and agent in selected:
            selected.remove(agent)
        self.active_agents = selected or ["gemini"]

    @rx.event
    def login(self):
        self.error_message = ""
        self.success_message = ""
        try:
            display_username, user_id = Config.resolve_supplied_identity(self.username)
        except InvalidUserIdError as exc:
            self.error_message = str(exc)
            return

        self.display_username = display_username
        self.user_id = user_id
        self.logged_in = True
        self.current_surface = "theme"
        self.theme_studio_open = True
        self.dna_runtime_available = dna_available()
        self.private_theme_studio_available = theme_studio_available()
        if self.dna_runtime_available:
            ensure_dna_registered()
            self.theme_status = "Private Design-DNA available"
        else:
            self.theme_status = "Safe neutral presentation"
        self.current_session_id = ""
        self.current_session_name = ""
        self.current_session_mode = "coding"
        self.history = []
        self.final_answer = ""
        self.warnings = []
        self._runtime_memories = {}
        self._pending_uploads = []
        self.upload_names = []
        self._refresh_sessions()
        self._refresh_estimate()

    @rx.event
    def logout(self):
        if self.busy:
            self.error_message = "A run is still active."
            return
        self.username = ""
        self.display_username = ""
        self.user_id = ""
        self.logged_in = False
        self.current_surface = "theme"
        self.sessions = []
        self.current_session_id = ""
        self.current_session_name = ""
        self.current_session_mode = "coding"
        self.history = []
        self.prompt = ""
        self.status_message = ""
        self.error_message = ""
        self.success_message = ""
        self.final_answer = ""
        self.warnings = []
        self.upload_names = []
        self._runtime_memories = {}
        self._pending_uploads = []
        self._pending_restore = b""

    # Theme Studio draft/apply/discard/reset/handoff.
    @rx.event
    def set_draft_archetype(self, value: str):
        if value in ARCHETYPES:
            self.draft_archetype = value

    @rx.event
    def set_draft_identity_dna(self, value: str):
        self.draft_identity_dna = value

    @rx.event
    def set_draft_web_dna(self, value: str):
        self.draft_web_dna = value

    @rx.event
    def set_draft_density(self, value: str):
        self.draft_density = value

    @rx.event
    def set_draft_radius(self, value: str):
        self.draft_radius = value

    @rx.event
    def apply_theme(self):
        self.active_archetype = self.draft_archetype
        self.active_identity_dna = self.draft_identity_dna
        self.active_web_dna = self.draft_web_dna
        self.active_density = self.draft_density
        self.active_radius = self.draft_radius
        self.theme_studio_open = False
        self.current_surface = "workspace"
        self.success_message = "Theme composition applied."

    @rx.event
    def discard_theme(self):
        self.draft_archetype = self.active_archetype
        self.draft_identity_dna = self.active_identity_dna
        self.draft_web_dna = self.active_web_dna
        self.draft_density = self.active_density
        self.draft_radius = self.active_radius
        self.success_message = "Draft discarded."

    @rx.event
    def reset_theme(self):
        self.draft_archetype = "chat_first"
        self.draft_identity_dna = ""
        self.draft_web_dna = ""
        self.draft_density = "comfortable"
        self.draft_radius = "medium"
        self.success_message = "Draft reset to safe defaults."

    @rx.event
    def open_theme_studio(self):
        if self.busy:
            self.error_message = "Finish the active run before changing presentation."
            return
        self.theme_studio_open = True
        self.current_surface = "theme"

    @rx.event
    def return_to_workspace(self):
        self.theme_studio_open = False
        self.current_surface = "workspace"

    # Templates.
    @rx.event
    def select_template(self, template_id: str):
        self.selected_template = template_id
        template = _TEMPLATE_MANAGER.get_template(template_id) if template_id else None
        if not template:
            self.template_description = ""
            self.template_variables = []
            self.template_preview = ""
            return
        self.template_description = str(template.get("description", ""))
        self.template_variables = list(dict.fromkeys(_TEMPLATE_VARIABLE_RE.findall(template.get("prompt", ""))))
        self.template_variables_json = "{}"
        self.template_preview = str(template.get("prompt", ""))

    @rx.event
    def set_template_variables_json(self, value: str):
        self.template_variables_json = value
        if not self.selected_template:
            return
        try:
            variables = json.loads(value or "{}")
            if not isinstance(variables, dict):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            self.template_preview = "Invalid JSON variables."
            return
        applied = _TEMPLATE_MANAGER.apply_template(self.selected_template, variables) or {}
        self.template_preview = str(applied.get("prompt", ""))

    @rx.event
    def use_template_preview(self):
        if self.template_preview and self.template_preview != "Invalid JSON variables.":
            self.prompt = self.template_preview
            self._refresh_estimate()

    # Sessions.
    @rx.event
    def create_session(self):
        if not self.logged_in:
            self.error_message = "Login required."
            return
        name = self.new_session_name.strip()
        if not name:
            self.error_message = "Session name is required."
            return

        application = self._application()
        session_id = application.create_session(name, self.new_session_mode)
        self._refresh_sessions()
        session = next((item for item in self.sessions if item["id"] == session_id), None)
        if session is not None:
            application.select_session(session)
            self.current_session_id = session["id"]
            self.current_session_name = session.get("name", name)
            self.current_session_mode = session.get("mode", self.new_session_mode)
        self.new_session_name = ""
        self.error_message = ""
        self.success_message = "Session created."
        self._refresh_history()
        self._refresh_estimate()

    @rx.event
    def select_session(self, session_id: str):
        if self.busy:
            self.error_message = "Finish the active run before switching sessions."
            return
        session = next((item for item in self.sessions if item["id"] == session_id), None)
        if session is None:
            self.error_message = "Session not found."
            return

        self._application().select_session(session)
        self.current_session_id = session["id"]
        self.current_session_name = session.get("name", "Session")
        self.current_session_mode = session.get("mode", "coding")
        self.error_message = ""
        self.success_message = ""
        self.final_answer = ""
        self.warnings = []
        self._refresh_history()
        self._refresh_estimate()

    # Uploads and restore staging must consume UploadFile outside background work.
    @rx.event
    async def stage_uploads(self, files: list[rx.UploadFile]):
        staged = []
        warnings = []
        for upload in files[: FileHandler.MAX_FILES]:
            name = upload.filename or "upload"
            declared_size = getattr(upload, "size", None)
            if declared_size is not None and declared_size > FileHandler.MAX_SIZE:
                warnings.append(f"{name}: file too large (max 10MB)")
                continue
            data = await upload.read()
            if len(data) > FileHandler.MAX_SIZE:
                warnings.append(f"{name}: file too large (max 10MB)")
                continue
            staged.append({"name": name, "data": data})

        self._pending_uploads = staged
        self.upload_names = [item["name"] for item in staged]
        self.warnings = warnings
        self._refresh_estimate()

    @rx.event
    def clear_uploads(self):
        if self.busy:
            return
        self._pending_uploads = []
        self.upload_names = []
        self._refresh_estimate()

    @rx.event
    async def stage_restore(self, files: list[rx.UploadFile]):
        self._pending_restore = b""
        self.restore_name = ""
        if not files:
            return
        upload = files[0]
        self.restore_name = upload.filename or "backup.db"
        self._pending_restore = await upload.read()

    @rx.event
    def restore_database(self):
        if self.busy:
            self.error_message = "Finish the active run before restore."
            return
        if not self._pending_restore:
            self.error_message = "Stage a backup first."
            return
        result = self._application().restore_database(self._pending_restore)
        self.error_message = ""
        if result.status == "success":
            self.current_session_id = ""
            self.current_session_name = ""
            self.history = []
            self.final_answer = ""
            self._runtime_memories = {}
            self._refresh_sessions()
            self.success_message = "Database restored safely."
        elif result.status == "invalid_backup":
            self.error_message = "Backup is invalid."
        else:
            self.error_message = "Restore operation failed."
        self._pending_restore = b""
        self.restore_name = ""

    @rx.event
    def export_database(self):
        if not self.logged_in:
            return
        return rx.download(
            data=self._application().export_database(),
            filename=f"multimind-{self.user_id}.db",
        )

    @rx.event(background=True)
    async def run_chat(self):
        """Execute the real app while preserving persistent busy/duplicate-run safety."""
        async with self:
            if self.busy:
                return
            if not self.logged_in:
                self.error_message = "Login required."
                return
            if not self.current_session_id:
                self.error_message = "Select or create a session first."
                return
            prompt = self.prompt.strip()
            if not prompt and not self._pending_uploads:
                self.error_message = "Enter a prompt or stage at least one file."
                return
            if not self.active_agents:
                self.error_message = "Select at least one agent."
                return

            self.busy = True
            self.status_message = "Running…"
            self.error_message = ""
            self.success_message = ""
            self.final_answer = ""
            self.warnings = []

            user_id = self.user_id
            session_id = self.current_session_id
            session_mode = self.current_session_mode
            runtime_memories = self._runtime_memories
            staged_uploads = [dict(item) for item in self._pending_uploads]
            request = ChatRequest(
                original_prompt=prompt,
                uploads=[BufferedUpload(item["name"], item["data"]) for item in staged_uploads],
                context_mode=self.context_mode,
                session_id=session_id,
                session_mode=session_mode,
                compressor_enabled=self.compressor_enabled,
                active_agents=list(self.active_agents),
                debate_rounds=self.debate_rounds,
                selected_skill=self.selected_skill,
            )

        try:
            application = build_host_application(user_id, runtime_memories)
            result = await asyncio.to_thread(application.execute_chat, request)
            history = await asyncio.to_thread(application.get_session_chats, session_id, 50)
        except Exception:
            result = None
            history = None

        async with self:
            self.busy = False
            self.status_message = ""
            if result is None:
                self.error_message = "Chat execution failed. Please try again."
                return

            self.warnings = list(result.warnings)
            if result.status != "success":
                self.error_message = "No usable provider response was returned."
                return

            self.final_answer = result.final_answer
            self.history = _history_snapshots(history or [])
            self.prompt = ""
            self._pending_uploads = []
            self.upload_names = []
            self.success_message = "Response saved to session history."
            self._refresh_estimate()
