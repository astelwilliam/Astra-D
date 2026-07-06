"""Memory engine for Astra-D.

Thin orchestration layer that connects NLP preprocessing (memory_nlp)
to semantic memory and SQLite persistence.
"""

from __future__ import annotations

from memory_database import MemoryDatabase
from memory_nlp import analyze
from semantic_memory import MemoryEntry, SemanticMemory


class MemoryEngine:
    """Coordinates text analysis, in-memory storage, and persistence."""

    def __init__(
        self,
        db_path: str = "astra_memory.db",
        load_existing: bool = True,
    ) -> None:
         """Initialize the engine."""

         self._memory = SemanticMemory()
         self._database = MemoryDatabase(db_path)

         if load_existing:
            for memory in self._database.load_memories():
              self._memory.add(memory)

    @property
    def semantic_memory(self) -> SemanticMemory:
        """Expose the underlying semantic memory."""
        return self._memory

    def remember(self, text: str) -> MemoryEntry:
        """Analyze text, store in RAM, and persist to SQLite."""

        nlp_result = analyze(text)

        memory = self._memory.store(text, nlp_result)

        self._database.save_memory(memory)

        return memory

    def count(self) -> int:
        """Return the total number of stored memories."""
        return self._memory.count()

    def all_memories(self) -> list[MemoryEntry]:
        """Return all stored memories."""
        return self._memory.get_all()

    def close(self) -> None:
        """Close the database connection."""
        self._database.close()