from typing import Literal
from brain.state import BrainState

LegacyRouteMode = Literal["llm_mode", "tool_mode"]
RawRouteMode = Literal["llm", "tool"]


class DynamicRouter:
    """
    DynamicRouter v2 (dual-compatible)

    - route()      → legacy API ("llm_mode" / "tool_mode")
    - route_raw()  → v2 API ("llm" / "tool")

    This keeps all old tests green while allowing new v2 tests to use the
    modern interface.
    """

    def __init__(self):
        pass

    # --------------------------------------------------------------
    # Legacy API (used by orchestrator + old tests)
    # --------------------------------------------------------------
    def route(self, state: BrainState) -> LegacyRouteMode:
        raw = self.route_raw(state)
        return "tool_mode" if raw == "tool" else "llm_mode"

    # --------------------------------------------------------------
    # New API (used by router_v2 tests)
    # --------------------------------------------------------------
    def route_raw(self, state: BrainState) -> RawRouteMode:
        text = (state.user_input or "").lower()
        intent = self._classify_intent(text)

        if intent == "search":
            return "tool"
        return "llm"

    # --------------------------------------------------------------
    # Internal helpers
    # --------------------------------------------------------------
    def _classify_intent(self, text: str) -> str:
        if not text:
            return "chat"

        search_keywords = [
            "search",
            "look up",
            "lookup",
            "google",
            "find info",
            "web search",
        ]

        for kw in search_keywords:
            if kw in text:
                return "search"

        return "chat"

    def _score_confidence(self, text: str) -> float:
        if not text:
            return 0.5
        return 0.8
