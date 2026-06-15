"""Astra-D: production-ready local AI assistant."""

from __future__ import annotations

import os
import shlex
import sys
from typing import Callable

import ollama


import filesearch
import memory
import notes
import tasks
import pdf_utils


MODEL = "qwen2.5:3b"
SYSTEM_PROMPT = (
    "You are Astra-D, a helpful local AI assistant. "
    "Be concise, practical, and friendly."
)


class OllamaChatError(Exception):
    """Raised when Ollama chat requests fail."""


def chat_with_ollama(message: str, history: list[dict[str, str]]) -> str:
    """Send a message to Ollama with full conversation history."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history, {"role": "user", "content": message}]
    try:
        response = ollama.chat(model=MODEL, messages=messages)
    except Exception as exc:  # noqa: BLE001 - surface provider errors to CLI
        raise OllamaChatError(f"Ollama request failed: {exc}") from exc

    content = response.get("message", {}).get("content")
    if not content:
        raise OllamaChatError("Ollama returned an empty response.")
    return content


def _print_help() -> str:
    return """
Commands:
  help                         Show this help
  chat <message>               Send a message to the assistant
  history                      Show saved conversation history
  clear                        Clear conversation history

  note add <content>           Create a note
  note list                    View all notes
  note delete <id>             Delete a note by id

  task add <title> [--desc T]  Create a task
  task list                    View all tasks
  task complete <id>           Mark a task complete
  task delete <id>             Delete a task

  search <directory> <query>   Search filenames recursively
  pdf <file>                   Read a PDF file
  quit | exit                  Exit Astra-D

Tips:
  - Plain text (without a command) is treated as chat input.
  - Conversation history is saved automatically in data/memory.json.
""".strip()


def _format_notes() -> str:
    items = notes.view_notes()
    if not items:
        return "No notes yet."
    lines = []
    for note in items:
        lines.append(f"[{note['id']}] {note['content']}")
    return "\n".join(lines)


def _format_tasks() -> str:
    items = tasks.load_tasks()
    if not items:
        return "No tasks yet."
    lines = []
    for task in items:
        status = "done" if task.get("completed") else "open"
        lines.append(f"[{task['id']}] ({status}) {task['title']}")
        if task.get("description"):
            lines.append(f"    {task['description']}")
    return "\n".join(lines)


def _handle_note_command(args: list[str]) -> str:
    if not args:
        raise ValueError("Usage: note add <content> | note list | note delete <id>")

    action = args[0].lower()
    if action == "add":
        content = " ".join(args[1:]).strip()
        note = notes.create_note(content)
        return f"Note created: [{note['id']}] {note['content']}"
    if action == "list":
        return _format_notes()
    if action == "delete":
        if len(args) < 2:
            raise ValueError("Usage: note delete <id>")
        deleted = notes.delete_note(args[1])
        return "Note deleted." if deleted else f"No note found with id {args[1]}"
    raise ValueError(f"Unknown note command: {action}")


def _handle_task_command(args: list[str]) -> str:
    if not args:
        raise ValueError("Usage: task add <title> [--desc text] | task list | task complete <id> | task delete <id>")

    action = args[0].lower()
    if action == "add":
        title_parts: list[str] = []
        description = ""
        index = 1
        while index < len(args):
            if args[index] == "--desc" and index + 1 < len(args):
                description = args[index + 1]
                index += 2
            else:
                title_parts.append(args[index])
                index += 1
        task = tasks.create_task(" ".join(title_parts), description)
        return f"Task created: [{task['id']}] {task['title']}"
    if action == "list":
        return _format_tasks()
    if action == "complete":
        if len(args) < 2:
            raise ValueError("Usage: task complete <id>")
        completed = tasks.complete_task(args[1])
        return "Task completed." if completed else f"No task found with id {args[1]}"
    if action == "delete":
        if len(args) < 2:
            raise ValueError("Usage: task delete <id>")
        deleted = tasks.delete_task(args[1])
        return "Task deleted." if deleted else f"No task found with id {args[1]}"
    raise ValueError(f"Unknown task command: {action}")


def _handle_search_command(args: list[str]) -> str:
    if len(args) < 2:
        raise ValueError("Usage: search <directory> <query>")
    directory = args[0]
    query = " ".join(args[1:])
    matches = filesearch.file_search(directory, query)
    if not matches:
        return "No matching files found."
    return "\n".join(matches)

def _handle_pdf_command(args: list[str]) -> str:
    if not args:
        raise ValueError("Usage: pdf <file>")

    file_path = args[0]

    text = pdf_utils.read_pdf(file_path)

    if not text:
        return "No text found in PDF."

    if len(text) > 3000:
        text = text[:3000] + "\n\n[Output truncated]"

    return text

def _handle_summarize_command(args):
    if not args:
        return "Usage: summarize <pdf-file>"

    file_path = " ".join(args)

    try:
        text = pdf_utils.read_pdf(file_path)

        prompt = f"""
Summarize the following PDF:

{text[:10000]}
"""

        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        return response["message"]["content"]

    except Exception as e:
        return f"Error: {e}"
    


def _handle_askpdf_command(args):
    if len(args) < 2:
        return "Usage: askpdf <file> <question>"

    file_path = args[0]
    question = " ".join(args[1:])

    try:
        text = pdf_utils.read_pdf(file_path)

        prompt = f"""
You are analyzing a PDF document.

Use ONLY the document content.

If the answer is found, provide a detailed response.

If the document is a question bank, identify:
- important theories
- important concepts
- repeated topics
- likely exam questions

DOCUMENT:
{text[:30000]}

QUESTION:
{question}
"""

        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        return response["message"]["content"]

    except Exception as e:
        return f"Error: {e}"


def _handle_chat(message: str) -> str:
    history = memory.load_conversations()
    reply = chat_with_ollama(message, history)
    memory.add_message("user", message)
    memory.add_message("assistant", reply)
    return reply


def dispatch(line: str) -> str | None:
    """Process one user input line. Returns output text or None to exit."""
    stripped = line.strip()

    if not stripped:
        return ""

    lowered = stripped.lower()

    if lowered in {"quit", "exit"}:
        return None

    if lowered.startswith("my name is "):
        name = stripped[11:].strip()
        memory.remember("name", name)
        return f"I'll remember that. Your name is {name}."

    if lowered == "what is my name":
        name = memory.recall("name")

        if name:
            return f"Your name is {name}."

        return "I don't know your name yet."

    try:
        parts = shlex.split(stripped, posix=(os.name != "nt"))
    except ValueError as exc:
        raise ValueError(f"Invalid input: {exc}") from exc

    command = parts[0].lower()
    args = parts[1:]

    handlers: dict[str, Callable[[], str]] = {
        "help": _print_help,
        "history": lambda: _format_history(),
        "clear": _clear_history,
    }

    if command in handlers:
        return handlers[command]()

    if command == "chat":
        message = " ".join(args).strip()

        if not message:
            raise ValueError("Usage: chat <message>")

        return _handle_chat(message)

    if command == "note":
        return _handle_note_command(args)

    if command == "task":
        return _handle_task_command(args)

    if command == "search":
        return _handle_search_command(args)

    if command == "pdf":
        return _handle_pdf_command(args)

    if command == "summarize":
        return _handle_summarize_command(args)
    
    if command == "askpdf":
        return _handle_askpdf_command(args)

    return _handle_chat(stripped)


def _format_history() -> str:
    history = memory.load_conversations()
    if not history:
        return "No conversation history yet."
    lines = []
    for item in history:
        role = item.get("role", "unknown").upper()
        content = item.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _clear_history() -> str:
    memory.clear_conversations()
    return "Conversation history cleared."


def run() -> None:
    """Start the interactive Astra-D assistant."""
    memory.load_conversations()
    notes.load_notes()
    tasks.load_tasks()

    print("Astra-D local assistant")
    print(f"Model: {MODEL}")
    print("Type 'help' for commands or chat directly. Type 'quit' to exit.\n")

    while True:
        try:
            line = input("astra-d> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        try:
            result = dispatch(line)
        except (ValueError, memory.MemoryError, notes.NotesError, tasks.TasksError, filesearch.FileSearchError, OllamaChatError) as exc:
            print(f"Error: {exc}")
            continue

        if result is None:
            print("Goodbye.")
            break

        if result:
            print(result)
            print()


if __name__ == "__main__":
    try:
        run()
    except memory.MemoryError as exc:
        print(f"Fatal memory error: {exc}", file=sys.stderr)
        sys.exit(1)
