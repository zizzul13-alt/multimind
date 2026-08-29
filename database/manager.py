"""
Database manager - SQLite Simple
"""
import sqlite3
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path


class RestoreValidationError(ValueError):
    """Raised when an uploaded restore candidate is invalid or incompatible."""


REQUIRED_RESTORE_SCHEMA = {
    "sessions": {"id", "name", "mode", "config", "created_at", "updated_at"},
    "chats": {
        "id", "session_id", "prompt", "prompt_compressed", "mode",
        "context_mode", "final_answer", "debate_data", "tokens_used", "cost",
        "created_at",
    },
}


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

    def restore_from_bytes(self, backup_bytes):
        """Validate an uploaded backup before replacing this manager's database.

        This deliberately validates a separate temporary candidate first. The
        subsequent replacement retains the existing non-atomic behavior; crash
        safety and recovery are outside this validation boundary.
        """
        if not isinstance(backup_bytes, bytes):
            raise RestoreValidationError("Backup content is invalid.")

        file_descriptor, candidate_path = tempfile.mkstemp(suffix=".db")
        try:
            with os.fdopen(file_descriptor, "wb") as candidate_file:
                candidate_file.write(backup_bytes)
            validate_restore_candidate(candidate_path)
            with open(candidate_path, "rb") as candidate_file, open(self.db_path, "wb") as active_file:
                active_file.write(candidate_file.read())
        finally:
            if os.path.exists(candidate_path):
                os.remove(candidate_path)
        return True

    def save_chat(self, session_id, chat_data):
        """Save chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chats 
            (id, session_id, prompt, prompt_compressed, mode, context_mode,
             final_answer, debate_data, tokens_used, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chat_data["id"], session_id, chat_data["prompt"],
            chat_data.get("prompt_compressed", ""),
            chat_data.get("mode", "continue"),
            chat_data.get("context_mode", "continue"),
            chat_data.get("final_answer", ""),
            chat_data.get("debate_data", "{}"),
            chat_data.get("tokens_used", 0),
            chat_data.get("cost", 0.0)
        ))
        
        conn.commit()
        conn.close()
        return True

    def get_session_chats(self, session_id, limit=50):
        """Get chats"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM chats 
            WHERE session_id = ? 
            ORDER BY created_at ASC 
            LIMIT ?
        """, (session_id, limit))
        
        chats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return chats

    def get_session_chats_for_memory(self, session_id):
        """Get complete chat history in deterministic insertion order for memory hydration."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # This table is not declared WITHOUT ROWID, so rowid is available as a
        # stable insertion-order tiebreaker when SQLite timestamps share a second.
        cursor.execute("""
            SELECT * FROM chats
            WHERE session_id = ?
            ORDER BY created_at ASC, rowid ASC
        """, (session_id,))

        chats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return chats

    def create_session(self, session_id, name, mode="coding", config=None):
        """Create session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (id, name, mode, config)
            VALUES (?, ?, ?, ?)
        """, (session_id, name, mode, json.dumps(config or {})))
        
        conn.commit()
        conn.close()
        return True

    def get_sessions(self):
        """Get all sessions"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions ORDER BY updated_at DESC")
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sessions
