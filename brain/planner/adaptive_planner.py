from typing import List, Dict, Any

from brain.planner.base import Planner
from brain.state import BrainState


class AdaptivePlanner(Planner):
    """
    Planner v2:
    - Builds a multi-step plan.
    - Retries failed steps (up to N).
    - Escalates to tools after repeated failure.
    """

    MAX_RETRIES = 2

    def plan(self, state: BrainState) -> List[Dict[str, Any]]:
        last = state.history[-1] if state.history else None

        # ---------------------------------------------------------
        # 1. If last step failed → decide whether to retry or escalate
        # ---------------------------------------------------------
        if last and last.get("error"):

            # If there's no previous step, we cannot retry → escalate
            if "step" not in last:
                return [{
                    "action": "use_tool",
                    "tool": "search",
                    "args": {"query": state.user_input},
                }]

            retries = last.get("retries", 0)

            # Retry same step if possible
            if retries < self.MAX_RETRIES:
                step = last["step"].copy()
                step["retries"] = retries + 1
                return [step]

            # Too many retries → escalate
            return [{
                "action": "use_tool",
                "tool": "search",
                "args": {"query": state.user_input},
            }]

            # Too many retries → escalate to tool
            return [{
                "action": "use_tool",
                "tool": "search",
                "args": {"query": state.user_input},
            }]

        # ---------------------------------------------------------
        # 2. If user input clearly suggests tool usage → tool-first plan
        # ---------------------------------------------------------
        if "search" in state.user_input.lower():
            return [
                {
                    "action": "use_tool",
                    "tool": "search",
                    "args": {"query": state.user_input},
                },
                {
                    "action": "think",
                },
            ]

        # ---------------------------------------------------------
        # 3. Default: simple two-step plan (think → maybe tool later)
        # ---------------------------------------------------------
        if not state.plan:
            return [
                {"action": "think"},
            ]

        # ---------------------------------------------------------
        # 4. Fallback: keep existing plan if present
        # ---------------------------------------------------------
        return state.plan
