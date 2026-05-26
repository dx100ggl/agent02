from __future__ import annotations
from typing import Any, Dict

from brain.c4.tools.registry import ToolRegistry
from brain.c3.memory.store import MemoryStore
from brain.c1.planner.plan import Plan, PlanStep


class Executor:
    """
    C2 Executor.

    Executes a Plan:
    - each PlanStep may be: use_tool, llm, think
    - results are written back into the Plan
    """

    def __init__(self, tools: ToolRegistry, memory: MemoryStore):
        self.tools = tools
        self.memory = memory

    # ---------------------------------------------------------
    # Main entry point: execute a full Plan
    # ---------------------------------------------------------
    def execute_plan(self, plan: Plan, state):
        """
        Execute all steps in a Plan.
        Returns the final LLM text or tool output.
        """
        final_output = None

        for i, step in enumerate(plan.steps):
            plan.log("step_start", {
                "index": i,
                "description": step.description,
                "tool": step.tool,
                "args": step.args,
            })

            result = self._execute_step(step, state)
            plan.set_result(i, result)

            plan.log("step_result", {
                "index": i,
                "result": result,
            })

            if isinstance(result, dict) and result.get("text"):
                final_output = result["text"]

        return final_output or "Done."

    # ---------------------------------------------------------
    # Execute a single PlanStep
    # ---------------------------------------------------------
    def _execute_step(self, step: PlanStep, state) -> Dict[str, Any]:
        action = step.tool or step.description.lower()

        if step.tool == "use_tool":
            return self._execute_tool(step, state)

        if step.tool == "llm":
            return self._execute_llm(step, state)

        if step.tool == "think" or action == "think":
            return {"final": False, "thought": "thinking"}

        return {"error": True, "message": f"Unknown step/tool: {step.tool}"}

    # ---------------------------------------------------------
    # Tool execution
    # ---------------------------------------------------------
    def _execute_tool(self, step: PlanStep, state):
        tool_name = step.args.get("tool") if step.args else None
        tool_args = step.args.get("args", {}) if step.args else {}

        if tool_name not in self.tools.tools:
            return {"error": True, "message": f"Unknown tool: {tool_name}"}

        tool = self.tools.get(tool_name)
        result = tool.run(**tool_args)

        if isinstance(result, dict) and "results" in result:
            state.memory_results = result["results"]

        return result

    # ---------------------------------------------------------
    # LLM execution (memory‑aware)
    # ---------------------------------------------------------
    def _execute_llm(self, step: PlanStep, state):
        llm_tool = self.tools.get(self.tools.default_llm)

        memory_context = ""
        if getattr(state, "memory_results", None):
            memory_context = "\n".join(
                f"- {item.text}" for item in state.memory_results
            )

        prompt_payload = {
            "text": step.args.get("prompt", "") if step.args else "",
            "memory_context": memory_context,
        }

        raw = llm_tool.run(prompt_payload)

        if isinstance(raw, dict):
            text = raw.get("text") or raw.get("output") or raw.get("response")
        else:
            text = str(raw)

        return {
            "final": False,
            "llm_output": raw,
            "text": text,
        }
