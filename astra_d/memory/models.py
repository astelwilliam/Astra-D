from dataclasses import dataclass
from enum import Enum


class MemoryCategory(str, Enum):
    IGNORE = "ignore"
    TEMPORARY = "temporary"
    KNOWLEDGE = "knowledge"
    PREFERENCE = "preference"
    GOAL = "goal"
    PROJECT = "project"
    RELATIONSHIP = "relationship"
    TIMELINE = "timeline"
    EMOTION = "emotion"


@dataclass(frozen=True, slots=True)
class MemoryCandidate:
    content: str
    source: str


@dataclass(frozen=True, slots=True)
class MemoryDecision:
    should_store: bool
    category: MemoryCategory
    confidence: float
    reason: str

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )

        if not self.reason.strip():
            raise ValueError("Reason must not be empty")

        if self.should_store and self.category is MemoryCategory.IGNORE:
            raise ValueError(
                "IGNORE category cannot be stored."
            )

        if not self.should_store and self.category is not MemoryCategory.IGNORE:
            raise ValueError(
                "Category must be IGNORE when should_store is False."
            )

    @classmethod
    def ignore(cls, reason: str) -> "MemoryDecision":
        return cls(
            should_store=False,
            category=MemoryCategory.IGNORE,
            confidence=1.0,
            reason=reason,
        )