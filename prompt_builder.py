"""Prompt builder for Astra-D."""

from __future__ import annotations

from astra_d.retrieval.engine import RetrievalEngine


class PromptBuilder:
    """Build prompts enriched with relevant memories."""

    def __init__(self, retrieval_engine: RetrievalEngine) -> None:
        self._retrieval = retrieval_engine

    def build(self, user_message: str) -> str:
        """Create a prompt using relevant memories."""

        memories = self._retrieval.retrieve(user_message, top_k=5)

        if not memories:
            return user_message

        memory_section = "\n".join(
            f"- {memory.text}" for memory in memories
        )

        return (
            "Relevant memories:\n"
            f"{memory_section}\n\n"
            f"Current user message:\n{user_message}"
        )