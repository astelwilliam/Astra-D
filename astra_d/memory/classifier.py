from astra_d.memory.models import (
    MemoryCandidate,
    MemoryCategory,
    MemoryDecision,
)


class MemoryClassifier:
    def classify(self, candidate: MemoryCandidate) -> MemoryDecision:
        text = candidate.content.lower()

        print(f"TEXT: {text!r}")

        if "i want to" in text:
            print("GOAL DETECTED")
            return MemoryDecision(
                should_store=True,
                category=MemoryCategory.GOAL,
                confidence=0.95,
                reason="Detected goal",
            )

        print("DEFAULT")
        return MemoryDecision.ignore(
            reason="Default classifier behavior"
        )