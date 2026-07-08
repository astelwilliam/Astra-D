"""Tests for memory ranking."""

from datetime import datetime

from astra_d.retrieval.ranking import score_memory, rank_memories
from astra_d.memory.semantic import MemoryEntry


def make_memory(text: str, keywords: list[str]) -> MemoryEntry:
    """Create a MemoryEntry for testing."""

    return MemoryEntry(
        id="1",
        text=text,
        entities=[],
        noun_chunks=[],
        keywords=keywords,
        timestamp=datetime.now(),
        importance=0.5,
    )


def test_exact_keyword_match_scores_higher():
    """Matching keywords should produce a higher score."""

    memory = make_memory(
        "RTX 2050 has 4GB VRAM",
        ["rtx", "2050", "vram"],
    )

    score = score_memory(memory, "Tell me about my RTX")

    assert score > 0


def test_no_match_scores_zero():
    """Unrelated memories should score zero."""

    memory = make_memory(
        "Python programming",
        ["python", "programming"],
    )

    score = score_memory(memory, "Tell me about my GPU")

    assert score == 0


def test_rank_returns_sorted_memories():
    """Best matching memories should appear first."""

    gpu = make_memory(
        "RTX 2050",
        ["rtx", "2050"],
    )

    python = make_memory(
        "Python",
        ["python"],
    )

    ranked = rank_memories(
        [python, gpu],
        "RTX",
    )

    assert ranked[0] == gpu


def test_rank_returns_all_memories():
    """Ranking should not discard memories."""

    gpu = make_memory(
        "RTX",
        ["rtx"],
    )

    python = make_memory(
        "Python",
        ["python"],
    )

    ranked = rank_memories(
        [gpu, python],
        "RTX",
    )

    assert len(ranked) == 2