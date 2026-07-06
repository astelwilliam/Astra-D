"""SQLite persistence layer for Astra-D semantic memories."""

from __future__ import annotations

import sqlite3
from pathlib import Path


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

    def close(self) -> None:
        """Close the SQLite connection."""
        self.connection.close()