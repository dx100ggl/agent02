# brain/c2/planner/adaptive_planner.py

from __future__ import annotations
from typing import Any, Dict, List

from brain.c2.planner.base import Planner
from brain.c1.state import BrainState
from brain.c2.planner.intent_classifier import IntentClassifier


class AdaptivePlanner(Planner):
    """
    AdaptivePlanner with Option B memory → LLM reasoning.

    - llm_callable is optional (tests expect AdaptivePlanner() to work)
    - If llm_callable is None, initial step is THINK (test compatibility)
    - After memory search, planner schedules an LLM step
    """

    MAX_RETRIES = 2

    def __init__(self, llm_callable=None):
        self.llm = llm_callable
        self.intent_classifier = IntentClassifier() if llm_callable else None

    # ---------------------------------------------------------
    # Main planning entry point
    # ---------------------------------------------------------
    def plan(self, state: BrainState) -> List[Dict[str, Any]]:
        text = (state.user_input or "").lower()
        last = state.history[-1] if state.history else None

        # ---------------------------------------------------------
        # 0. Intent classification (only if llm_callable provided)
        # ---------------------------------------------------------
        if self.llm and self.intent_classifier:
            intent = self.intent_classifier.classify(self.llm, state.user_input)

            if intent == "write_memory":
                return [{
                    "action": "use_tool",
                    "tool": "write_memory",
                    "args": {"fact": state.user_input},
                }]

            if intent == "retrieve_memory":
                return [{
                    "action": "use_tool",
                    "tool": "search_memory",
                    "args": {"query": state.user_input},
                }]

        # ---------------------------------------------------------
        # 1. Error handling (v3 semantics)
        # ---------------------------------------------------------
        if last and last.get("error"):

            # No step recorded → escalate immediately
            if "step" not in last:
                return [{
                    "action": "use_tool",
                    "tool": "search",
                    "args": {"query": state.user_input},
                }]

            # Retry if step exists
            retries = last.get("retries", 0)
            if retries < self.MAX_RETRIES:
                step = last["step"].copy()
                step["retries"] = retries + 1
                return [step]

            # Max retries exceeded → escalate
            return [{
                "action": "use_tool",
                "tool": "search",
                "args": {"query": state.user_input},
            }]

        # ---------------------------------------------------------
        # 2. Analyze-after-tool (unchanged)
        # ---------------------------------------------------------
        if last and not last.get("error") and "step" in last:
            step = last["step"]
            if step.get("action") == "use_tool" and step.get("tool") != "search_memory":
                return [{"action": "think"}]

        # ---------------------------------------------------------
        # 2.5 Option B: After memory search → follow up with LLM
        # ---------------------------------------------------------
        if last and last.get("step", {}).get("tool") == "search_memory" and not last.get("error"):
            # Optionally, you could also check that there *are* results:
            # result = last.get("result", {})
            # if result.get("results"):
            #     ...
            return [{
                "action": "llm",
                "prompt": state.user_input,
            }]

        # ---------------------------------------------------------
        # 3. Memory-aware planning (unchanged)
        # ---------------------------------------------------------
        if getattr(state, "memory_results", None):
            top = state.memory_results[0]
            if top.get("score", 0.0) >= 0.75:
                return [{"action": "think", "use_memory": True}]

        # ---------------------------------------------------------
        # 4. Tool-first intent (unchanged)
        # ---------------------------------------------------------
        if "search" in text:
            return [{
                "action": "use_tool",
                "tool": "search",
                "args": {"query": state.user_input},
            }]

        # ---------------------------------------------------------
        # 5. Default step (THINK if no LLM, LLM otherwise)
        # ---------------------------------------------------------
        if self.llm is None:
            return [{"action": "think"}]

        return [{
            "action": "llm",
            "prompt": state.user_input,
        }]
