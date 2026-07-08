"""SQLite database for Astra-D conversations."""

from __future__ import annotations

import sqlite3
from datetime import datetime


class ConversationDatabase:
    """Store conversations and messages."""

    def __init__(self, db_path: str = "data/conversations.db") -> None:
         self._connection = sqlite3.connect(db_path)
         self._connection.row_factory = sqlite3.Row
         self._connection.execute("PRAGMA foreign_keys = ON")
         self._create_tables()

    def _create_tables(self) -> None:
        """Create required tables if they do not exist."""

        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            )
            """
        )

        self._connection.commit()

    def create_conversation(self, title: str) -> int:
        """Create a new conversation."""

        now = datetime.now().isoformat()

        cursor = self._connection.execute(
            """
            INSERT INTO conversations(title, created_at, updated_at)
            VALUES (?, ?, ?)
            """,
            (title, now, now),
        )

        self._connection.commit()

        return cursor.lastrowid



    def get_conversation(self, conversation_id: int) -> dict | None:
        """Return a conversation by ID."""

        cursor = self._connection.execute(
           """
           SELECT
               id,
               title,
               created_at,
               updated_at
           FROM conversations
           WHERE id = ?
           """,
           (conversation_id,),
        )

        row = cursor.fetchone()

        if row is None:
           return None

        return dict(row)

    def get_last_conversation(self) -> dict | None:
        """Return the most recently updated conversation."""

        cursor = self._connection.execute(
            """
            SELECT
                id,
                title,
                created_at,
                updated_at
            FROM conversations
            ORDER BY updated_at DESC, id DESC
            LIMIT 1
            """
        )
    
        row = cursor.fetchone()
    
        if row is None:
            return None
    
        return dict(row)

    

    def list_conversations(self) -> list[dict]:
        """Return all conversations."""

        cursor = self._connection.execute(
            """
            SELECT id, title
            FROM conversations
            ORDER BY id
            """
        )

        return [dict(row) for row in cursor.fetchall()]

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ) -> None:
        """Add a message to a conversation."""

        now = datetime.now().isoformat()

        self._connection.execute(
            """
            INSERT INTO messages(
                conversation_id,
                role,
                content,
                timestamp
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                conversation_id,
                role,
                content,
                now,
            ),
        )

        self._connection.execute(
            """
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ?
            """,
            (now, conversation_id),
        )

        self._connection.commit()

    def get_messages(self, conversation_id: int) -> list[dict]:
        """Return all messages for a conversation."""

        cursor = self._connection.execute(
            """
            SELECT
                role,
                content,
                timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (conversation_id,),
        )

        return [dict(row) for row in cursor.fetchall()]


    def delete_conversation(self, conversation_id: int) -> None:
        """Delete a conversation."""
    
        self._connection.execute(
            """
            DELETE FROM conversations
            WHERE id = ?
            """,
            (conversation_id,),
        )
    
        self._connection.commit()
    

    def close(self) -> None:
        """Close the database."""

        self._connection.close()