from brain.c4.tools.base import Tool


class SearchTool(Tool):
    """
    Minimal fake search tool used by the test suite.
    Always returns a predictable structure.
    """

    def __init__(self, name="search"):
        super().__init__(name)

    def run(self, query: str = ""):
        return {
            "results": [
                {"item": f"Result for: {query}"}
            ]
        }
