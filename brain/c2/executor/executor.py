# brain/c2/executor/executor.py

from __future__ import annotations
import json
from typing import Any, Dict

from brain.c1.planner.plan import ResearchPlan, PlanStep, PlanStepKind
from brain.llm.lmstudio_llm import LMStudioLLM


class Executor:
    """
    Deterministic C2 executor (Option A).
    Executes steps in order.
    If a tool fails, asks the LLM for a repair.
    Retries once with repaired arguments.
    """

    def __init__(self, tools, synthesizer, llm: LMStudioLLM):
        self._tools = tools
        self._synth = synthesizer
        self._llm = llm
        self.enable_argument_validation = False


    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------
    def execute(self, plan: ResearchPlan, ctx: Dict[str, Any]) -> Dict[str, Any]:
        exec_ctx = {"steps": [], "final": None}

        for step in plan.steps:
            step_result = self._execute_step(step, exec_ctx)
            exec_ctx["steps"].append(step_result)

        exec_ctx["final"] = exec_ctx["steps"][-1] if exec_ctx["steps"] else None
        return exec_ctx

    # ------------------------------------------------------------------
    # Step execution
    # ------------------------------------------------------------------
    def _execute_step(self, step: PlanStep, exec_ctx: Dict[str, Any]) -> Dict[str, Any]:
        kind = step.kind

        if kind == PlanStepKind.FUNDAMENTALS:
            return self._execute_fundamentals(step)

        if kind == PlanStepKind.SYNTHESIZE:
            return self._execute_synthesis(step, exec_ctx)

        if kind == PlanStepKind.TOOL:
            return self._execute_tool(step)

        if kind == PlanStepKind.SEARCH:
            return self._execute_search(step)
        
        if kind == PlanStepKind.MARKET_DATA:
            return self._execute_tool(step)

        if kind == PlanStepKind.TECHNICALS:
            return self._execute_tool(step)

        if kind == PlanStepKind.OPTIONS:
            return self._execute_tool(step)

        if kind == PlanStepKind.SENTIMENT:
            return self._execute_tool(step)

        if kind == PlanStepKind.MACRO:
            return self._execute_tool(step)

        if kind == PlanStepKind.ANALOGS:
            return self._execute_tool(step)        

        return {"step": step, "error": True, "message": f"Unknown step kind: {kind}"}

    # ------------------------------------------------------------------
    # Fundamentals step
    # ------------------------------------------------------------------
    def _execute_fundamentals(self, step: PlanStep) -> Dict[str, Any]:
        tool = self._tools.get(step.tool_name)
        args = step.params

        result = self._safe_tool_call(tool, args)
        if not self._is_failure(result):
            return {"step": step, "result": result, "repaired": False}

        # Repair attempt
        repaired_args = self._repair_args(step, args, result)
        result2 = self._safe_tool_call(tool, repaired_args)

        return {
            "step": step,
            "result": result2,
            "repaired": True,
            "repair_args": repaired_args,
        }

    # ------------------------------------------------------------------
    # Synthesis step
    # ------------------------------------------------------------------
    def _execute_synthesis(self, step: PlanStep, exec_ctx: Dict[str, Any]) -> Dict[str, Any]:
        result = self._synth.synthesize(step.params, exec_ctx)
        return {"step": step, "result": result, "repaired": False}

    # ------------------------------------------------------------------
    # Generic tool step
    # ------------------------------------------------------------------
    def _execute_tool(self, step: PlanStep) -> Dict[str, Any]:
        tool = self._tools.get(step.tool_name)
        args = step.params

        result = self._safe_tool_call(tool, args)
        if not self._is_failure(result):
            return {"step": step, "result": result, "repaired": False}

        repaired_args = self._repair_args(step, args, result)
        result2 = self._safe_tool_call(tool, repaired_args)

        return {
            "step": step,
            "result": result2,
            "repaired": True,
            "repair_args": repaired_args,
        }

    # ------------------------------------------------------------------
    # Search step (optional)
    # ------------------------------------------------------------------
    def _execute_search(self, step: PlanStep) -> Dict[str, Any]:
        # Placeholder: you can wire in a search tool later
        return {"step": step, "result": {"search": "not implemented"}, "repaired": False}

    # ------------------------------------------------------------------
    # Tool call wrapper
    # ------------------------------------------------------------------
    def _safe_tool_call(self, tool, args: Dict[str, Any]) -> Any:
        try:
            if self.enable_argument_validation:
                self._validate_args(tool, args)

            return tool.run(**args)
        except Exception as e:
            return {"error": True, "message": str(e)}

    def _is_failure(self, result: Any) -> bool:
        return isinstance(result, dict) and result.get("error")

    # ------------------------------------------------------------------
    # LLM-based argument repair
    # ------------------------------------------------------------------
    def _repair_args(self, step: PlanStep, args: Dict[str, Any], failure: Any) -> Dict[str, Any]:
        prompt = f"""
A tool call failed.

Tool: {step.tool_name}
Original arguments: {args}
Failure: {failure}

Task:
Suggest corrected arguments as a JSON dict.
Only return the JSON. No commentary.
"""

        raw = self._llm.complete(prompt)

        try:
            repaired = json.loads(raw)
            if isinstance(repaired, dict):
                return repaired
        except Exception:
            pass

        return args

    def _validate_args(self, tool, args):
        """
        Validate arguments against the tool's declared schema.
        """
        schema = getattr(tool, "schema", None)
        if not schema:
            return True  # No schema → nothing to validate

        # Required fields
        required = schema.get("required", [])
        for field in required:
            if field not in args:
                raise ValueError(f"Missing required argument '{field}' for tool '{tool.name}'")

        # Type checks
        properties = schema.get("properties", {})
        for key, expected in properties.items():
            if key in args:
                if expected == "string" and not isinstance(args[key], str):
                    raise TypeError(f"Argument '{key}' must be a string for tool '{tool.name}'")
                if expected == "number" and not isinstance(args[key], (int, float)):
                    raise TypeError(f"Argument '{key}' must be a number for tool '{tool.name}'")
                if expected == "boolean" and not isinstance(args[key], bool):
                    raise TypeError(f"Argument '{key}' must be a boolean for tool '{tool.name}'")

        return True
