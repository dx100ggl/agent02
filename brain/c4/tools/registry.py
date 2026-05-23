# brain/c4/tools/registry.py

from brain.c4.tools.base import Tool
from brain.c4.tools.builtin.lmstudio_llm import LMStudioLLM
from brain.c4.tools.builtin.search_tool import SearchTool

class ToolRegistry:
    """
    Instance-based tool registry.
    Supports:
    - dynamic registration
    - multiple LLM backends
    - default LLM selection
    - clean integration with Executor
    """

    def __init__(self):
        # Instance-level registry
        self.tools = {}

        # Register built-in tools here
        # (Your existing builtins will also be registered the same way)
        self.register(LMStudioLLM(name="lmstudio_llm"))
        self.register(SearchTool())

        # Default LLM backend (can be overridden in build_brain)
        self.default_llm = "lmstudio_llm"

    # -----------------------------
    # Registration API
    # -----------------------------
    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self.tools[name]

    def list(self):
        return list(self.tools.keys())
