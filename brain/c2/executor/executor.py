# brain/c2/executor/executor.py
from __future__ import annotations

from typing import Any, Dict, Optional

from brain.c1.planner.plan import PlanStep, PlanStepKind, ResearchPlan
from brain.c4.tools.builtin.fundamentals_tool import (
    FundamentalsRequest,
    FundamentalsResult,
    FUNDAMENTALS_TOOL_NAME,
)
from brain.c4.tools.registry import ToolRegistry


# ---------------------------------------------------------------------------
# Execution Context
# ---------------------------------------------------------------------------

class ExecutionContext:
    """
    Shared execution context across steps.
    C4 synthesizer reads from this.
    """

    def __init__(self) -> None:
        self._results: Dict[str, Any] = {}

    def set_result(self, key: str, value: Any) -> None:
        self._results[key] = value

    def get_result(self, key: str, default: Any = None) -> Any:
        return self._results.get(key, default)


# ---------------------------------------------------------------------------
# Plan Executor
# ---------------------------------------------------------------------------

class PlanExecutor:
    def __init__(self, llm: Any, tools: ToolRegistry) -> None:
        self._llm = llm
        self._tools = tools

    def execute(
        self,
        plan: ResearchPlan,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> ExecutionContext:

        exec_ctx = ExecutionContext()
        tool_ctx: Dict[str, Any] = ctx or {}

        for step in plan.steps:
            if step.kind == PlanStepKind.FUNDAMENTALS:
                self._execute_fundamentals_step(step, exec_ctx, tool_ctx)

            elif step.kind == PlanStepKind.SEARCH:
                self._execute_search_step(step, exec_ctx, tool_ctx)

            elif step.kind == PlanStepKind.SYNTHESIZE:
                # handled by C4 synthesizer
                continue

        return exec_ctx

    # -----------------------------------------------------------------------
    # Fundamentals step
    # -----------------------------------------------------------------------

    def _execute_fundamentals_step(
        self,
        step: PlanStep,
        exec_ctx: ExecutionContext,
        tool_ctx: Dict[str, Any],
    ) -> None:

        tool = self._tools.get(step.tool_name or FUNDAMENTALS_TOOL_NAME)

        request = FundamentalsRequest(
            ticker=step.params["ticker"],
            as_of=step.params.get("as_of"),
        )

        result: FundamentalsResult = tool.run(
            llm=self._llm,
            request=request,
            ctx=tool_ctx,
        )

        exec_ctx.set_result("fundamentals", result)

    # -----------------------------------------------------------------------
    # Existing search step (unchanged)
    # -----------------------------------------------------------------------

    def _execute_search_step(
        self,
        step: PlanStep,
        exec_ctx: ExecutionContext,
        tool_ctx: Dict[str, Any],
    ) -> None:
        ...
