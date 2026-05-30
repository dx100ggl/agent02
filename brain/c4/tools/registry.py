# brain/c4/tools/registry.py

from __future__ import annotations
from typing import Dict, Iterable, Optional, Any
from brain.c1.planner.tool_schema import ToolSchema

from brain.c4.tools.base import Tool
from brain.c4.tools.builtin.market_data_tool import MarketDataTool
from brain.c4.tools.builtin.options_data_tool import OptionsDataTool
from brain.c4.tools.builtin.sentiment_tool import SentimentTool
from brain.c4.tools.builtin.macro_tool import MacroTool
from brain.c4.tools.builtin.analog_search_tool import AnalogSearchTool


class ToolRegistry:
    """
    S4 ToolRegistry with backward compatibility.
    """

    def __init__(self, tools: Optional[Iterable[Any]] = None):
        tools = tools or []

        # Load any tools passed in (legacy behavior)
        self.tools: Dict[str, Any] = {t.name: t for t in tools}
        self.schemas: Dict[str, ToolSchema] = {}

        # Default LLM tool name
        self.default_llm = "lmstudio_llm"

        # -----------------------------------------------------
        # Register built‑in research tools (canonical names)
        # -----------------------------------------------------
        self.register("market_data", MarketDataTool())
        self.register("options_data", OptionsDataTool())
        self.register("sentiment", SentimentTool())
        self.register("macro", MacroTool())
        self.register("analog_search", AnalogSearchTool())

    # ---------------------------------------------------------
    # Registration API
    # ---------------------------------------------------------
    def register(self, name: str, tool: Any, schema: Optional[ToolSchema] = None):
        self.tools[name] = tool
        if schema:
            self.schemas[name] = schema

    # ---------------------------------------------------------
    # Lookup API
    # ---------------------------------------------------------
    def get(self, name: str) -> Any:
        return self.tools[name]

    def get_schema(self, name: str) -> Optional[ToolSchema]:
        return self.schemas.get(name)

    def list_schemas(self) -> Dict[str, ToolSchema]:
        return dict(self.schemas)

    def list_tools(self) -> Dict[str, Any]:
        return dict(self.tools)
