"""
Database manager - Turso (SQLite Edge)
"""
import os
import json
from datetime import datetime
import libsql_experimental as libsql
from utils.error_handler import DatabaseError, error_logger

class DatabaseManager:
    """Turso database manager"""

    def __init__(self, db_path_or_url, auth_token=None):
        self.db_url = db_path_or_url
        self.auth_token = auth_token
        
        if auth_token and db_path_or_url.startswith("libsql://"):
            # Turso mode
            self.client = libsql.connect(
                database=db_path_or_url,
                auth_token=auth_token
            )
            self.is_turso = True
        else:
            # SQLite local fallback
            import sqlite3
            os.makedirs(os.path.dirname(db_path_or_url), exist_ok=True)
            self.client = sqlite3.connect(db_path_or_url)
            self.client.row_factory = sqlite3.Row
            self.is_turso = False
        
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        try:
            self.client.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    mode TEXT DEFAULT 'coding',
                    config TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.client.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    id TEXT PRIMARY KEY,
                    session_id TEXT REFERENCES sessions(id),
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
            
            self.client.execute("""
                CREATE TABLE IF NOT EXISTS pool_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    api_owner TEXT,
                    provider TEXT,
                    tokens INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0.0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.client.commit()
        
        except Exception as e:
            error_logger.log("DB_INIT_ERROR", str(e))
            raise DatabaseError(f"Failed to initialize database: {e}")

    def save_chat(self, session_id, chat_data):
        """Save chat to database"""
        try:
            self.client.execute("""
                INSERT INTO chats 
                (id, session_id, prompt, prompt_compressed, mode, context_mode,
                 final_answer, debate_data, tokens_used, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chat_data["id"],
                session_id,
                chat_data["prompt"],
                chat_data.get("prompt_compressed", ""),
                chat_data.get("mode", "continue"),
                chat_data.get("context_mode", "continue"),
                chat_data.get("final_answer", ""),
                chat_data.get("debate_data", "{}"),
                chat_data.get("tokens_used", 0),
                chat_data.get("cost", 0.0)
            ))
            
            self.client.commit()
            return True
        
        except Exception as e:
            error_logger.log("DB_SAVE_ERROR", str(e))
            return False

    def get_session_chats(self, session_id, limit=50):
        """Get chats for a session"""
        try:
            result = self.client.execute("""
                SELECT * FROM chats 
                WHERE session_id = ? 
                ORDER BY created_at ASC 
                LIMIT ?
            """, (session_id, limit))
            
            if self.is_turso:
                rows = result.fetchall()
                chats = []
                for row in rows:
                    chat = {
                        "id": row[0],
                        "session_id": row[1],
                        "prompt": row[2],
                        "prompt_compressed": row[3],
                        "mode": row[4],
                        "context_mode": row[5],
                        "final_answer": row[6],
                        "debate_data": row[7],
                        "tokens_used": row[8],
                        "cost": row[9],
                        "created_at": row[10]
                    }
                    chats.append(chat)
                return chats
            else:
                return [dict(row) for row in result.fetchall()]
        
        except Exception as e:
            error_logger.log("DB_QUERY_ERROR", str(e))
            return []

    def create_session(self, session_id, name, mode="coding", config=None):
        """Create new session"""
        try:
            self.client.execute("""
                INSERT INTO sessions (id, name, mode, config)
                VALUES (?, ?, ?, ?)
            """, (session_id, name, mode, json.dumps(config or {})))
            
            self.client.commit()
            return True
        
        except Exception as e:
            error_logger.log("DB_SESSION_ERROR", str(e))
            return False

    def get_sessions(self):
        """Get all sessions"""
        try:
            result = self.client.execute("""
                SELECT * FROM sessions 
                ORDER BY updated_at DESC
            """)
            
            if self.is_turso:
                rows = result.fetchall()
                sessions = []
                for row in rows:
                    session = {
                        "id": row[0],
                        "name": row[1],
                        "mode": row[2],
                        "config": row[3],
                        "created_at": row[4],
                        "updated_at": row[5]
                    }
                    sessions.append(session)
                return sessions
            else:
                return [dict(row) for row in result.fetchall()]
        
        except Exception as e:
            error_logger.log("DB_QUERY_ERROR", str(e))
            return []

    def log_pool_usage(self, user_id, api_owner, provider, tokens, cost):
        """Log API pool usage"""
        try:
            self.client.execute("""
                INSERT INTO pool_usage (user_id, api_owner, provider, tokens, cost)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, api_owner, provider, tokens, cost))
            
            self.client.commit()
        
        except Exception as e:
            error_logger.log("POOL_LOG_ERROR", str(e))
