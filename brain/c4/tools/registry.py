# brain/c4/tools/registry.py

from brain.c4.tools.base import Tool
from brain.c4.tools.builtin.lmstudio_llm import LMStudioLLM
from brain.c4.tools.builtin.search_tool import SearchTool

# New memory tools
from brain.c4.tools.builtin.write_memory_tool import WriteMemoryTool
from brain.c4.tools.builtin.search_memory_tool import SearchMemoryTool


class ToolRegistry:
    """
    Instance-based tool registry.

    Supports:
    - dynamic registration
    - multiple LLM backends
    - default LLM selection
    - clean integration with Executor
    - memory-aware tools (write_memory, search_memory)
    """

    def __init__(self, memory=None):
        # Instance-level registry
        self.tools = {}

        # Memory is optional, but required for memory tools
        self.memory = memory

        # -----------------------------
        # Built-in tools
        # -----------------------------
        self.register(LMStudioLLM(name="lmstudio_llm"))
        self.register(SearchTool())

        # Register memory tools only if memory is provided
        if self.memory is not None:
            self.register(WriteMemoryTool(self.memory))
            self.register(SearchMemoryTool(self.memory))

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
