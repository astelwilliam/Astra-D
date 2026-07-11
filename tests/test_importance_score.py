import dataclasses

import pytest

from astra_d.memory.models import ImportanceScore


def test_valid_importance_score():
    score = ImportanceScore(
        score=0.7,
        reason="Long-term goal",
    )

    assert score.score == 0.7
    assert score.reason == "Long-term goal"


def test_score_accepts_lower_boundary():
    score = ImportanceScore(
        score=0.0,
        reason="Minimum",
    )

    assert score.score == 0.0


def test_score_accepts_upper_boundary():
    score = ImportanceScore(
        score=1.0,
        reason="Maximum",
    )

    assert score.score == 1.0


def test_score_rejects_below_zero():
    with pytest.raises(ValueError, match="Score must be between"):
        ImportanceScore(
            score=-0.1,
            reason="Invalid",
        )


def test_score_rejects_above_one():
    with pytest.raises(ValueError, match="Score must be between"):
        ImportanceScore(
            score=1.1,
            reason="Invalid",
        )


def test_reason_rejects_empty():
    with pytest.raises(ValueError, match="Reason must not be empty"):
        ImportanceScore(
            score=0.5,
            reason="",
        )


def test_reason_rejects_whitespace():
    with pytest.raises(ValueError, match="Reason must not be empty"):
        ImportanceScore(
            score=0.5,
            reason="   ",
        )


def test_importance_score_is_immutable():
    score = ImportanceScore(
        score=0.5,
        reason="Immutable",
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        score.score = 0.9


def test_importance_score_has_slots():
    score = ImportanceScore(
        score=0.5,
        reason="Slots",
    )

    assert not hasattr(score, "__dict__")


def test_importance_score_equality():
    a = ImportanceScore(
        score=0.5,
        reason="Same",
    )

    b = ImportanceScore(
        score=0.5,
        reason="Same",
    )

    c = ImportanceScore(
        score=0.7,
        reason="Different",
    )

    assert a == b
    assert a != c