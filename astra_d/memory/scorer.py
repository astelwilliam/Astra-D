from __future__ import annotations

from typing import Protocol

from .models import (
    MemoryCandidate,
    MemoryDecision,
    ImportanceScore,
)


class ImportanceScorer(Protocol):
    """
    Computes an importance score for a memory candidate.
    """

    def score(
        self,
        candidate: MemoryCandidate,
        decision: MemoryDecision,
    ) -> ImportanceScore:
        """
        Return an importance score for the candidate.

        The implementation must be deterministic and stateless.
        """
        ...