"""
Database manager - SQLite Simple
"""
import sqlite3
import os
import json
from datetime import datetime

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