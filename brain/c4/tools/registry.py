# brain/c4/tools/registry.py

from typing import Dict, Any, Optional
from brain.c1.planner.tool_schema import ToolSchema


class ToolRegistry:
    """
    Registry for all tools available to the agent.
    Memory-aware and provides a default LLM tool.
    """

    def __init__(self, memory=None):
        self.memory = memory
        self.tools: Dict[str, Any] = {}
        self.schemas: Dict[str, ToolSchema] = {}
        self.default_llm = "llm"

        # Register memory tools if memory is provided
        if memory is not None:
            self.register("write_memory", memory.write)
            self.register("search_memory", memory.search)

        # Provide a default lmstudio_llm tool so build_brain() never fails
        class DummyLMStudioLLM:
            def run(self, prompt):
                return {"answer": f"dummy:{prompt}"}

        self.register("lmstudio_llm", DummyLMStudioLLM())

    def register(self, name: str, tool: Any, schema: Optional[ToolSchema] = None):
        self.tools[name] = tool
        if schema:
            self.schemas[name] = schema

    def get(self, name: str):
        return self.tools[name]

    def get_schema(self, name: str) -> Optional[ToolSchema]:
        return self.schemas.get(name)

    def list_schemas(self):
        return self.schemas
