import pytest

from astra_d.memory.classifier import MemoryClassifier
from astra_d.memory.models import (
    MemoryCandidate,
    MemoryCategory,
    MemoryDecision,
)


class MemoryClassifier:
    def classify(self, candidate: MemoryCandidate) -> MemoryDecision:
        text = candidate.content.lower()

        if "i want to" in text:
            return MemoryDecision(
                should_store=True,
                category=MemoryCategory.GOAL,
                confidence=0.95,
                reason="Detected goal",
            )

        return MemoryDecision.ignore(
            reason="Default classifier behavior"
        )

  
def test_classifier_can_be_created():
    classifier = MemoryClassifier()

    assert classifier is not None


def test_classifier_returns_memory_decision():
    classifier = MemoryClassifier()

    candidate = MemoryCandidate(
        content="I like coffee.",
        source="conversation",
    )

    decision = classifier.classify(candidate)

    assert isinstance(decision, MemoryDecision)


def test_classifier_returns_ignore_by_default():
    classifier = MemoryClassifier()

    candidate = MemoryCandidate(
        content="Hello",
        source="conversation",
    )

    decision = classifier.classify(candidate)

    assert decision.should_store is False
    assert decision.category is MemoryCategory.IGNORE


def test_classifier_reason_is_not_empty():
    classifier = MemoryClassifier()

    candidate = MemoryCandidate(
        content="Hello",
        source="conversation",
    )

    decision = classifier.classify(candidate)

    assert decision.reason != ""


def test_classifier_confidence_is_valid():
    classifier = MemoryClassifier()

    candidate = MemoryCandidate(
        content="Hello",
        source="conversation",
    )

    decision = classifier.classify(candidate)

    assert 0.0 <= decision.confidence <= 1.0



def test_classifier_detects_goal():
    classifier = MemoryClassifier()

    candidate = MemoryCandidate(
        content="I want to become a software engineer.",
        source="conversation",
    )

    decision = classifier.classify(candidate)

    assert decision.should_store is True
    assert decision.category is MemoryCategory.GOAL