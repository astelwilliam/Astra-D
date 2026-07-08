"""Memory ranking utilities for Astra-D."""

from astra_d.memory.semantic import MemoryEntry


def score_memory(memory: MemoryEntry, query: str) -> int:
    """Return a simple relevance score based on keyword matches."""

    query_words = query.lower().split()

    score = 0

    for keyword in memory.keywords:
        if keyword.lower() in query_words:
            score += 1

    return score


def rank_memories(
    memories: list[MemoryEntry],
    query: str,
) -> list[MemoryEntry]:
    """Return memories sorted by relevance."""

    return sorted(
        memories,
        key=lambda memory: score_memory(memory, query),
        reverse=True,
    )