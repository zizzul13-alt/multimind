"""
Database manager - SQLite Simple
"""
import sqlite3
import os
import json
import tempfile
from pathlib import Path


class RestoreValidationError(ValueError):
    """Raised when an uploaded restore candidate is invalid or incompatible."""


class RestoreOperationError(RuntimeError):
    """Raised when staging, activation, or post-activation verification fails."""

    def __init__(self, message, *, database_replaced=False):
        super().__init__(message)
        self.database_replaced = database_replaced


REQUIRED_RESTORE_SCHEMA = {
    "sessions": {"id", "name", "mode", "config", "created_at", "updated_at"},
    "chats": {
        "id", "session_id", "prompt", "prompt_compressed", "mode",
        "context_mode", "final_answer", "debate_data", "tokens_used", "cost",
        "created_at",
    },
}

MAX_RESTORE_CANDIDATE_BYTES = 100 * 1024 * 1024


def validate_restore_candidate(candidate_path):
    """Fail closed unless an isolated candidate is an intact MultiMind database."""
    candidate_uri = Path(candidate_path).resolve().as_uri()
    try:
        conn = sqlite3.connect(f"{candidate_uri}?mode=ro", uri=True)
        try:
            integrity_result = [row[0] for row in conn.execute("PRAGMA integrity_check")]
            if integrity_result != ["ok"]:
                raise RestoreValidationError("Backup integrity check failed.")

            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            for table_name, required_columns in REQUIRED_RESTORE_SCHEMA.items():
                if table_name not in tables:
                    raise RestoreValidationError("Backup schema is incompatible.")
                columns = {
                    row[1] for row in conn.execute(f"PRAGMA table_info({table_name})")
                }
                if not required_columns.issubset(columns):
                    raise RestoreValidationError("Backup schema is incompatible.")
        finally:
            conn.close()
    except RestoreValidationError:
        raise
    except sqlite3.Error as exc:
        raise RestoreValidationError("Backup is not a valid SQLite database.") from exc


class DatabaseManager:
    """SQLite database manager"""

    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT,
                mode TEXT DEFAULT 'coding',
                config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                prompt TEXT,
                prompt_compressed TEXT,
                mode TEXT DEFAULT 'continue',
                context_mode TEXT DEFAULT 'continue',
                final_answer TEXT,
                debate_data TEXT,
                tokens_used INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def export_bytes(self):
        """Return a transactionally consistent SQLite snapshot as bytes."""
        db_directory = os.path.dirname(os.path.abspath(self.db_path))
        file_descriptor, snapshot_path = tempfile.mkstemp(
            prefix=".multimind-export-",
            suffix=".db",
            dir=db_directory,
        )
        os.close(file_descriptor)
        try:
            source = sqlite3.connect(self.db_path)
            destination = sqlite3.connect(snapshot_path)
            try:
                source.backup(destination)
            finally:
                destination.close()
                source.close()
            validate_restore_candidate(snapshot_path)
            with open(snapshot_path, "rb") as database_file:
                return database_file.read()
        finally:
            try:
                os.remove(snapshot_path)
            except FileNotFoundError:
                pass

    def restore_from_bytes(self, backup_bytes):
        """Stage and validate an uploaded backup before single-step activation."""
        if not isinstance(backup_bytes, bytes):
            raise RestoreValidationError("Backup content is invalid.")
        if len(backup_bytes) > MAX_RESTORE_CANDIDATE_BYTES:
            raise RestoreValidationError("Backup is too large to restore.")

        db_directory = os.path.dirname(os.path.abspath(self.db_path))
        try:
            file_descriptor, candidate_path = tempfile.mkstemp(
                prefix=".multimind-restore-",
                suffix=".db",
                dir=db_directory,
            )
        except OSError as exc:
            raise RestoreOperationError("Backup staging failed.") from exc
        try:
            try:
                candidate_file = os.fdopen(file_descriptor, "wb")
            except OSError as exc:
                os.close(file_descriptor)
                raise RestoreOperationError("Backup staging failed.") from exc

            try:
                with candidate_file:
                    bytes_written = candidate_file.write(backup_bytes)
                    if bytes_written != len(backup_bytes):
                        raise RestoreOperationError("Backup staging write was incomplete.")
            except OSError as exc:
                raise RestoreOperationError("Backup staging failed.") from exc
            validate_restore_candidate(candidate_path)
            try:
                os.replace(candidate_path, self.db_path)
            except OSError as exc:
                raise RestoreOperationError("Database replacement failed.") from exc

            candidate_path = None
            try:
                validate_restore_candidate(self.db_path)
            except (RestoreValidationError, OSError) as exc:
                raise RestoreOperationError(
                    "Database replacement could not be verified.",
                    database_replaced=True,
                ) from exc
        finally:
            if candidate_path and os.path.exists(candidate_path):
                try:
                    os.remove(candidate_path)
                except OSError:
                    pass

    def create_session(self, session_id, name, mode="coding", config=None):
        """Create new session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (id, name, mode, config)
            VALUES (?, ?, ?, ?)
        """, (session_id, name, mode, json.dumps(config or {})))
        conn.commit()
        conn.close()

    def get_sessions(self):
        """Get all sessions"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY updated_at DESC")
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sessions

    def save_chat(self, chat_data):
        """Save chat to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chats (
                id, session_id, prompt, prompt_compressed, mode,
                context_mode, final_answer, debate_data, tokens_used, cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chat_data["id"], chat_data["session_id"], chat_data["prompt"],
            chat_data.get("prompt_compressed", ""), chat_data.get("mode", "continue"),
            chat_data.get("context_mode", "continue"), chat_data["final_answer"],
            chat_data.get("debate_data", "{}"), chat_data.get("tokens_used", 0),
            chat_data.get("cost", 0.0)
        ))
        conn.commit()
        conn.close()

    def get_session_chats(self, session_id, limit=50):
        """Get chats for session"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chats
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (session_id, limit))
        chats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return chats

    def update_session_timestamp(self, session_id):
        """Update session timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()
