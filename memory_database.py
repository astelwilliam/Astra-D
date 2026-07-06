"""SQLite persistence layer for Astra-D semantic memories."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from semantic_memory import MemoryEntry


class MemoryDatabase:
    """SQLite storage backend for semantic memories."""

    def __init__(self, db_path: str = "astra_memory.db") -> None:
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        """Create required database tables if they do not exist."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                entities TEXT,
                noun_chunks TEXT,
                keywords TEXT,
                timestamp TEXT,
                importance REAL
            )
            """
        )

        self.connection.commit()

    def save_memory(self, memory: MemoryEntry) -> None:
        """Persist a MemoryEntry to SQLite."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO memories (
                id,
                text,
                entities,
                noun_chunks,
                keywords,
                timestamp,
                importance
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory.id,
                memory.text,
                json.dumps(memory.entities),
                json.dumps(memory.noun_chunks),
                json.dumps(memory.keywords),
                memory.timestamp.isoformat(),
                memory.importance,
            ),
        )

        self.connection.commit()

    def load_memories(self) -> list[MemoryEntry]:
        """Load all stored memories from SQLite."""

        cursor = self.connection.cursor()

        rows = cursor.execute(
            """
            SELECT
                id,
                text,
                entities,
                noun_chunks,
                keywords,
                timestamp,
                importance
            FROM memories
            ORDER BY timestamp
            """
        ).fetchall()

        memories: list[MemoryEntry] = []

        for row in rows:
            memories.append(
                MemoryEntry(
                    id=row[0],
                    text=row[1],
                    entities=json.loads(row[2]),
                    noun_chunks=json.loads(row[3]),
                    keywords=json.loads(row[4]),
                    timestamp=datetime.fromisoformat(row[5]),
                    importance=row[6],
                )
            )

        return memories

    def close(self) -> None:
        """Close the SQLite connection."""
        self.connection.close()