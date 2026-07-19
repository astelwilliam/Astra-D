from enum import Enum

from astra_d.memory.models import (
    MemoryCandidate,
    MemoryCategory,
)


class ResolutionAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    IGNORE = "ignore"


class UpdateResolver:
    def resolve(
        self,
        candidate: MemoryCandidate,
        category: MemoryCategory,
        existing_memories: list[str],
    ) -> ResolutionAction:

        content = candidate.content.strip().lower()

        for memory in existing_memories:
            if memory.strip().lower() == content:
                return ResolutionAction.IGNORE

        if existing_memories:
            return ResolutionAction.UPDATE

        return ResolutionAction.CREATE