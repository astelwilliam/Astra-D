from astra_d.context.models import Context
from astra_d.routing.types import Intent


class ContextBuilder:

    def build(
        self,
        *,
        intent: Intent,
        message: str,
    ) -> Context:

        context = Context()

        if intent is Intent.MEMORY:
            context.use_memory = True

        elif intent is Intent.DOCUMENT:
            context.use_documents = True

        elif intent is Intent.NOTE:
            context.use_notes = True

        elif intent is Intent.TASK:
            context.use_tasks = True

        return context