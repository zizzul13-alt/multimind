"""
Database manager for user history
"""
import sqlite3
import os
import json
from datetime import datetime
from utils.error_handler import DatabaseError, error_logger

class DatabaseManager:
    """SQLite database manager"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sessions table
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
            
            # Chats table
            cursor.execute("""
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
            
            # Pool usage table
            cursor.execute("""
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
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            error_logger.log("DB_INIT_ERROR", str(e))
            raise DatabaseError(f"Failed to initialize database: {e}")
    
def save_chat(self, session_id, chat_data):
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # DEBUG
        print(f"DEBUG DB: debate_data type: {type(chat_data.get('debate_data'))}")
        print(f"DEBUG DB: debate_data preview: {str(chat_data.get('debate_data', ''))[:200]}")
        
        cursor.execute("""
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
            chat_data.get("debate_data", "{}"),  # ← INI YANG DISIMPAN
            chat_data.get("tokens_used", 0),
            chat_data.get("cost", 0.0)
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"DEBUG DB ERROR: {e}")
        return False
    
    def get_session_chats(self, session_id, limit=50):
        """Get chats for a session"""
        try:
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
        
        except Exception as e:
            error_logger.log("DB_QUERY_ERROR", str(e))
            return []
    
    def create_session(self, session_id, name, mode="coding", config=None):
        """Create new session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sessions (id, name, mode, config)
                VALUES (?, ?, ?, ?)
            """, (session_id, name, mode, json.dumps(config or {})))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            error_logger.log("DB_SESSION_ERROR", str(e))
            return False
    
    def get_sessions(self):
        """Get all sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM sessions 
                ORDER BY updated_at DESC
            """)
            
            sessions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return sessions
        
        except Exception as e:
            error_logger.log("DB_QUERY_ERROR", str(e))
            return []
    
    def log_pool_usage(self, user_id, api_owner, provider, tokens, cost):
        """Log API pool usage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO pool_usage (user_id, api_owner, provider, tokens, cost)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, api_owner, provider, tokens, cost))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            error_logger.log("POOL_LOG_ERROR", str(e))
