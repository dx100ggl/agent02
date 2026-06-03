# brain/c2/router/dynamic_router.py

from __future__ import annotations
from typing import Any, Dict, Optional

from brain.c1.planner.plan import ResearchPlan, build_fundamentals_plan, build_full_research_plan
from brain.c3.memory.memory_service import MemoryService
from brain.llm.lmstudio_llm import LMStudioLLM
from brain.c2.executor.executor import Executor



class DynamicRouter:
    """
    C2 router with C3 memory integration.
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

        # C3: retrieve memory
        memory_hits = self._memory.retrieve(user_input)
        ctx["memory"] = memory_hits

        # C2: classify → build plan
        decision = self._classify(user_input)
        plan = self._build_plan(decision, memory_hits)

        # C2: execute
        exec_ctx = self._executor.execute(plan, ctx)
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

            # return build_fundamentals_plan(
            #     ticker=ticker,
            #     intent=decision["intent"],
            #     as_of=None,
            # )
        
            return build_full_research_plan(
                ticker=ticker,
                intent=decision["intent"],
                as_of=None,
            )        

        raise ValueError(f"Unsupported route kind: {decision['kind']}")
