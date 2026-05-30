# brain/c2/router/dynamic_router.py

class DynamicRouter:
    """
    Brain‑24 / S4 DynamicRouter
    """

    def route(self, state):
        """
        Determine which skill should handle the current state.

        Backward‑compatible:
        - If state has no .meta, or no intent, fall back to "default".
        """

        meta = getattr(state, "meta", None)
        if not isinstance(meta, dict):
            return "default"

        intent = meta.get("intent", "")
        if not isinstance(intent, str):
            return "default"

        intent = intent.lower()

        if intent == "equity_research":
            return "equity_research_skill"

        if intent == "write_memory":
            return "write_memory_skill"

        if intent == "retrieve_memory":
            return "retrieve_memory_skill"

        return "default"
