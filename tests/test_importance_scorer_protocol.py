from typing import runtime_checkable

from astra_d.memory.scorer import ImportanceScorer


def test_importance_scorer_is_protocol():
    """ImportanceScorer should be defined as a Protocol."""

    assert hasattr(ImportanceScorer, "__dict__")


def test_importance_scorer_defines_score_method():
    """ImportanceScorer must define a score() method."""

    assert hasattr(ImportanceScorer, "score")