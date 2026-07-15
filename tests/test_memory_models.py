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
          "identity",
          "preference",
          "goal",
          "project",
          "task",
          "fact",
          "event",
          "relationship",
          "emotion",
}

    actual = {category.value for category in MemoryCategory}

    assert actual == expected


def test_memory_category_values_are_unique():
    values = [category.value for category in MemoryCategory]

    assert len(values) == len(set(values))



def test_memory_decision_rejects_confidence_below_zero():
    with pytest.raises(ValueError, match="Confidence must be between"):
        MemoryDecision(True, MemoryCategory.GOAL, -0.1, "Bad confidence")


def test_memory_decision_rejects_confidence_above_one():
    with pytest.raises(ValueError, match="Confidence must be between"):
        MemoryDecision(True, MemoryCategory.GOAL, 1.5, "Bad confidence")


def test_memory_decision_accepts_boundary_confidence():
    d0 = MemoryDecision(True, MemoryCategory.FACT, 0.0, "Minimum")
    d1 = MemoryDecision(True, MemoryCategory.FACT, 1.0, "Maximum")

    assert d0.confidence == 0.0
    assert d1.confidence == 1.0


def test_memory_decision_rejects_empty_reason():
    with pytest.raises(ValueError, match="Reason must not be empty"):
        MemoryDecision(True, MemoryCategory.GOAL, 0.9, "")


def test_memory_decision_rejects_whitespace_only_reason():
    with pytest.raises(ValueError, match="Reason must not be empty"):
        MemoryDecision(True, MemoryCategory.GOAL, 0.9, "   ")


def test_memory_decision_rejects_non_ignore_when_not_storing():
    with pytest.raises(ValueError, match="Category must be IGNORE"):
        MemoryDecision(False, MemoryCategory.GOAL, 0.8, "Should not happen")


def test_memory_decision_allows_ignore_when_not_storing():
    decision = MemoryDecision(False, MemoryCategory.IGNORE, 0.9, "Not relevant")

    assert decision.should_store is False
    assert decision.category is MemoryCategory.IGNORE


def test_memory_decision_ignore_factory():
    decision = MemoryDecision.ignore("Greeting, no useful info")

    assert decision.should_store is False
    assert decision.category is MemoryCategory.IGNORE
    assert decision.confidence == 1.0
    assert decision.reason == "Greeting, no useful info"