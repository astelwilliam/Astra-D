"""Router for Astra-D."""

from astra_d.routing.intent import detect_intent
from astra_d.routing.types import Intent


class Router:

    def route(self, text: str) -> Intent:
        return detect_intent(text)