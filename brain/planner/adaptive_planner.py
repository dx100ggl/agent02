from brain.planner.base import Planner
from brain.state import BrainState


class AdaptivePlanner(Planner):
    def plan(self, state: BrainState):
        last = state.history[-1] if state.history else None

        # ---------------------------------------------------------
        # 1. If last step failed → escalate to tool
        # ---------------------------------------------------------
        if last and last.get("error"):
            return [{"action": "use_tool", "tool": "search"}]

        # ---------------------------------------------------------
        # 2. If router wants tool mode → emit tool step
        # ---------------------------------------------------------
        if "search" in state.user_input.lower():
            return [{"action": "use_tool", "tool": "search", "args": {"query": state.user_input}}]

        # ---------------------------------------------------------
        # 3. Default: think step
        # ---------------------------------------------------------
        return [{"action": "think"}]
