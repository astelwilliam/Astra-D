from astra_d.memory.models import MemoryCandidate


class FactExtractor:
    def extract(self, message: str) -> list[MemoryCandidate]:
        message = message.strip()

        if not message:
            return []

        return [
            MemoryCandidate(
                content=message,
                source="conversation",
            )
        ]