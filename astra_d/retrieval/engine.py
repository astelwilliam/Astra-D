"""Retrieval engine for Astra-D."""

from __future__ import annotations

from astra_d.memory.semantic import MemoryEntry, SemanticMemory
from astra_d.memory.retrieval import retrieve_memories


class RetrievalEngine:
    """High-level interface for retrieving relevant memories."""

    def __init__(self, semantic_memory: SemanticMemory) -> None:
        self._semantic_memory = semantic_memory

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[MemoryEntry]:
        """Return the most relevant memories."""

        return retrieve_memories(
            self._semantic_memory,
            query,
            top_k,
        )