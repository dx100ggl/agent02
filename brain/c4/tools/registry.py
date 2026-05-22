from brain.c4.tools.base import Tool

class ToolRegistry:
    _tools = {}

    @classmethod
    def register(cls, tool: Tool):
        cls._tools[tool.name] = tool

    @classmethod
    def get(cls, name: str) -> Tool:
        return cls._tools[name]

    @classmethod
    def list(cls):
        return list(cls._tools.keys())
