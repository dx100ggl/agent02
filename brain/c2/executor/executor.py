# brain/c2/executor/executor.py

from brain.c4.tools.base import Tool


class Executor:
    """
    C2 Executor — now LLM‑aware.
    Executes planner steps and delegates to tools or LLM backends.
    """

    def __init__(self, tools=None, memory=None):
        self.tools = tools
        self.memory = memory

    # ---------------------------------------------------------
    # LLM helper
    # ---------------------------------------------------------
    def _call_llm(self, state, prompt: str | None = None):
        if prompt is None:
            prompt = getattr(state, "user_input", "")

        backend_name = getattr(self.tools, "default_llm", None)
        if backend_name is None:
            return {"final": True, "answer": f"[LLM response to: {prompt}]"}

        llm_tool = self.tools.tools.get(backend_name)
        if llm_tool is None:
            return {"final": True, "answer": f"[LLM response to: {prompt}]"}

        return llm_tool.run(prompt)

    # ---------------------------------------------------------
    # Main execution entry
    # ---------------------------------------------------------
    def execute(self, step, state):
        action = step.get("action")

        # LLM call
        if action == "llm":
            return self._call_llm(state, step.get("prompt"))

        # Thought step
        if action == "think":
            return {"thought": step.get("content", "")}

        # Tool call
        if action == "use_tool":
            tool_name = step.get("tool")
            tool_args = step.get("args", {})

            tool = self.tools.tools.get(tool_name)
            if tool is None:
                return {"error": True, "message": f"Unknown tool: {tool_name}"}

            return tool.run(**tool_args)

        # Finish step
        if action == "finish":
            return {"final": True, "answer": step.get("message", "")}

        return {"error": True, "message": f"Unknown action: {action}"}
