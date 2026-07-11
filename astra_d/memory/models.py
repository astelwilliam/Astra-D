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