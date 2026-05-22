from typing import Literal, Optional

from brain.state import BrainState
from brain.memory.retriever import MemoryRetriever
from brain.memory.store import MemoryStore

LegacyRouteMode = Literal["llm_mode", "tool_mode"]
RawRouteMode = Literal["llm", "tool", "memory"]


class DynamicRouter:
    """
    DynamicRouter v2.5 — memory-aware routing.

    - route()      → legacy API ("llm_mode" / "tool_mode")
    - route_raw()  → new API ("llm" / "tool" / "memory")

    New behavior:
        * If memory has a strong match → "memory"
        * Else if intent == search → "tool"
        * Else → "llm"
    """

    def __init__(self, memory: Optional[MemoryStore] = None):
        self.memory = memory or MemoryStore()
        self.retriever = MemoryRetriever(store=self.memory)

    # --------------------------------------------------------------
    # Legacy API (used by orchestrator + old tests)
    # --------------------------------------------------------------
    def route(self, state: BrainState) -> LegacyRouteMode:
        raw = self.route_raw(state)
        if raw == "tool":
            return "tool_mode"
        # "memory" and "llm" both map to llm_mode for legacy compatibility
        return "llm_mode"

    # --------------------------------------------------------------
    # New API (v2.5)
    # --------------------------------------------------------------
    def route_raw(self, state: BrainState) -> RawRouteMode:
        # BrainState stores user text in state.user_input
        text = (state.user_input or "").lower()

        # 1. Memory-first routing
        if self._memory_relevant(state):
            return "memory"

        # 2. Intent classification
        intent = self._classify_intent(text)
        if intent == "search":
            return "tool"

        # 3. Default: LLM
        return "llm"

    # --------------------------------------------------------------
    # Memory relevance check
    # --------------------------------------------------------------
    def _memory_relevant(self, state: BrainState) -> bool:
        """
        Returns True if memory contains a strong match.
        """
        results = self.retriever.retrieve(state, top_k=1)
        if not results:
            return False

        # Strong match threshold
        return results[0]["score"] >= 0.75

    # --------------------------------------------------------------
    # Intent classifier
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
