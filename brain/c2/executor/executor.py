# brain/c2/executor/executor.py

from __future__ import annotations
from typing import Any, Dict, List

from brain.c4.tools.registry import ToolRegistry
from brain.c3.memory.base import MemoryProvider
from brain.c1.planner.plan import Plan, PlanStep


class Executor:
    """
    C2 Executor (Brain‑24 version)

    FIXED:
    - Stores tool results under their tool name (market_data, options_data, etc.)
    - Does NOT merge tool internals into state.context
    - Fully compatible with Synthesizer
    """

    def __init__(self, tools: ToolRegistry, memory: MemoryProvider):
        self.tools = tools
        self.memory = memory

    # ---------------------------------------------------------
    # Main entry point
    # ---------------------------------------------------------
    def execute_plan(self, plan: Plan, state):
        final_output = None

        # Ensure context exists
        if not hasattr(state, "context") or state.context is None:
            state.context = {}

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

            # Capture final LLM text
            if isinstance(result, dict) and result.get("text"):
                final_output = result["text"]

        return final_output or "Done."

    # ---------------------------------------------------------
    # Step dispatcher
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
    # TOOL EXECUTION
    # ---------------------------------------------------------
    def _execute_tool(self, step: PlanStep, state):
        tool_name = step.args.get("tool") if step.args else None
        tool_args = step.args.get("args", {}) if step.args else {}

        if tool_name not in self.tools.tools:
            return {"error": True, "message": f"Unknown tool: {tool_name}"}

        tool = self.tools.get(tool_name)
        result = tool.run(**tool_args)

        # ⭐ Store tool result under its tool name
        state.context[tool_name] = result

        # ⭐ Memory search support
        if isinstance(result, list):
            state.memory_results = result
        elif isinstance(result, dict) and "results" in result:
            state.memory_results = result["results"]

        return result

    # ---------------------------------------------------------
    # LLM EXECUTION
    # ---------------------------------------------------------
    def _execute_llm(self, step: PlanStep, state):
        llm_tool = self.tools.get(self.tools.default_llm)

        # Build memory context
        memory_context = ""
        if getattr(state, "memory_results", None):
            lines: List[str] = []
            for item in state.memory_results:
                content = item.get("content", "")
                lines.append(f"- {content}")
            memory_context = "\n".join(lines)

        prompt_text = step.args.get("prompt", "") if step.args else ""

        payload = {
            "text": prompt_text,
            "memory_context": memory_context,
        }

        raw = llm_tool.run(payload)

        # Normalize LLM output
        if isinstance(raw, dict):
            text = (
                raw.get("text")
                or raw.get("output")
                or raw.get("response")
                or raw.get("answer")
            )
        else:
            text = str(raw)

        return {
            "final": False,
            "llm_output": raw,
            "text": text,
        }
