"""Task management persisted to tasks.json."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASKS_FILENAME = "tasks.json"


class TasksError(Exception):
    """Raised when task storage operations fail."""


def _data_dir() -> Path:
    override = os.environ.get("ASTRA_D_DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "data"


def tasks_path() -> Path:
    return _data_dir() / TASKS_FILENAME


def _default_payload() -> dict[str, Any]:
    return {"tasks": []}


def _ensure_file() -> None:
    path = tasks_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        _write_payload(_default_payload())


def _read_payload() -> dict[str, Any]:
    _ensure_file()
    path = tasks_path()
    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise TasksError(f"Invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise TasksError(f"Unable to read {path}: {exc}") from exc

    if not isinstance(payload.get("tasks"), list):
        raise TasksError("tasks.json must contain a 'tasks' list.")
    return payload


def _write_payload(payload: dict[str, Any]) -> None:
    path = tasks_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
    except OSError as exc:
        raise TasksError(f"Unable to write {path}: {exc}") from exc


def load_tasks() -> list[dict[str, Any]]:
    """Return all tasks."""
    return _read_payload()["tasks"]


def create_task(title: str, description: str = "") -> dict[str, Any]:
    """Create a task and persist it."""
    if not title.strip():
        raise ValueError("Task title cannot be empty.")

    payload = _read_payload()
    task = {
        "id": str(uuid.uuid4()),
        "title": title.strip(),
        "description": description.strip(),
        "completed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }
    payload["tasks"].append(task)
    _write_payload(payload)
    return task


def complete_task(task_id: str) -> bool:
    """Mark a task complete. Returns True if updated."""
    payload = _read_payload()
    updated = False
    for task in payload["tasks"]:
        if task.get("id") == task_id:
            task["completed"] = True
            task["completed_at"] = datetime.now(timezone.utc).isoformat()
            updated = True
            break
    if updated:
        _write_payload(payload)
    return updated


def delete_task(task_id: str) -> bool:
    """Delete a task by id. Returns True if removed."""
    payload = _read_payload()
    original_count = len(payload["tasks"])
    payload["tasks"] = [task for task in payload["tasks"] if task.get("id") != task_id]
    if len(payload["tasks"]) == original_count:
        return False
    _write_payload(payload)
    return True
