"""Keyword-overlap retrieval over SemanticMemory.

This is a deliberately simple, deterministic retrieval strategy based on
keyword overlap. It has no databases, no embeddings, and no machine
learning. The public interface (retrieve()) is kept stable so it can be
swapped for embedding-based search later without changing callers.
"""

from __future__ import annotations

from memory_nlp import analyze
from semantic_memory import MemoryEntry, SemanticMemory


class RetrievalEngine:
    """Retrieves stored memories by keyword overlap with a query.

    Wraps a SemanticMemory instance without modifying it. Scoring is a
    plain integer count of shared keywords between the query and each
    stored memory, so results are fully deterministic and reproducible.
    """

    def __init__(self, semantic_memory: SemanticMemory) -> None:
        """Store a reference to an existing SemanticMemory instance.

        Args:
            semantic_memory: The SemanticMemory to retrieve from. This
                engine only reads from it and never modifies it.
        """
        self._semantic_memory = semantic_memory

    def retrieve(self, query: str, top_k: int = 5) -> list[MemoryEntry]:
        """Return stored memories ranked by keyword overlap with query.

        Args:
            query: The natural-language query to search for.
            top_k: Maximum number of memories to return.

        Returns:
            A list of MemoryEntry objects with score > 0, sorted from
            highest overlap score to lowest. Ties preserve the original
            storage order (stable sort). Empty list if nothing matches
            or the query has no usable keywords.
        """
        if top_k <= 0:
            return []

        query_result = analyze(query)
        query_keywords = set(query_result.keywords)
        if not query_keywords:
            return []

        scored: list[tuple[int, MemoryEntry]] = []
        for entry in self._semantic_memory.get_all():
            score = self._score(query_keywords, entry.keywords)
            if score > 0:
                scored.append((score, entry))

        # Stable sort: ties keep original (insertion) order since Python's
        # sort is stable and we only sort by score, descending.
        scored.sort(key=lambda pair: pair[0], reverse=True)

        return [entry for _score, entry in scored[:top_k]]

    @staticmethod
    def _score(query_keywords: set[str], memory_keywords: list[str]) -> int:
        """Return the count of keywords shared between query and memory.

        Args:
            query_keywords: Set of keywords extracted from the query.
            memory_keywords: List of keywords stored on a MemoryEntry.

        Returns:
            The number of distinct keywords present in both.
        """
        return len(query_keywords.intersection(memory_keywords))