from astra_d.memory.models import MemoryCandidate, MemoryCategory
from astra_d.memory.resolver import (
    UpdateResolver,
    ResolutionAction,
)


def test_new_memory_creates():
    resolver = UpdateResolver()

    result = resolver.resolve(
        MemoryCandidate(
            content="I want to build Astra-D",
            source="conversation",
        ),
        MemoryCategory.PROJECT,
        [],
    )

    assert result is ResolutionAction.CREATE


def test_duplicate_memory_is_ignored():
    resolver = UpdateResolver()

    result = resolver.resolve(
        MemoryCandidate(
            content="I like Python",
            source="conversation",
        ),
        MemoryCategory.FACT,
        [
            "I like Python"
        ],
    )

    assert result is ResolutionAction.IGNORE


def test_existing_different_memory_updates():
    resolver = UpdateResolver()

    result = resolver.resolve(
        MemoryCandidate(
            content="Astra-D version 0.10",
            source="conversation",
        ),
        MemoryCategory.PROJECT,
        [
            "Astra-D version 0.9"
        ],
    )

    assert result is ResolutionAction.UPDATE