from typing import Dict, Any, Optional
from brain.c1.planner.tool_schema import ToolSchema


class ToolRegistry:
    """
    Registry for all tools available to the agent.
    """

    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.schemas: Dict[str, ToolSchema] = {}
        self.default_llm = "llm"

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
