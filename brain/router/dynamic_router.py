from brain.router.base import Router
from brain.state import BrainState

class DynamicRouter(Router):
    def route(self, state: BrainState) -> str:
        if "search" in state.user_input.lower():
            return "tool_mode"

        if state.history and state.history[-1].get("error"):
            return "escalate"

        return "llm_mode"
