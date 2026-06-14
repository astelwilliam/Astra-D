"""Recursive filename search."""

from __future__ import annotations

import os
from pathlib import Path


class FileSearchError(Exception):
    """Raised when file search cannot be performed."""


def file_search(directory_path: str | Path, search_string: str) -> list[str]:
    """
    Search files recursively under directory_path.

    Returns absolute paths whose filenames contain search_string (case-insensitive).
    """
    if not search_string.strip():
        raise ValueError("Search string cannot be empty.")

    root = Path(directory_path).expanduser().resolve()
    if not root.exists():
        raise FileSearchError(f"Directory does not exist: {root}")
    if not root.is_dir():
        raise FileSearchError(f"Path is not a directory: {root}")

    needle = search_string.lower()
    results: list[str] = []
    try:
        for current_root, _, files in os.walk(root):
            for filename in files:
                if needle in filename.lower():
                    results.append(str(Path(current_root, filename).resolve()))
    except OSError as exc:
        raise FileSearchError(f"Unable to search {root}: {exc}") from exc

    return sorted(results)
