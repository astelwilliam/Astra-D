"""Recursive filename search."""

from __future__ import annotations

import os
from pathlib import Path


class FileSearchError(Exception):
    """Raised when file search cannot be performed."""
    pass


IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
}


def file_search(directory_path: str | Path, search_string: str) -> list[str]:
    """
    Search files recursively under directory_path.

    Returns absolute paths whose filenames contain search_string.
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
        for current_root, dirs, files in os.walk(root):

            dirs[:] = [
                d for d in dirs
                if d not in IGNORE_DIRS
            ]

            for filename in files:
                if needle in filename.lower():
                    results.append(
                        str(Path(current_root, filename).resolve())
                    )

    except OSError as exc:
        raise FileSearchError(
            f"Search failed: {exc}"
        ) from exc

    results.sort()
    return results


if __name__ == "__main__":
    directory = input("Directory: ")
    query = input("Search for: ")

    try:
        matches = file_search(directory, query)

        if matches:
            print("\nFound:")
            for match in matches:
                print(match)
        else:
            print("\nNo files found.")

    except Exception as exc:
        print(f"Error: {exc}")