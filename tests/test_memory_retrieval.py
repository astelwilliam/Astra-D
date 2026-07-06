from datetime import datetime

from memory_retrieval import retrieve_memories
from semantic_memory import MemoryEntry, SemanticMemory


def make_memory(text, keywords):
    return MemoryEntry(
        id=text,
        text=text,
        entities=[],
        noun_chunks=[],
        keywords=keywords,
        timestamp=datetime.now(),
        importance=0.5,
    )


def test_returns_empty_when_no_memories():
    memory = SemanticMemory()

    result = retrieve_memories(memory, "RTX")

    assert result == []


def test_returns_best_matching_memory():
    memory = SemanticMemory()

    gpu = make_memory("RTX 2050", ["rtx", "2050"])
    python = make_memory("Python", ["python"])

    memory.add(gpu)
    memory.add(python)

    result = retrieve_memories(memory, "RTX")

    assert result[0] == gpu


def test_top_k_limits_results():
    memory = SemanticMemory()

    for i in range(10):
        memory.add(
            make_memory(
                f"Memory {i}",
                [f"memory{i}"],
            )
        )

    result = retrieve_memories(memory, "memory", top_k=3)

    assert len(result) == 3