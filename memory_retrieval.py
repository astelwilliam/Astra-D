"""Memory retrieval for Astra-D."""

from semantic_memory import MemoryEntry, SemanticMemory
from ranking import rank_memories


def retrieve_memories(
    memory: SemanticMemory,
    query: str,
    top_k: int = 5,
) -> list[MemoryEntry]:
    """Return the most relevant memories for a query."""

    memories = memory.get_all()

    if not memories:
        return []

    ranked = rank_memories(memories, query)

    return ranked[:top_k]