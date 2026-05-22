# brain/c5/heuristics/tool_rules.py

"""
Tool misuse heuristics for C5 Reflection Engine v1.
Detects invalid or missing arguments based on tool metadata.
"""

def detect_tool_misuse(executor_trace):
    """
    Detects when a tool call fails due to invalid arguments.

    Expected executor trace format:
    {
        "tool": "search",
        "args": {"query": None},
        "error": "Missing required argument: query"
    }

    Returns:
        Optional[str] - description of misuse
    """

    for step in executor_trace:
        error = step.get("error")
        if not error:
            continue

        # Strong signals of misuse
        if "Missing required argument" in error:
            return error

        if "Invalid type" in error:
            return error

        if "Unexpected argument" in error:
            return error

        if "schema" in error.lower():
            return error

    return None
