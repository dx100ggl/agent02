from brain.planner.base import Planner
from brain.state import BrainState

class AdaptivePlanner(Planner):
    def plan(self, state: BrainState):
        if not state.plan:
            return [{"action": "think"}]

        last = state.history[-1] if state.history else None

        if last and last.get("error"):
            return [{"action": "use_tool", "tool": "search"}]

        return state.plan
