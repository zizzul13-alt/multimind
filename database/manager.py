"""
Database manager - Turso via REST API
"""
import os
import json
import requests
from datetime import datetime
from utils.error_handler import DatabaseError, error_logger

class DatabaseManager:
    """Turso database manager via REST API"""

    def __init__(self, db_url, auth_token=None):
        self.db_url = db_url
        self.auth_token = auth_token
        self.is_turso = bool(auth_token and db_url.startswith("libsql://"))
        
        if not self.is_turso:
            import sqlite3
            os.makedirs(os.path.dirname(db_url), exist_ok=True)
            self.client = sqlite3.connect(db_url)
            self.client.row_factory = sqlite3.Row
        else:
            self.client = None
            # Extract host from libsql://xxx.turso.io
            self.host = db_url.replace("libsql://", "https://")
        
        self._init_db()

    def _execute_turso(self, sql, params=None):
        """Execute SQL via Turso REST API"""
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "requests": [
                {"type": "execute", "stmt": {"sql": sql, "args": params or []}}
            ]
        }
        
        resp = requests.post(
            f"{self.host}/v2/pipeline",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if resp.status_code != 200:
            raise Exception(f"Turso error: {resp.text}")
        
        return resp.json()

    def _init_db(self):
        """Initialize database tables"""
        try:
            if self.is_turso:
                self._execute_turso("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        mode TEXT DEFAULT 'coding',
                        config TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                self._execute_turso("""
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
                
                self._execute_turso("""
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
            else:
                self.client.execute("""CREATE TABLE IF NOT EXISTS sessions (...)""")
                self.client.execute("""CREATE TABLE IF NOT EXISTS chats (...)""")
                self.client.execute("""CREATE TABLE IF NOT EXISTS pool_usage (...)""")
                self.client.commit()
        
        except Exception as e:
            error_logger.log("DB_INIT_ERROR", str(e))

    def save_chat(self, session_id, chat_data):
        """Save chat to database"""
        try:
            sql = """
                INSERT INTO chats 
                (id, session_id, prompt, prompt_compressed, mode, context_mode,
                 final_answer, debate_data, tokens_used, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                chat_data["id"], session_id, chat_data["prompt"],
                chat_data.get("prompt_compressed", ""),
                chat_data.get("mode", "continue"),
                chat_data.get("context_mode", "continue"),
                chat_data.get("final_answer", ""),
                chat_data.get("debate_data", "{}"),
                chat_data.get("tokens_used", 0),
                chat_data.get("cost", 0.0)
            )
            
            if self.is_turso:
                self._execute_turso(sql, params)
            else:
                self.client.execute(sql, params)
                self.client.commit()
            return True
        
        except Exception as e:
            error_logger.log("DB_SAVE_ERROR", str(e))
            return False

    def get_session_chats(self, session_id, limit=50):
        """Get chats for a session"""
        try:
            if self.is_turso:
                result = self._execute_turso(
                    "SELECT * FROM chats WHERE session_id = ? ORDER BY created_at ASC LIMIT ?",
                    [session_id, limit]
                )
                # Parse Turso response
                rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
                chats = []
                for row in rows:
                    vals = [c.get("value") for c in row]
                    chats.append({
                        "id": vals[0], "session_id": vals[1], "prompt": vals[2],
                        "prompt_compressed": vals[3], "mode": vals[4],
                        "context_mode": vals[5], "final_answer": vals[6],
                        "debate_data": vals[7], "tokens_used": vals[8],
                        "cost": vals[9], "created_at": vals[10]
                    })
                return chats
            else:
                result = self.client.execute(
                    "SELECT * FROM chats WHERE session_id = ? ORDER BY created_at ASC LIMIT ?",
                    (session_id, limit)
                )
                return [dict(row) for row in result.fetchall()]
        
        except Exception as e:
            error_logger.log("DB_QUERY_ERROR", str(e))
            return []

    def create_session(self, session_id, name, mode="coding", config=None):
        """Create new session"""
        try:
            sql = "INSERT INTO sessions (id, name, mode, config) VALUES (?, ?, ?, ?)"
            params = (session_id, name, mode, json.dumps(config or {}))
            
            if self.is_turso:
                self._execute_turso(sql, params)
            else:
                self.client.execute(sql, params)
                self.client.commit()
            return True
        
        except Exception as e:
            error_logger.log("DB_SESSION_ERROR", str(e))
            return False

    def get_sessions(self):
        """Get all sessions"""
        try:
            if self.is_turso:
                result = self._execute_turso("SELECT * FROM sessions ORDER BY updated_at DESC")
                rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
                sessions = []
                for row in rows:
                    vals = [c.get("value") for c in row]
                    sessions.append({
                        "id": vals[0], "name": vals[1], "mode": vals[2],
                        "config": vals[3], "created_at": vals[4], "updated_at": vals[5]
                    })
                return sessions
            else:
                result = self.client.execute("SELECT * FROM sessions ORDER BY updated_at DESC")
                return [dict(row) for row in result.fetchall()]
        
        except Exception as e:
            error_logger.log("DB_QUERY_ERROR", str(e))
            return []

    def log_pool_usage(self, user_id, api_owner, provider, tokens, cost):
        """Log API pool usage"""
        try:
            sql = "INSERT INTO pool_usage (user_id, api_owner, provider, tokens, cost) VALUES (?, ?, ?, ?, ?)"
            params = (user_id, api_owner, provider, tokens, cost)
            
            if self.is_turso:
                self._execute_turso(sql, params)
            else:
                self.client.execute(sql, params)
                self.client.commit()
        
        except Exception as e:
            error_logger.log("POOL_LOG_ERROR", str(e))