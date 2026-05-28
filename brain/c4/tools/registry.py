# brain/c4/tools/registry.py

from __future__ import annotations
from typing import Dict, Iterable, Optional, Any
from brain.c1.planner.tool_schema import ToolSchema


class ToolRegistry:
    """
    S4 ToolRegistry with full backward compatibility.

    Supports BOTH:
        ToolRegistry()
        ToolRegistry([tool1, tool2])
    """

    def __init__(self, tools: Optional[Iterable[Any]] = None):
        tools = tools or []  # <-- legacy compatibility
        self.tools: Dict[str, Any] = {t.name: t for t in tools}
        self.schemas: Dict[str, ToolSchema] = {}

        # Default LLM tool name
        self.default_llm = "lmstudio_llm"

    # -----------------------------------------------------
    # Registration API
    # -----------------------------------------------------
    def register(self, name: str, tool: Any, schema: Optional[ToolSchema] = None):
        self.tools[name] = tool
        if schema:
            self.schemas[name] = schema

    # -----------------------------------------------------
    # Lookup API
    # -----------------------------------------------------
    def get(self, name: str) -> Any:
        return self.tools[name]

    def get_schema(self, name: str) -> Optional[ToolSchema]:
        return self.schemas.get(name)

    def list_schemas(self) -> Dict[str, ToolSchema]:
        return dict(self.schemas)

    def list_tools(self) -> Dict[str, Any]:
        return dict(self.tools)
