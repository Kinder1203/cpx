"""Local SQLite persistence for resumable CPX educational sessions."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SessionStore:
    """Persist current session state and an append-only event audit trail."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute("PRAGMA journal_mode=WAL")
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        case_id TEXT NOT NULL,
                        engine_state_json TEXT NOT NULL,
                        completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
                        learner_assessment_json TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS session_events (
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS idx_session_events_session
                        ON session_events(session_id, event_id);
                    """
                )

    def save(
        self,
        session_id: str,
        case_id: str,
        engine_state: dict[str, object],
        *,
        completed: bool,
        learner_assessment: dict[str, str] | None,
        event_type: str,
        event_payload: dict[str, object] | None = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        state_json = json.dumps(engine_state, ensure_ascii=False, separators=(",", ":"))
        assessment_json = (
            json.dumps(learner_assessment, ensure_ascii=False, separators=(",", ":"))
            if learner_assessment is not None
            else None
        )
        payload_json = json.dumps(event_payload or {}, ensure_ascii=False, separators=(",", ":"))
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                """
                INSERT INTO sessions (
                    session_id, case_id, engine_state_json, completed,
                    learner_assessment_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    case_id = excluded.case_id,
                    engine_state_json = excluded.engine_state_json,
                    completed = excluded.completed,
                    learner_assessment_json = excluded.learner_assessment_json,
                    updated_at = excluded.updated_at
                """,
                    (
                        session_id,
                        case_id,
                        state_json,
                        int(completed),
                        assessment_json,
                        now,
                        now,
                    ),
                )
                connection.execute(
                """
                INSERT INTO session_events (session_id, event_type, payload_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, event_type, payload_json, now),
                )

    def load_all(self) -> tuple[dict[str, Any], ...]:
        restored: list[dict[str, Any]] = []
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT session_id, case_id, engine_state_json, completed,
                       learner_assessment_json
                FROM sessions
                ORDER BY created_at
                """
            ).fetchall()
        for row in rows:
            try:
                engine_state = json.loads(row["engine_state_json"])
                assessment = (
                    json.loads(row["learner_assessment_json"])
                    if row["learner_assessment_json"] is not None
                    else None
                )
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            if not isinstance(engine_state, dict):
                continue
            if assessment is not None and not isinstance(assessment, dict):
                continue
            restored.append(
                {
                    "session_id": row["session_id"],
                    "case_id": row["case_id"],
                    "engine_state": engine_state,
                    "completed": bool(row["completed"]),
                    "learner_assessment": assessment,
                }
            )
        return tuple(restored)
