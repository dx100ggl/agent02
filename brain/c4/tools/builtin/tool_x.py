from brain.c4.tools.base import Tool

class SearchTool(Tool):
    name = "search"
    description = "Searches local index"

    def run(self, query: str):
        return {"results": ["item1", "item2"]}
