"""
Database manager - SQLite Simple
"""
import sqlite3
import os
import json
import tempfile
from pathlib import Path

class RestoreValidationError(ValueError): pass
class RestoreOperationError(RuntimeError):
    def __init__(self,message,*,database_replaced=False): super().__init__(message); self.database_replaced=database_replaced
REQUIRED_RESTORE_SCHEMA={"sessions":{"id","name","mode","config","created_at","updated_at"},"chats":{"id","session_id","prompt","prompt_compressed","mode","context_mode","final_answer","debate_data","tokens_used","cost","created_at"}}
MAX_RESTORE_CANDIDATE_BYTES=100*1024*1024

def validate_restore_candidate(candidate_path):
    candidate_uri=Path(candidate_path).resolve().as_uri()
    try:
        conn=sqlite3.connect(f"{candidate_uri}?mode=ro",uri=True)
        try:
            if [row[0] for row in conn.execute("PRAGMA integrity_check")] != ["ok"]: raise RestoreValidationError("Backup integrity check failed.")
            tables={row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            for table,required in REQUIRED_RESTORE_SCHEMA.items():
                if table not in tables or not required.issubset({row[1] for row in conn.execute(f"PRAGMA table_info({table})")}): raise RestoreValidationError("Backup schema is incompatible.")
        finally: conn.close()
    except RestoreValidationError: raise
    except sqlite3.Error as exc: raise RestoreValidationError("Backup is not a valid SQLite database.") from exc

class DatabaseManager:
    def __init__(self,db_path): self.db_path=db_path; os.makedirs(os.path.dirname(db_path),exist_ok=True); self._init_db()
    def _init_db(self):
        conn=sqlite3.connect(self.db_path)
        conn.execute("""CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY,name TEXT,mode TEXT DEFAULT 'coding',config TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS chats (id TEXT PRIMARY KEY,session_id TEXT,prompt TEXT,prompt_compressed TEXT,mode TEXT DEFAULT 'continue',context_mode TEXT DEFAULT 'continue',final_answer TEXT,debate_data TEXT,tokens_used INTEGER DEFAULT 0,cost REAL DEFAULT 0.0,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        conn.commit(); conn.close()
    def export_bytes(self):
        directory=os.path.dirname(os.path.abspath(self.db_path)); fd,path=tempfile.mkstemp(prefix=".multimind-export-",suffix=".db",dir=directory); os.close(fd)
        try:
            source=sqlite3.connect(self.db_path); destination=sqlite3.connect(path)
            try: source.backup(destination)
            finally: destination.close(); source.close()
            validate_restore_candidate(path)
            with open(path,"rb") as f: return f.read()
        finally:
            try: os.remove(path)
            except FileNotFoundError: pass
    def restore_from_bytes(self,backup_bytes):
        if not isinstance(backup_bytes,bytes): raise RestoreValidationError("Backup content is invalid.")
        if len(backup_bytes)>MAX_RESTORE_CANDIDATE_BYTES: raise RestoreValidationError("Backup is too large to restore.")
        directory=os.path.dirname(os.path.abspath(self.db_path))
        try: fd,path=tempfile.mkstemp(prefix=".multimind-restore-",suffix=".db",dir=directory)
        except OSError as exc: raise RestoreOperationError("Backup staging failed.") from exc
        try:
            try:
                with os.fdopen(fd,"wb") as f:
                    if f.write(backup_bytes)!=len(backup_bytes): raise RestoreOperationError("Backup staging write was incomplete.")
            except OSError as exc: raise RestoreOperationError("Backup staging failed.") from exc
            validate_restore_candidate(path)
            try: os.replace(path,self.db_path)
            except OSError as exc: raise RestoreOperationError("Database replacement failed.") from exc
            path=None
            try: validate_restore_candidate(self.db_path)
            except (RestoreValidationError,OSError) as exc: raise RestoreOperationError("Database replacement could not be verified.",database_replaced=True) from exc
        finally:
            if path and os.path.exists(path):
                try: os.remove(path)
                except OSError: pass
        return True
    def save_chat(self,session_id,chat_data):
        conn=sqlite3.connect(self.db_path); conn.execute("INSERT INTO chats (id,session_id,prompt,prompt_compressed,mode,context_mode,final_answer,debate_data,tokens_used,cost) VALUES (?,?,?,?,?,?,?,?,?,?)",(chat_data["id"],session_id,chat_data["prompt"],chat_data.get("prompt_compressed",""),chat_data.get("mode","continue"),chat_data.get("context_mode","continue"),chat_data.get("final_answer",""),chat_data.get("debate_data","{}"),chat_data.get("tokens_used",0),chat_data.get("cost",0.0))); conn.commit(); conn.close(); return True
    def get_chat(self,session_id,chat_id):
        conn=sqlite3.connect(self.db_path); conn.row_factory=sqlite3.Row
        try:
            row=conn.execute("SELECT * FROM chats WHERE session_id=? AND id=?",(session_id,chat_id)).fetchone(); return dict(row) if row else None
        finally: conn.close()
    def update_chat_debate_data(self,session_id,chat_id,debate_data):
        conn=sqlite3.connect(self.db_path)
        try: cursor=conn.execute("UPDATE chats SET debate_data=? WHERE session_id=? AND id=?",(debate_data,session_id,chat_id)); conn.commit(); return cursor.rowcount==1
        finally: conn.close()
    def get_session_chats(self,session_id,limit=50):
        conn=sqlite3.connect(self.db_path); conn.row_factory=sqlite3.Row
        try: return [dict(row) for row in conn.execute("SELECT * FROM chats WHERE session_id=? ORDER BY created_at ASC LIMIT ?",(session_id,limit)).fetchall()]
        finally: conn.close()
    def get_session_chats_for_memory(self,session_id):
        conn=sqlite3.connect(self.db_path); conn.row_factory=sqlite3.Row
        try: return [dict(row) for row in conn.execute("SELECT * FROM chats WHERE session_id=? ORDER BY created_at ASC,rowid ASC",(session_id,)).fetchall()]
        finally: conn.close()
    def search_relevant_chats(self,query,limit=20,exclude_session_id=None):
        terms=[term for term in str(query or "").lower().split() if len(term)>=3][:8]
        if not terms: return []
        clauses=[]; params=[]
        for term in terms: clauses.append("(lower(prompt) LIKE ? OR lower(final_answer) LIKE ?)"); pattern=f"%{term}%"; params.extend([pattern,pattern])
        where=" OR ".join(clauses)
        if exclude_session_id: where=f"({where}) AND session_id != ?"; params.append(exclude_session_id)
        params.append(max(1,int(limit)))
        conn=sqlite3.connect(self.db_path); conn.row_factory=sqlite3.Row
        try: return [dict(row) for row in conn.execute(f"SELECT * FROM chats WHERE {where} ORDER BY created_at DESC,rowid DESC LIMIT ?",params).fetchall()]
        finally: conn.close()
    def create_session(self,session_id,name,mode="coding",config=None):
        conn=sqlite3.connect(self.db_path); conn.execute("INSERT INTO sessions (id,name,mode,config) VALUES (?,?,?,?)",(session_id,name,mode,json.dumps(config or {}))); conn.commit(); conn.close(); return True
    def get_sessions(self):
        conn=sqlite3.connect(self.db_path); conn.row_factory=sqlite3.Row
        try: return [dict(row) for row in conn.execute("SELECT * FROM sessions ORDER BY updated_at DESC").fetchall()]
        finally: conn.close()
    def get_session_operating_state(self,session_id):
        conn=sqlite3.connect(self.db_path)
        try:
            row=conn.execute("SELECT config FROM sessions WHERE id=?",(session_id,)).fetchone()
            if not row: return {}
            try: config=json.loads(row[0] or "{}")
            except (TypeError,ValueError): return {}
            return dict(config.get("operating_state") or {})
        finally: conn.close()
    def set_session_operating_state(self,session_id,state):
        conn=sqlite3.connect(self.db_path)
        try:
            row=conn.execute("SELECT config FROM sessions WHERE id=?",(session_id,)).fetchone()
            if not row: return False
            try: config=json.loads(row[0] or "{}")
            except (TypeError,ValueError): config={}
            config["operating_state"]=dict(state or {}); cursor=conn.execute("UPDATE sessions SET config=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(json.dumps(config),session_id)); conn.commit(); return cursor.rowcount==1
        finally: conn.close()
