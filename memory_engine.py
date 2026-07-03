"""Memory engine for Astra-D.

Thin orchestration layer that connects NLP preprocessing (memory_nlp)
to in-RAM storage (semantic_memory). Contains no databases, no web
frameworks, no embeddings, and no machine learning of its own — it
simply wires analysis to storage.
"""

from __future__ import annotations

from memory_nlp import analyze
from semantic_memory import MemoryEntry, SemanticMemory


class MemoryEngine:
    """Coordinates text analysis and semantic memory storage.

    Each MemoryEngine owns a single SemanticMemory instance. Callers
    hand it raw text; it runs NLP analysis and persists the result
    in RAM as a MemoryEntry.
    """

    def __init__(self) -> None:
        """Initialize the engine with a fresh, empty SemanticMemory."""
        self._memory = SemanticMemory()

    def remember(self, text: str) -> MemoryEntry:
        """Analyze text and store it as a new memory.

        Args:
            text: The raw text to remember.

        Returns:
            The MemoryEntry that was created and stored.
        """
        nlp_result = analyze(text)
        return self._memory.store(text, nlp_result)

    def count(self) -> int:
        """Return the total number of stored memories.

        Returns:
            The number of MemoryEntry records currently stored.
        """
        return self._memory.count()

    def all_memories(self) -> list[MemoryEntry]:
        """Return every stored memory.

        Returns:
            A list of all MemoryEntry records currently stored.
        """
        return self._memory.get_all()