"""In-memory semantic memory storage layer for Astra-D.

This module is a pure storage layer, not an AI model. It holds
MemoryEntry records built from NLPResult objects produced by
memory_nlp.analyze(). Everything lives in RAM; persistence is a
future concern and is intentionally not implemented here.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MemoryEntry:
    """A single stored memory derived from analyzed text.

    Attributes:
        id: Unique identifier for this memory (UUID4 string).
        text: The original text that was analyzed.
        entities: Named entities extracted from the text, each a dict
            like {"text": ..., "label": ...}.
        noun_chunks: Noun chunks extracted from the text.
        keywords: Lemmatized, deduplicated keywords extracted from the text.
        timestamp: When this memory was created.
        importance: A relevance/priority score for this memory, defaulting
            to 0.5. Higher values may later be used to weight retrieval or
            control forgetting.
    """

    id: str
    text: str
    entities: list[dict]
    noun_chunks: list[str]
    keywords: list[str]
    timestamp: datetime
    importance: float = 0.5


class SemanticMemory:
    """In-RAM store of MemoryEntry records.

    No data is written to disk. Persistence will be added in a later
    milestone once this storage layer's shape has stabilized.
    """

    def __init__(self) -> None:
        """Initialize an empty in-memory store."""
        self._memories: list[MemoryEntry] = []

    def store(self, text: str, nlp_result: Any) -> MemoryEntry:
        """Create and store a MemoryEntry from an NLPResult.

        Args:
            text: The original text being remembered.
            nlp_result: An NLPResult (or any object exposing .entities,
                .noun_chunks, and .keywords attributes) as returned by
                memory_nlp.analyze().

        Returns:
            The newly created MemoryEntry, already appended to the store.
        """
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            text=text,
            entities=list(nlp_result.entities),
            noun_chunks=list(nlp_result.noun_chunks),
            keywords=list(nlp_result.keywords),
            timestamp=datetime.now(),
            importance=0.5,
        )
        self._memories.append(entry)
        return entry

    def get_all(self) -> list[MemoryEntry]:
        """Return all stored memories, in insertion order.

        Returns:
            A list of all MemoryEntry records currently stored.
        """
        return list(self._memories)

    def get(self, memory_id: str) -> MemoryEntry | None:
        """Return a single memory by its id.

        Args:
            memory_id: The id of the memory to retrieve.

        Returns:
            The matching MemoryEntry, or None if no memory has that id.
        """
        for memory in self._memories:
            if memory.id == memory_id:
                return memory
        return None

    def delete(self, memory_id: str) -> bool:
        """Delete a memory by its id.

        Args:
            memory_id: The id of the memory to delete.

        Returns:
            True if a memory was found and deleted, False otherwise.
        """
        for index, memory in enumerate(self._memories):
            if memory.id == memory_id:
                del self._memories[index]
                return True
        return False

    def count(self) -> int:
        """Return the number of stored memories.

        Returns:
            The count of MemoryEntry records currently in the store.
        """
        return len(self._memories)

    def clear(self) -> None:
        """Remove all stored memories."""
        self._memories.clear()