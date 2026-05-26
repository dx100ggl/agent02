from brain.c4.tools.base import Tool


class SearchMemoryTool(Tool):
    """
    Tool to search long-term memory.
    """

    def __init__(self, memory, name: str = "search_memory"):
        super().__init__(name)
        self.memory = memory

    def run(self, query: str):
        """
        query: natural language query for memory.
        """
        results = self.memory.search(query)
        return {
            "final": False,
            "results": results,
        }
