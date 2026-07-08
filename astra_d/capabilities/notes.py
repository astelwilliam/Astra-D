"""Note management persisted to notes.json."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOTES_FILENAME = "notes.json"


class NotesError(Exception):
    """Raised when note storage operations fail."""


def _data_dir() -> Path:
    override = os.environ.get("ASTRA_D_DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "data"


def notes_path() -> Path:
    return _data_dir() / NOTES_FILENAME


def _default_payload() -> dict[str, Any]:
    return {"notes": []}


def _ensure_file() -> None:
    path = notes_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        _write_payload(_default_payload())


def _read_payload() -> dict[str, Any]:
    _ensure_file()
    path = notes_path()
    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise NotesError(f"Invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise NotesError(f"Unable to read {path}: {exc}") from exc

    if not isinstance(payload.get("notes"), list):
        raise NotesError("notes.json must contain a 'notes' list.")
    return payload


def _write_payload(payload: dict[str, Any]) -> None:
    path = notes_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
    except OSError as exc:
        raise NotesError(f"Unable to write {path}: {exc}") from exc


def load_notes() -> list[dict[str, Any]]:
    """Return all notes."""
    return _read_payload()["notes"]


def create_note(content: str) -> dict[str, Any]:
    """Create a note and persist it."""
    if not content.strip():
        raise ValueError("Note content cannot be empty.")

    payload = _read_payload()
    note = {
        "id": str(uuid.uuid4()),
        "content": content.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    payload["notes"].append(note)
    _write_payload(payload)
    return note


def view_notes() -> list[dict[str, Any]]:
    """Return notes for display."""
    return load_notes()


def delete_note(note_id: str) -> bool:
    """Delete a note by id. Returns True if a note was removed."""
    payload = _read_payload()
    original_count = len(payload["notes"])
    payload["notes"] = [note for note in payload["notes"] if note.get("id") != note_id]
    if len(payload["notes"]) == original_count:
        return False
    _write_payload(payload)
    return True
