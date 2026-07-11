"""Integration tests for the Astra-D memory pipeline.

Pipeline under test:
    User Message -> FactExtractor -> MemoryCandidate
                  -> MemoryClassifier -> MemoryDecision

These are integration tests only: no mocks, real components used
end-to-end as they will run in production.
"""

from astra_d.memory.extractor import FactExtractor
from astra_d.memory.classifier import MemoryClassifier
from astra_d.memory.models import (
    MemoryCategory,
    MemoryDecision,
)


def test_goal_statement_is_extracted_and_classified_as_goal():
    extractor = FactExtractor()
    classifier = MemoryClassifier()

    candidates = extractor.extract("I want to become a software engineer.")

    assert len(candidates) == 1
    assert candidates[0].content == "I want to become a software engineer."

    decision = classifier.classify(candidates[0])

    assert isinstance(decision, MemoryDecision)
    assert decision.should_store is True
    assert decision.category is MemoryCategory.GOAL
    assert 0.0 <= decision.confidence <= 1.0


def test_greeting_is_extracted_but_ignored():
    extractor = FactExtractor()
    classifier = MemoryClassifier()

    candidates = extractor.extract("Hello")

    assert len(candidates) == 1
    assert candidates[0].content == "Hello"

    decision = classifier.classify(candidates[0])

    assert isinstance(decision, MemoryDecision)
    assert decision.should_store is False
    assert decision.category is MemoryCategory.IGNORE
    assert 0.0 <= decision.confidence <= 1.0