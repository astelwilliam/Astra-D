"""Memory engine for Astra-D.

Thin orchestration layer that connects NLP preprocessing (memory_nlp)
to in-RAM storage (semantic_memory). Contains no databases, no web
frameworks, no embeddings, and no machine learning of its own — it
simply wires analysis to storage.
"""



from __future__ import annotations

from memory_database import MemoryDatabase

from memory_nlp import analyze
from semantic_memory import MemoryEntry, SemanticMemory


class MemoryEngine:
    def __init__(self) -> None:
        """Initialize the engine with a fresh, empty SemanticMemory."""
        self._memory = SemanticMemory()
        self._database = MemoryDatabase()

    @property
    def semantic_memory(self) -> SemanticMemory:
        """Expose the underlying semantic memory (read-only)."""
        return self._memory    

    def remember(self, text: str) -> MemoryEntry:
        """Analyze text and store it as a new memory.

        Args:
            text: The raw text to remember.

        Returns:
            The MemoryEntry that was created and stored.
        """
        nlp_result = analyze(text)

        entry = self._memory.store(text, nlp_result)

        self._database.save_memory(entry)

        return entry

    

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