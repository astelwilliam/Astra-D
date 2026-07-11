import pytest

from astra_d.memory.models import MemoryCategory

from dataclasses import FrozenInstanceError

from astra_d.memory.models import MemoryCandidate

from astra_d.memory.models import MemoryDecision


def test_memory_decision_creation():
    decision = MemoryDecision(
        should_store=True,
        category=MemoryCategory.GOAL,
        confidence=0.95,
        reason="Detected long-term goal",
    )

    assert decision.should_store is True
    assert decision.category is MemoryCategory.GOAL
    assert decision.confidence == 0.95
    assert decision.reason == "Detected long-term goal"


def test_memory_decision_equality():
    d1 = MemoryDecision(
        True,
        MemoryCategory.GOAL,
        0.95,
        "Detected long-term goal",
    )

    d2 = MemoryDecision(
        True,
        MemoryCategory.GOAL,
        0.95,
        "Detected long-term goal",
    )

    assert d1 == d2


def test_memory_decision_is_immutable():
    decision = MemoryDecision(
        True,
        MemoryCategory.GOAL,
        0.95,
        "Detected long-term goal",
    )

    with pytest.raises(FrozenInstanceError):
        decision.confidence = 0.50


def test_memory_decision_repr_contains_class_name():
    decision = MemoryDecision(
        True,
        MemoryCategory.GOAL,
        0.95,
        "Detected long-term goal",
    )

    assert "MemoryDecision" in repr(decision)
    


def test_memory_candidate_creation():
    candidate = MemoryCandidate(
        content="User likes coffee",
        source="conversation",
    )

    assert candidate.content == "User likes coffee"
    assert candidate.source == "conversation"


def test_memory_candidate_equality():
    candidate1 = MemoryCandidate(
        content="User likes coffee",
        source="conversation",
    )

    candidate2 = MemoryCandidate(
        content="User likes coffee",
        source="conversation",
    )

    assert candidate1 == candidate2


def test_memory_candidate_is_immutable():
    candidate = MemoryCandidate(
        content="User likes coffee",
        source="conversation",
    )

    with pytest.raises(FrozenInstanceError):
        candidate.content = "New content"


def test_memory_candidate_repr_contains_class_name():
    candidate = MemoryCandidate(
        content="User likes coffee",
        source="conversation",
    )

    assert "MemoryCandidate" in repr(candidate)


def test_memory_category_contains_expected_values():
    expected = {
        "ignore",
        "temporary",
        "knowledge",
        "preference",
        "goal",
        "project",
        "relationship",
        "timeline",
        "emotion",
    }

    actual = {category.value for category in MemoryCategory}

    assert actual == expected


def test_memory_category_values_are_unique():
    values = [category.value for category in MemoryCategory]

    assert len(values) == len(set(values))