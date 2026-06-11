from brain.c4.tools.base import Tool


class SearchTool(Tool):
    """
    Minimal fake search tool used by the test suite.
    Now includes a schema so Executor argument validation works.
    """

    # Tool name used by registry
    name = "search"

    # Schema for argument validation
    schema = {
        "required": ["query"],
        "properties": {
            "query": "string"
        }
    }

    def __init__(self):
        super().__init__(self.name)

    def run(self, args):
        """
        Executor now passes args as a dict, not a raw string.
        """
        query = args.get("query", "")
        return {
            "results": [
                {"item": f"Result for: {query}"}
            ]
        }
