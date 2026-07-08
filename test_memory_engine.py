"""Tests for memory_engine.py."""

from __future__ import annotations

from astra_d.memory.engine import MemoryEngine
from astra_d.memory.semantic import MemoryEntry


def test_remember_stores_one_memory():
    engine = MemoryEngine(db_path=":memory:")
    assert engine.count() == 0
    engine.remember("Barack Obama was born in Hawaii.")
    assert engine.count() == 1


def test_count_increases_correctly():
    engine = MemoryEngine(db_path=":memory:")
    assert engine.count() == 0
    engine.remember("First memory.")
    assert engine.count() == 1
    engine.remember("Second memory.")
    assert engine.count() == 2
    engine.remember("Third memory.")
    assert engine.count() == 3


def test_all_memories_returns_memory_entry_objects():
    engine = MemoryEngine(db_path=":memory:")
    engine.remember("The cat sat on the mat.")
    memories = engine.all_memories()
    assert len(memories) == 1
    assert all(isinstance(m, MemoryEntry) for m in memories)


def test_stored_entities_are_preserved():
    engine = MemoryEngine(db_path=":memory:")
    entry = engine.remember("Barack Obama was born in Hawaii.")
    stored = engine.all_memories()[0]
    assert stored.entities == entry.entities
    entity_texts = {e["text"] for e in stored.entities}
    assert "Barack Obama" in entity_texts


def test_stored_keywords_are_preserved():
    engine = MemoryEngine(db_path=":memory:")
    entry = engine.remember("The cat is sitting on the mat, quietly.")
    stored = engine.all_memories()[0]
    assert stored.keywords == entry.keywords
    assert "cat" in stored.keywords
    assert "mat" in stored.keywords


def test_multiple_memories_can_be_stored():
    engine = MemoryEngine(db_path=":memory:")
    first = engine.remember("Astra-D runs locally on Ollama.")
    second = engine.remember("The RTX 2050 has limited VRAM.")

    memories = engine.all_memories()
    assert len(memories) == 2
    ids = {m.id for m in memories}
    assert first.id in ids
    assert second.id in ids
    # Each memory keeps its own text, not overwritten by the other.
    texts = {m.text for m in memories}
    assert "Astra-D runs locally on Ollama." in texts
    assert "The RTX 2050 has limited VRAM." in texts


def test_empty_text_is_handled_safely():
    engine = MemoryEngine(db_path=":memory:")
    entry = engine.remember("")
    assert engine.count() == 1
    assert entry.entities == []
    assert entry.noun_chunks == []
    assert entry.keywords == []


def test_whitespace_only_text_is_handled_safely():
    engine = MemoryEngine(db_path=":memory:")
    entry = engine.remember("   \n\t  ")
    assert engine.count() == 1
    assert entry.entities == []
    assert entry.noun_chunks == []
    assert entry.keywords == []