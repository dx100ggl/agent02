# brain/c2/executor/executor.py

from __future__ import annotations
from typing import Any, Dict

from brain.c4.tools.registry import ToolRegistry
from brain.c3.memory.store import MemoryStore


class Executor:
    """
    C2 Executor.

    Executes a single step:
    - use_tool
    - llm
    - think (no-op)
    """

    def __init__(self, tools: ToolRegistry, memory: MemoryStore):
        self.tools = tools
        self.memory = memory

    # ---------------------------------------------------------
    # Main entry point
    # ---------------------------------------------------------
    def execute(self, step: Dict[str, Any], state) -> Dict[str, Any]:
        action = step.get("action")

        if action == "use_tool":
            return self._execute_tool(step, state)

        if action == "llm":
            return self._execute_llm(step, state)

        if action == "think":
            return {"final": False, "thought": "thinking"}

        return {"error": True, "message": f"Unknown action: {action}"}

    # ---------------------------------------------------------
    # Tool execution
    # ---------------------------------------------------------
    def _execute_tool(self, step: Dict[str, Any], state):
        tool_name = step.get("tool")
        tool_args = step.get("args", {})

        if tool_name not in self.tools.tools:
            return {"error": True, "message": f"Unknown tool: {tool_name}"}

        tool = self.tools.get(tool_name)
        result = tool.run(**tool_args)

        # Store memory search results into state for follow-up LLM
        if isinstance(result, dict) and "results" in result:
            state.memory_results = result["results"]

        return result

    # ---------------------------------------------------------
    # LLM execution (Option B: memory-aware)
    # ---------------------------------------------------------
    def _execute_llm(self, step: Dict[str, Any], state):
        llm_tool = self.tools.get(self.tools.default_llm)

        # Build memory context for the LLM
        memory_context = ""
        if getattr(state, "memory_results", None):
            memory_context = "\n".join(
                f"- {item.text}" for item in state.memory_results
            )

        # Build prompt dict for LMStudioLLM
        prompt_payload = {
            "text": step.get("prompt", ""),
            "memory_context": memory_context,
        }

        return llm_tool.run(prompt_payload)
