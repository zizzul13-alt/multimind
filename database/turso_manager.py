"""Remote Turso persistence adapter preserving MultiMind's database contract.

The adapter deliberately keeps SQLite as the local/fallback implementation while
using one shared remote Turso database with explicit ``user_id`` scoping.  It
also preserves the existing user-facing SQLite backup format by materializing a
portable per-user SQLite snapshot on export and restoring that snapshot into the
remote user scope transactionally.
"""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile

from database.manager import (
    MAX_RESTORE_CANDIDATE_BYTES,
    DatabaseManager,
    RestoreOperationError,
    RestoreValidationError,
    validate_restore_candidate,
)


SESSIONS_TABLE = "multimind_sessions"
CHATS_TABLE = "multimind_chats"

SESSION_COLUMNS = (
    "id", "name", "mode", "config", "created_at", "updated_at",
)
CHAT_COLUMNS = (
    "id", "session_id", "prompt", "prompt_compressed", "mode",
    "context_mode", "final_answer", "debate_data", "tokens_used", "cost",
    "created_at",
)


def _default_connection_factory(database_url: str, auth_token: str):
    import libsql

    return libsql.connect(database=database_url, auth_token=auth_token)


def _rows_as_dicts(cursor):
    columns = [description[0] for description in cursor.description or ()]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class TursoDatabaseManager:
    """User-scoped remote persistence implementing the DatabaseManager surface."""

    def __init__(self, database_url, auth_token, user_id, connection_factory=None):
        if not database_url or not auth_token:
            raise ValueError("Turso database URL and auth token are required together.")
        if not user_id:
            raise ValueError("A validated user_id is required for Turso persistence.")

        self.database_url = database_url
        self.auth_token = auth_token
        self.user_id = user_id
        self._connection_factory = connection_factory or _default_connection_factory
        self._init_db()

    def _connect(self):
        return self._connection_factory(self.database_url, self.auth_token)

    def _init_db(self):
        conn = self._connect()
        try:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {SESSIONS_TABLE} (
                    user_id TEXT NOT NULL,
                    id TEXT NOT NULL,
                    name TEXT,
                    mode TEXT DEFAULT 'coding',
                    config TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, id)
                )
            """)
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {CHATS_TABLE} (
                    user_id TEXT NOT NULL,
                    id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    prompt TEXT,
                    prompt_compressed TEXT,
                    mode TEXT DEFAULT 'continue',
                    context_mode TEXT DEFAULT 'continue',
                    final_answer TEXT,
                    debate_data TEXT,
                    tokens_used INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, id)
                )
            """)
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_multimind_sessions_user_updated "
                f"ON {SESSIONS_TABLE}(user_id, updated_at DESC)"
            )
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_multimind_chats_user_session_order "
                f"ON {CHATS_TABLE}(user_id, session_id, created_at ASC)"
            )
            conn.commit()
        finally:
            conn.close()

    def save_chat(self, session_id, chat_data):
        conn = self._connect()
        try:
            conn.execute(f"""
                INSERT INTO {CHATS_TABLE}
                (user_id, id, session_id, prompt, prompt_compressed, mode,
                 context_mode, final_answer, debate_data, tokens_used, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.user_id,
                chat_data["id"],
                session_id,
                chat_data["prompt"],
                chat_data.get("prompt_compressed", ""),
                chat_data.get("mode", "continue"),
                chat_data.get("context_mode", "continue"),
                chat_data.get("final_answer", ""),
                chat_data.get("debate_data", "{}"),
                chat_data.get("tokens_used", 0),
                chat_data.get("cost", 0.0),
            ))
            conn.execute(
                f"UPDATE {SESSIONS_TABLE} SET updated_at = CURRENT_TIMESTAMP "
                "WHERE user_id = ? AND id = ?",
                (self.user_id, session_id),
            )
            conn.commit()
        finally:
            conn.close()
        return True

    def get_session_chats(self, session_id, limit=50):
        conn = self._connect()
        try:
            cursor = conn.execute(f"""
                SELECT {', '.join(CHAT_COLUMNS)} FROM {CHATS_TABLE}
                WHERE user_id = ? AND session_id = ?
                ORDER BY created_at ASC, rowid ASC
                LIMIT ?
            """, (self.user_id, session_id, limit))
            return _rows_as_dicts(cursor)
        finally:
            conn.close()

    def get_session_chats_for_memory(self, session_id):
        conn = self._connect()
        try:
            cursor = conn.execute(f"""
                SELECT {', '.join(CHAT_COLUMNS)} FROM {CHATS_TABLE}
                WHERE user_id = ? AND session_id = ?
                ORDER BY created_at ASC, rowid ASC
            """, (self.user_id, session_id))
            return _rows_as_dicts(cursor)
        finally:
            conn.close()

    def create_session(self, session_id, name, mode="coding", config=None):
        conn = self._connect()
        try:
            conn.execute(f"""
                INSERT INTO {SESSIONS_TABLE} (user_id, id, name, mode, config)
                VALUES (?, ?, ?, ?, ?)
            """, (self.user_id, session_id, name, mode, json.dumps(config or {})))
            conn.commit()
        finally:
            conn.close()
        return True

    def get_sessions(self):
        conn = self._connect()
        try:
            cursor = conn.execute(
                f"SELECT {', '.join(SESSION_COLUMNS)} FROM {SESSIONS_TABLE} "
                "WHERE user_id = ? ORDER BY updated_at DESC, rowid DESC",
                (self.user_id,),
            )
            return _rows_as_dicts(cursor)
        finally:
            conn.close()

    def export_bytes(self):
        """Materialize this user's remote state as the existing SQLite backup format."""
        file_descriptor, snapshot_path = tempfile.mkstemp(
            prefix=".multimind-turso-export-", suffix=".db"
        )
        os.close(file_descriptor)
        try:
            local = DatabaseManager(snapshot_path)
            local_conn = sqlite3.connect(snapshot_path)
            remote = self._connect()
            try:
                sessions = _rows_as_dicts(remote.execute(
                    f"SELECT {', '.join(SESSION_COLUMNS)} FROM {SESSIONS_TABLE} "
                    "WHERE user_id = ? ORDER BY created_at ASC, rowid ASC",
                    (self.user_id,),
                ))
                chats = _rows_as_dicts(remote.execute(
                    f"SELECT {', '.join(CHAT_COLUMNS)} FROM {CHATS_TABLE} "
                    "WHERE user_id = ? ORDER BY created_at ASC, rowid ASC",
                    (self.user_id,),
                ))

                local_conn.executemany(
                    "INSERT INTO sessions "
                    "(id, name, mode, config, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    [tuple(row[column] for column in SESSION_COLUMNS) for row in sessions],
                )
                local_conn.executemany(
                    "INSERT INTO chats "
                    "(id, session_id, prompt, prompt_compressed, mode, context_mode, "
                    "final_answer, debate_data, tokens_used, cost, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [tuple(row[column] for column in CHAT_COLUMNS) for row in chats],
                )
                local_conn.commit()
            finally:
                remote.close()
                local_conn.close()

            validate_restore_candidate(snapshot_path)
            with open(snapshot_path, "rb") as database_file:
                return database_file.read()
        finally:
            try:
                os.remove(snapshot_path)
            except FileNotFoundError:
                pass

    def restore_from_bytes(self, backup_bytes):
        """Replace only this user's remote rows from a validated SQLite snapshot."""
        if not isinstance(backup_bytes, bytes):
            raise RestoreValidationError("Backup content is invalid.")
        if len(backup_bytes) > MAX_RESTORE_CANDIDATE_BYTES:
            raise RestoreValidationError("Backup is too large to restore.")

        file_descriptor, candidate_path = tempfile.mkstemp(
            prefix=".multimind-turso-restore-", suffix=".db"
        )
        try:
            with os.fdopen(file_descriptor, "wb") as candidate_file:
                if candidate_file.write(backup_bytes) != len(backup_bytes):
                    raise RestoreOperationError("Backup staging write was incomplete.")
            validate_restore_candidate(candidate_path)

            source = sqlite3.connect(candidate_path)
            source.row_factory = sqlite3.Row
            try:
                sessions = [dict(row) for row in source.execute(
                    "SELECT * FROM sessions ORDER BY created_at ASC, rowid ASC"
                ).fetchall()]
                chats = [dict(row) for row in source.execute(
                    "SELECT * FROM chats ORDER BY created_at ASC, rowid ASC"
                ).fetchall()]
            finally:
                source.close()

            remote = self._connect()
            committed = False
            try:
                remote.execute("BEGIN")
                remote.execute(
                    f"DELETE FROM {CHATS_TABLE} WHERE user_id = ?", (self.user_id,)
                )
                remote.execute(
                    f"DELETE FROM {SESSIONS_TABLE} WHERE user_id = ?", (self.user_id,)
                )
                for row in sessions:
                    remote.execute(
                        f"INSERT INTO {SESSIONS_TABLE} "
                        "(user_id, id, name, mode, config, created_at, updated_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (
                            self.user_id, row["id"], row["name"], row["mode"],
                            row["config"], row["created_at"], row["updated_at"],
                        ),
                    )
                for row in chats:
                    remote.execute(
                        f"INSERT INTO {CHATS_TABLE} "
                        "(user_id, id, session_id, prompt, prompt_compressed, mode, "
                        "context_mode, final_answer, debate_data, tokens_used, cost, created_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            self.user_id, row["id"], row["session_id"], row["prompt"],
                            row["prompt_compressed"], row["mode"], row["context_mode"],
                            row["final_answer"], row["debate_data"], row["tokens_used"],
                            row["cost"], row["created_at"],
                        ),
                    )
                remote.commit()
                committed = True

                session_count = remote.execute(
                    f"SELECT COUNT(*) FROM {SESSIONS_TABLE} WHERE user_id = ?",
                    (self.user_id,),
                ).fetchone()[0]
                chat_count = remote.execute(
                    f"SELECT COUNT(*) FROM {CHATS_TABLE} WHERE user_id = ?",
                    (self.user_id,),
                ).fetchone()[0]
                if session_count != len(sessions) or chat_count != len(chats):
                    raise RestoreOperationError(
                        "Database replacement could not be verified.",
                        database_replaced=True,
                    )
            except RestoreOperationError:
                raise
            except Exception as exc:
                if not committed:
                    try:
                        remote.rollback()
                    except Exception:
                        pass
                raise RestoreOperationError(
                    "Database replacement failed.", database_replaced=committed
                ) from exc
            finally:
                remote.close()
        finally:
            try:
                os.remove(candidate_path)
            except FileNotFoundError:
                pass
        return True
