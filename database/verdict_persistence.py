"""Small persistence extensions for application-owned user verdict updates.

No schema migration is introduced. Verdict truth remains inside the existing
``chats.debate_data`` JSON for both SQLite and Turso implementations.
"""

from __future__ import annotations

from database.manager import DatabaseManager
from database.turso_manager import CHATS_TABLE, CHAT_COLUMNS, TursoDatabaseManager, _rows_as_dicts


class VerdictDatabaseManager(DatabaseManager):
    """SQLite manager with bounded chat read/update operations."""

    def get_chat(self, session_id, chat_id):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT * FROM chats WHERE session_id = ? AND id = ? LIMIT 1",
                (session_id, chat_id),
            )
            row = cursor.fetchone()
            return dict(row) if row is not None else None
        finally:
            conn.close()

    def update_chat_debate_data(self, session_id, chat_id, debate_data):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "UPDATE chats SET debate_data = ? WHERE session_id = ? AND id = ?",
                (debate_data, session_id, chat_id),
            )
            conn.commit()
            return cursor.rowcount == 1
        finally:
            conn.close()


class VerdictTursoDatabaseManager(TursoDatabaseManager):
    """Turso manager preserving the existing user_id isolation boundary."""

    def get_chat(self, session_id, chat_id):
        conn = self._connect()
        try:
            cursor = conn.execute(
                f"SELECT {', '.join(CHAT_COLUMNS)} FROM {CHATS_TABLE} "
                "WHERE user_id = ? AND session_id = ? AND id = ? LIMIT 1",
                (self.user_id, session_id, chat_id),
            )
            rows = _rows_as_dicts(cursor)
            return rows[0] if rows else None
        finally:
            conn.close()

    def update_chat_debate_data(self, session_id, chat_id, debate_data):
        conn = self._connect()
        try:
            cursor = conn.execute(
                f"UPDATE {CHATS_TABLE} SET debate_data = ? "
                "WHERE user_id = ? AND session_id = ? AND id = ?",
                (debate_data, self.user_id, session_id, chat_id),
            )
            conn.commit()
            return cursor.rowcount == 1
        finally:
            conn.close()
