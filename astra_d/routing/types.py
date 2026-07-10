"""Intent types for Astra-D."""

from enum import Enum, auto


class Intent(Enum):
    CHAT = auto()

    MEMORY = auto()

    NOTE = auto()

    TASK = auto()

    DOCUMENT = auto()

    SEARCH = auto()

    HELP = auto()

    EXIT = auto()

    UNKNOWN = auto()