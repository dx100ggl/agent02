# brain/c2/router/dynamic_router.py

from __future__ import annotations
from typing import Any, Dict, Optional

from brain.c1.planner.plan import ResearchPlan, build_fundamentals_plan, build_full_research_plan
from brain.c3.memory.memory_service import MemoryService
from brain.llm.lmstudio_llm import LMStudioLLM
from brain.c2.executor.executor import Executor


class DynamicRouter:
    """
    C2 router with C3 + C5 integration.
    Belief‑aware routing without breaking existing behavior.
    """

    def __init__(self, executor: Executor, llm: LMStudioLLM, memory: MemoryService):
        self._executor = executor
        self._llm = llm
        self._memory = memory

    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------
    def route(self, user_input: str, ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ctx = ctx or {}

        # ---------------------------------------------------------
        # C3: retrieve memory
        # ---------------------------------------------------------
        memory_hits = self._memory.retrieve(user_input)
        ctx["memory"] = memory_hits

        # ---------------------------------------------------------
        # C5: pull beliefs if available
        # ---------------------------------------------------------
        beliefs = []
        if hasattr(self._memory, "get_beliefs"):
            try:
                beliefs = self._memory.get_beliefs()
            except Exception:
                beliefs = []
        ctx["beliefs"] = beliefs

        # ---------------------------------------------------------
        # Belief‑aware routing heuristics (C5 → C2)
        # ---------------------------------------------------------
        restricted = []
        for b in beliefs:
            if getattr(b, "kind", None) == "constraint":
                restricted.extend(b.metadata.get("tags", []))

        def belief_score(tool_name: str) -> float:
            score = 0.0

            # Preferences boost matching tools
            for b in beliefs:
                if getattr(b, "kind", None) == "preference":
                    tags = b.metadata.get("tags", [])
                    if any(t in tool_name for t in tags):
                        score += 0.5

            # Constraints penalize restricted tools
            if any(r in tool_name for r in restricted):
                score -= 1.0

            return score

        ctx["belief_score"] = belief_score  # executor may use this

        # ---------------------------------------------------------
        # C2: classify → build plan
        # ---------------------------------------------------------
        decision = self._classify(user_input)
        plan = self._build_plan(decision, memory_hits)

        # ---------------------------------------------------------
        # C2: execute plan
        # ---------------------------------------------------------
        exec_ctx = self._executor.execute(plan, ctx)

        # Attach beliefs to output so orchestrator can store them
        exec_ctx["beliefs"] = beliefs

        return exec_ctx

    # ------------------------------------------------------------------
    # Simple classifier
    # ------------------------------------------------------------------
    def _classify(self, user_input: str):
        text = user_input.lower()

        # For now: everything is fundamentals
        return {
            "kind": "fundamentals",
            "ticker": self._extract_ticker(user_input),
            "intent": user_input,
        }

    def _extract_ticker(self, text: str) -> Optional[str]:
        parts = text.replace(",", " ").split()
        if not parts:
            return None
        last = parts[-1].upper()
        if last.isalpha() and 1 <= len(last) <= 5:
            return last
        return None

    # ------------------------------------------------------------------
    # Plan construction
    # ------------------------------------------------------------------
    def _build_plan(self, decision: Dict[str, Any], memory_hits):
        if decision["kind"] == "fundamentals":
            ticker = decision["ticker"]
            if not ticker:
                raise ValueError("No ticker found for fundamentals request.")

            # Full research pipeline
            return build_full_research_plan(
                ticker=ticker,
                intent=decision["intent"],
                as_of=None,
            )

        raise ValueError(f"Unsupported route kind: {decision['kind']}")
