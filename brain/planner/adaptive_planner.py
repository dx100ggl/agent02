from typing import List, Dict, Any

from brain.planner.base import Planner
from brain.state import BrainState


class AdaptivePlanner(Planner):
    """
    AdaptivePlanner v3.5

    - v3 behavior:
        * retry on errors
        * escalate after max retries
        * analyze-after-tool (think after successful tool)
        * simple tool intent ("search" → use_tool)

    - v3.5 additions:
        * memory-aware planning:
            - if strong memory hit is present → think with memory
        * fully backward-compatible: if no memory info is present,
          behavior is identical to v3.
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
        # 2. Analyze-after-tool (unchanged v3 behavior)
        # ---------------------------------------------------------
        if last and not last.get("error") and "step" in last:
            step = last["step"]
            if step.get("action") == "use_tool":
                # We just used a tool successfully → now think about it.
                return [{"action": "think"}]

        # ---------------------------------------------------------
        # 3. Memory-aware planning (v3.5)
        # ---------------------------------------------------------
        if self._has_strong_memory(state):
            # We have a strong memory hit → think with memory context.
            # Extra key is additive and won't break existing consumers.
            return [{"action": "think", "use_memory": True}]

        # ---------------------------------------------------------
        # 4. Tool-first intent (only if no tool was just used)
        # ---------------------------------------------------------
        if "search" in text:
            return [{
                "action": "use_tool",
                "tool": "search",
                "args": {"query": state.user_input},
            }]

        # ---------------------------------------------------------
        # 5. Default: LLM-only think step
        # ---------------------------------------------------------
        if not state.plan:
            return [{"action": "think"}]

        # ---------------------------------------------------------
        # 6. Fallback: reuse existing plan
        # ---------------------------------------------------------
        return state.plan

    # -------------------------------------------------------------
    # v3.5 helper: memory relevance
    # -------------------------------------------------------------
    def _has_strong_memory(self, state: BrainState) -> bool:
        """
        Returns True if the state carries strong memory results.

        We assume an optional attribute:
            state.memory_results: List[{"text": ..., "score": float, ...}]

        If it's missing or empty, we treat it as "no memory".
        """
        memory_results = getattr(state, "memory_results", None)
        if not memory_results:
            return False

        top = memory_results[0]
        score = top.get("score", 0.0)
        return score >= 0.75
