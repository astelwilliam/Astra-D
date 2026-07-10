"""Intent detection."""

from astra_d.routing.types import Intent


COMMANDS = {
    "help": Intent.HELP,
    "exit": Intent.EXIT,
    "quit": Intent.EXIT,

    "note": Intent.NOTE,
    "task": Intent.TASK,

    "pdf": Intent.DOCUMENT,
    "search": Intent.SEARCH,

    "remember": Intent.MEMORY,
}


def detect_intent(text: str) -> Intent:
    text = text.strip().lower()

    if not text:
        return Intent.UNKNOWN

    command = text.split(maxsplit=1)[0]

    return COMMANDS.get(command, Intent.CHAT)