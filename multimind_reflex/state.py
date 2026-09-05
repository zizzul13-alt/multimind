"""RJ-2 Reflex state: identity -> session -> background execution -> result."""

from __future__ import annotations

import asyncio

import reflex as rx

from core.application import ChatRequest
from core.file_handler import FileHandler
from multimind_reflex.bridge import BufferedUpload, build_host_application
from utils.config import Config, InvalidUserIdError


class HostState(rx.State):
    """Minimal production-host spine; RJ-3 owns full presentation parity."""

    username: str = ""
    display_username: str = ""
    user_id: str = ""
    logged_in: bool = False

    sessions: list[dict] = []
    new_session_name: str = ""
    current_session_id: str = ""
    current_session_name: str = ""
    current_session_mode: str = "coding"
    history: list[dict] = []

    prompt: str = ""
    busy: bool = False
    status_message: str = ""
    error_message: str = ""
    final_answer: str = ""
    warnings: list[str] = []
    upload_names: list[str] = []

    _runtime_memories: dict = {}
    _pending_uploads: list[dict] = []

    def _application(self):
        if not self.user_id:
            raise RuntimeError("A validated user identity is required.")
        return build_host_application(self.user_id, self._runtime_memories)

    def _refresh_sessions(self):
        self.sessions = list(self._application().list_sessions())

    def _refresh_history(self):
        if not self.current_session_id:
            self.history = []
            return
        self.history = list(
            self._application().get_session_chats(self.current_session_id, limit=50)
        )

    @rx.event
    def set_username(self, value: str):
        self.username = value

    @rx.event
    def set_new_session_name(self, value: str):
        self.new_session_name = value

    @rx.event
    def set_prompt(self, value: str):
        self.prompt = value

    @rx.event
    def login(self):
        self.error_message = ""
        try:
            display_username, user_id = Config.resolve_supplied_identity(self.username)
        except InvalidUserIdError as exc:
            self.error_message = str(exc)
            return

        self.display_username = display_username
        self.user_id = user_id
        self.logged_in = True
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

    @rx.event
    def logout(self):
        if self.busy:
            self.error_message = "A run is still active."
            return
        self.username = ""
        self.display_username = ""
        self.user_id = ""
        self.logged_in = False
        self.sessions = []
        self.current_session_id = ""
        self.current_session_name = ""
        self.current_session_mode = "coding"
        self.history = []
        self.prompt = ""
        self.status_message = ""
        self.error_message = ""
        self.final_answer = ""
        self.warnings = []
        self.upload_names = []
        self._runtime_memories = {}
        self._pending_uploads = []

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
        session_id = application.create_session(name, "coding")
        self._refresh_sessions()
        session = next((item for item in self.sessions if item["id"] == session_id), None)
        if session is not None:
            application.select_session(session)
            self.current_session_id = session["id"]
            self.current_session_name = session.get("name", name)
            self.current_session_mode = session.get("mode", "coding")
        self.new_session_name = ""
        self.error_message = ""
        self._refresh_history()

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
        self.final_answer = ""
        self.warnings = []
        self._refresh_history()

    @rx.event
    async def stage_uploads(self, files: list[rx.UploadFile]):
        """Consume UploadFile in the normal upload event, never in a background task."""
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

    @rx.event
    def clear_uploads(self):
        if self.busy:
            return
        self._pending_uploads = []
        self.upload_names = []

    @rx.event(background=True)
    async def run_chat(self):
        """Run the real application in a supported Reflex background event."""
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

            self.busy = True
            self.status_message = "Running…"
            self.error_message = ""
            self.final_answer = ""
            self.warnings = []

            user_id = self.user_id
            session_id = self.current_session_id
            session_mode = self.current_session_mode
            runtime_memories = self._runtime_memories
            staged_uploads = [dict(item) for item in self._pending_uploads]

        uploads = [
            BufferedUpload(item["name"], item["data"])
            for item in staged_uploads
        ]

        try:
            application = build_host_application(user_id, runtime_memories)
            result = await asyncio.to_thread(
                application.execute_chat,
                ChatRequest(
                    original_prompt=prompt,
                    uploads=uploads,
                    context_mode="continue",
                    session_id=session_id,
                    session_mode=session_mode,
                    compressor_enabled=Config.COMPRESSOR_ENABLED,
                    active_agents=list(Config.DEFAULT_AGENTS),
                    debate_rounds=Config.DEBATE_ROUNDS_DEFAULT,
                    selected_skill="default",
                ),
            )
            history = await asyncio.to_thread(
                application.get_session_chats,
                session_id,
                50,
            )
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
            self.history = list(history or [])
            self.prompt = ""
            self._pending_uploads = []
            self.upload_names = []
