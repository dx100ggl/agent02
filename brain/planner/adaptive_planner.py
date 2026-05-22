from typing import List, Dict, Any

from brain.planner.base import Planner
from brain.state import BrainState


class AdaptivePlanner(Planner):
    """
    AdaptivePlanner v3 (corrected)

    - Keeps v2 behavior (retries + escalation).
    - Adds analyze-after-tool behavior.
    - Ensures successful tool follow-up overrides keyword intent.
    """

    MAX_RETRIES = 2

    def plan(self, state: BrainState) -> List[Dict[str, Any]]:
        last = state.history[-1] if state.history else None
        text = (state.user_input or "").lower()

        # ---------------------------------------------------------
        # 1. Error handling: retry or escalate
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

        # ---------------------------------------------------------
        # 2. Analyze-after-tool (MUST override keyword intent)
        # ---------------------------------------------------------
        if last and not last.get("error") and "step" in last:
            step = last["step"]
            if step.get("action") == "use_tool":
                # We just used a tool successfully → now think about it.
                return [{"action": "think"}]

        # ---------------------------------------------------------
        # 3. Tool-first intent (only if no tool was just used)
        # ---------------------------------------------------------
        if "search" in text:
            return [{
                "action": "use_tool",
                "tool": "search",
                "args": {"query": state.user_input},
            }]

        # ---------------------------------------------------------
        # 4. Default: LLM-only think step
        # ---------------------------------------------------------
        if not state.plan:
            return [{"action": "think"}]

        # ---------------------------------------------------------
        # 5. Fallback: reuse existing plan
        # ---------------------------------------------------------
        return state.plan
