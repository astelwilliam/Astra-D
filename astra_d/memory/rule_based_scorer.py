from __future__ import annotations

from .models import (
    ImportanceScore,
    MemoryCandidate,
    MemoryCategory,
    MemoryDecision,
)
from .scorer import ImportanceScorer


class RuleBasedImportanceScorer(ImportanceScorer):
    """
    Deterministic importance scorer.

    v0.10.0 intentionally keeps the scoring rules simple.
    Future versions may replace this implementation without
    changing the pipeline.
    """

    CATEGORY_SCORES = {
        MemoryCategory.IDENTITY: 0.95,
        MemoryCategory.GOAL: 0.90,
        MemoryCategory.PROJECT: 0.85,
        MemoryCategory.PREFERENCE: 0.75,
        MemoryCategory.RELATIONSHIP: 0.70,
        MemoryCategory.FACT: 0.60,
        MemoryCategory.EVENT: 0.55,
        MemoryCategory.TASK: 0.50,
        MemoryCategory.EMOTION: 0.40,
        MemoryCategory.IGNORE: 0.00,
    }

    def score(
        self,
        candidate: MemoryCandidate,
        decision: MemoryDecision,
    ) -> ImportanceScore:

        score = self.CATEGORY_SCORES.get(decision.category, 0.50)

        return ImportanceScore(
            score=score,
            reason=f"Rule-based score for {decision.category.value}",
        )