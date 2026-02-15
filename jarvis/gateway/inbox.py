"""SQLite-backed inbox queue for Jarvis gateway."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class InboxStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS inbox_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT,
                    workspace TEXT,
                    channel TEXT,
                    mode TEXT,
                    status TEXT,
                    user_text TEXT,
                    response_text TEXT NULL,
                    error_text TEXT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def insert_pending(self, workspace: str, channel: str, mode: str, user_text: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO inbox_messages (created_at, workspace, channel, mode, status, user_text)
                VALUES (?, ?, ?, ?, 'pending', ?)
                """,
                (self._now_iso(), workspace, channel, mode, user_text),
            )
            conn.commit()
            return int(cur.lastrowid)

    def set_status(self, inbox_id: int, status: str, response_text: Optional[str] = None, error_text: Optional[str] = None) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE inbox_messages
                SET status = ?, response_text = ?, error_text = ?
                WHERE id = ?
                """,
                (status, response_text, error_text, inbox_id),
            )
            conn.commit()

    def get(self, inbox_id: int):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM inbox_messages WHERE id = ?", (inbox_id,)).fetchone()
            return dict(row) if row else None
