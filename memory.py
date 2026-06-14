"""Conversation memory persisted to memory.json."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

MEMORY_FILENAME = "memory.json"


class MemoryError(Exception):
    """Raised when memory storage operations fail."""


def _data_dir() -> Path:
    override = os.environ.get("ASTRA_D_DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "data"


def memory_path() -> Path:
    return _data_dir() / MEMORY_FILENAME


def _default_payload() -> dict[str, Any]:
    return {"conversations": []}


def _ensure_file() -> None:
    path = memory_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        save_conversations([])


def load_conversations() -> list[dict[str, str]]:
    """Load conversation history from memory.json."""
    _ensure_file()
    path = memory_path()
    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise MemoryError(f"Invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise MemoryError(f"Unable to read {path}: {exc}") from exc

    conversations = payload.get("conversations", [])
    if not isinstance(conversations, list):
        raise MemoryError("memory.json must contain a 'conversations' list.")
    return conversations


def save_conversations(conversations: list[dict[str, str]]) -> None:
    """Persist conversation history to memory.json."""
    path = memory_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"conversations": conversations}
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
    except OSError as exc:
        raise MemoryError(f"Unable to write {path}: {exc}") from exc


def add_message(role: str, content: str) -> list[dict[str, str]]:
    """Append a message and save updated history."""
    if role not in {"user", "assistant", "system"}:
        raise ValueError(f"Unsupported role: {role}")
    if not content.strip():
        raise ValueError("Message content cannot be empty.")

    conversations = load_conversations()
    conversations.append({"role": role, "content": content})
    save_conversations(conversations)
    return conversations


def clear_conversations() -> None:
    """Remove all stored conversation history."""
    save_conversations([])
