from astra_d.memory.models import (
    ImportanceScore,
    MemoryCandidate,
    MemoryCategory,
    MemoryDecision,
)
from astra_d.memory.rule_based_scorer import RuleBasedImportanceScorer


def make_candidate() -> MemoryCandidate:
    return MemoryCandidate(
        content="User likes Python.",
        source="conversation",
    )


def make_decision(category: MemoryCategory) -> MemoryDecision:
    return MemoryDecision(
        should_store=category != MemoryCategory.IGNORE,
        category=category,
        confidence=1.0,
        reason="test",
    )


def test_returns_importance_score():
    scorer = RuleBasedImportanceScorer()

    result = scorer.score(
        make_candidate(),
        make_decision(MemoryCategory.GOAL),
    )

    assert isinstance(result, ImportanceScore)


def test_identity_scores_higher_than_fact():
    scorer = RuleBasedImportanceScorer()

    identity = scorer.score(
        make_candidate(),
        make_decision(MemoryCategory.IDENTITY),
    )

    fact = scorer.score(
        make_candidate(),
        make_decision(MemoryCategory.FACT),
    )

    assert identity.score > fact.score


def test_ignore_scores_zero():
    scorer = RuleBasedImportanceScorer()

    result = scorer.score(
        make_candidate(),
        make_decision(MemoryCategory.IGNORE),
    )

    assert result.score == 0.0


def test_reason_is_not_empty():
    scorer = RuleBasedImportanceScorer()

    result = scorer.score(
        make_candidate(),
        make_decision(MemoryCategory.PROJECT),
    )

    assert result.reason