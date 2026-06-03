# brain/c4/tools/registry.py

from __future__ import annotations
from typing import Dict, Iterable, Optional, Any
from brain.c1.planner.tool_schema import ToolSchema

from brain.c4.tools.base import Tool

# Built‑in tools
from brain.c4.tools.builtin.market_data_tool import MarketDataTool
from brain.c4.tools.builtin.technicals_tool import TechnicalsTool
from brain.c4.tools.builtin.options_data_tool import OptionsDataTool
from brain.c4.tools.builtin.real_options_data_tool import RealOptionsDataTool
from brain.c4.tools.builtin.sentiment_tool import SentimentTool
from brain.c4.tools.builtin.macro_tool import MacroTool
from brain.c4.tools.builtin.analogs_tool import AnalogsTool
from brain.c4.tools.builtin.fundamentals_tool import FundamentalsTool


class ToolRegistry:
    """
    Unified C4 ToolRegistry with consistent naming.
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
        self.register("technicals_data", TechnicalsTool())
        self.register("options_data", OptionsDataTool())
        self.register("real_options_data", RealOptionsDataTool())
        self.register("sentiment_data", SentimentTool())
        self.register("macro_data", MacroTool())
        self.register("analogs_data", AnalogsTool())
        self.register("fundamentals_data", FundamentalsTool())

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


# -------------------------------------------------------------------------
# Default registry bootstrap
# -------------------------------------------------------------------------

def build_default_tool_registry() -> ToolRegistry:
    """
    Standard registry bootstrap used by CLI entrypoints and orchestrators.
    Ensures all builtin tools (including fundamentals) are registered.
    """
    return ToolRegistry()
