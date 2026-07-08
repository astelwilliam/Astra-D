"""Astra-D: production-ready local AI assistant."""

from astra_d.memory.engine import MemoryEngine
from retrieval_engine import RetrievalEngine
from prompt_builder import PromptBuilder

from astra_d.conversation.database import ConversationDatabase
from astra_d.conversation.manager import ConversationManager


import os
import re
import shlex
import sys
from typing import Callable

try:
    import ollama
except Exception as exc:  # noqa: BLE001 - keep CLI importable when deps are missing
    _OLLAMA_IMPORT_ERROR = str(exc)

    class _MissingOllama:
        def chat(self, *args, **kwargs):
            raise RuntimeError(f"Ollama dependency is unavailable: {_OLLAMA_IMPORT_ERROR}")

    ollama = _MissingOllama()


import filesearch
import memory
import notes
import tasks
import pdf_utils
import retrieval


MODEL = "qwen2.5:3b"

MEMORY_ENGINE = MemoryEngine()
RETRIEVAL_ENGINE = RetrievalEngine(MEMORY_ENGINE.semantic_memory)
PROMPT_BUILDER = PromptBuilder(RETRIEVAL_ENGINE)
CONVERSATION_DB = ConversationDatabase()
CONVERSATION_MANAGER = ConversationManager(CONVERSATION_DB)

ACTIVE_DOCUMENT_PATH = None

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
  loadpdf <file>               Chunk and index a PDF for semantic retrieval
  retrieve <query>             Return top 5 semantic matches from loaded PDF
  ask <question>               Ask a question using top 5 semantic matches
  quit | exit                  Exit Astra-D

  summarize <file>            Summarize a PDF
  doc                         Show loaded document preview

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


def _handle_loadpdf_command(args):
    global ACTIVE_DOCUMENT_PATH

    if not args:
        return "Usage: loadpdf <file>"

    file_path = args[0]

    try:
        text = pdf_utils.read_pdf(file_path)

        if not text.strip():
            return "PDF contains no extractable text."

        hash_value = pdf_utils.file_hash(file_path)
        chunk_count = retrieval.index_document(file_path, text, file_hash=hash_value)

        ACTIVE_DOCUMENT_PATH = os.path.abspath(file_path)

        return (
            f"Loaded PDF: {file_path}\n"
            f"Indexed {chunk_count} chunks (cached/skipped re-embedding if unchanged)."
        )

    except Exception as e:
        return f"Error loading PDF: {e}"


def _handle_ask_command(args):
    global ACTIVE_DOCUMENT_PATH

    if ACTIVE_DOCUMENT_PATH is None:
        return "No PDF loaded. Use: loadpdf <file>"

    question = " ".join(args).strip()

    if not question:
        return "Usage: ask <question>"

    try:
        matches = retrieval.semantic_search(
            question,
            top_k=5,
            source=ACTIVE_DOCUMENT_PATH,
        )

        if not matches:
            return "ANSWER NOT PRESENT IN DOCUMENT"

        best_distance = matches[0].distance

        if best_distance is None:
            return "ANSWER NOT PRESENT IN DOCUMENT"

        if best_distance > 0.65:
            return "ANSWER NOT PRESENT IN DOCUMENT"

        context = "\n\n".join(
            f"[Chunk {m.chunk_index}]\n{m.text}"
            for m in matches
        )

        is_mcq = (
            len(
                re.findall(
                    r"[A-D][\.\)]",
                    question.upper()
                )
            ) >= 4
        )

        if is_mcq:
            prompt = prompt = f"""
You are answering questions ONLY from the supplied document excerpts.

Rules:

- Use only the supplied context.
- If the answer exists in the context, quote or summarize it.
- If the user asks for a question number (for example "Question 10"),
  return the exact wording of that question from the context.
- If multiple versions exist, list them separately with their chunk numbers.
- If it is absent from the supplied context, reply exactly:

ANSWER NOT PRESENT IN DOCUMENT

Context:

{context}

User question:

{question}

Answer:
"""

        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            options={
                "temperature": 0,
            },
        )

        return response["message"]["content"]

    except Exception as e:
        return f"Error: {e}"


def _format_semantic_matches(matches: list[retrieval.SemanticMatch]) -> str:
    if not matches:
        return "No semantic matches found."

    lines: list[str] = []
    for index, match in enumerate(matches, start=1):
        source = match.source or "unknown source"
        distance = f", distance {match.distance:.4f}" if match.distance is not None else ""
        lines.append(f"{index}. {source} chunk {match.chunk_index}{distance}")
        lines.append(match.text)
    return "\n\n".join(lines)


def _handle_retrieve_command(args: list[str]) -> str:
    global ACTIVE_DOCUMENT_PATH

    if ACTIVE_DOCUMENT_PATH is None:
        return "No PDF loaded. Use: loadpdf <file>"

    query = " ".join(args)
    if not query.strip():
        return "Usage: retrieve <query>"

    matches = retrieval.semantic_search(
        query,
        top_k=5,
        source=ACTIVE_DOCUMENT_PATH,
    )
    return _format_semantic_matches(matches)



def _build_memory_context(message: str) -> str:
    """Build a text context from relevant semantic memories."""

    memories = RETRIEVAL_ENGINE.retrieve(message, top_k=3)

    if not memories:
        return ""

    lines = ["Relevant memories:"]

    for memory in memories:
        lines.append(f"- {memory.text}")

    return "\n".join(lines)



def _handle_chat(message: str) -> str:
    if CONVERSATION_MANAGER.get_active_conversation() is None:
        if CONVERSATION_MANAGER.resume_last_conversation() is None:
            CONVERSATION_MANAGER.new_conversation("Chat")

    history = CONVERSATION_MANAGER.get_history()

    enriched_prompt = PROMPT_BUILDER.build(message)

    reply = chat_with_ollama(enriched_prompt, history)

    CONVERSATION_MANAGER.add_user_message(message)
    CONVERSATION_MANAGER.add_assistant_message(reply)

    MEMORY_ENGINE.remember(message)

    return reply


def _handle_doc_command(args):
    global ACTIVE_DOCUMENT_PATH

    if ACTIVE_DOCUMENT_PATH is None:
        return "No document loaded."

    try:
        text = pdf_utils.read_pdf(ACTIVE_DOCUMENT_PATH)  # cache hit, no re-OCR
    except Exception as e:
        return f"Error reading cached document: {e}"

    preview = text[:1000]
    if len(text) > 1000:
        preview += "\n\n[Document Preview Truncated]"

    return f"Loaded Document:\n{ACTIVE_DOCUMENT_PATH}\n\n{preview}"


def dispatch(line: str) -> str | None:
    """Process one user input line. Returns output text or None to exit."""
    stripped = line.strip()

    if not stripped:
        return ""

    lowered = stripped.lower()

    if lowered in {"quit", "exit"}:
        return None

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

    if command == "loadpdf":
        return _handle_loadpdf_command(args)

    if command == "ask":
        return _handle_ask_command(args)

    if command == "retrieve":
        return _handle_retrieve_command(args)

    if command == "doc":
        return _handle_doc_command(args)

    # If no command matches, treat the input as a chat message.
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
    print("RUNNING FILE:", __file__)
    """Start the interactive Astra-D assistant."""
    memory.load_conversations()
    notes.load_notes()
    tasks.load_tasks()

    if CONVERSATION_MANAGER.resume_last_conversation() is None:
       CONVERSATION_MANAGER.new_conversation("Chat")

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