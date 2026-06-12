import sqlite3
import json
import os
from datetime import datetime
from typing import Optional


class SessionDB:
    def __init__(self, db_path: str = "sessions/aiguard.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    project_path TEXT,
                    timestamp TEXT NOT NULL,
                    risk_score REAL DEFAULT 0.0,
                    files_read TEXT DEFAULT '[]',
                    blocked_attempts TEXT DEFAULT '[]',
                    status TEXT DEFAULT 'active'
                )
            """)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def create_session(self, prompt: str, project_path: str = ".") -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO sessions (prompt, project_path, timestamp) VALUES (?, ?, ?)",
                (prompt, project_path, datetime.now().isoformat())
            )
            return cur.lastrowid

    def log_file_read(self, session_id: int, file_path: str):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT files_read FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            if row:
                files = json.loads(row[0])
                files.append(file_path)
                conn.execute(
                    "UPDATE sessions SET files_read = ? WHERE id = ?",
                    (json.dumps(files), session_id)
                )
