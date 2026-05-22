# brain/c5/heuristics/efficiency_rules.py

"""
Efficiency heuristics for C5 Reflection Engine v1.
Detects redundant or repeated tool calls.
"""

def detect_redundancy(planner_trace):
    """
    Detects repeated identical tool calls in the planner trace.

    Returns:
        bool
    """

    seen_calls = set()

    for step in planner_trace:
        if step.get("action") != "tool_call":
            continue

        tool = step.get("tool")
        args = step.get("args")

        signature = (tool, tuple(sorted(args.items())) if isinstance(args, dict) else None)

        if signature in seen_calls:
            return True

        seen_calls.add(signature)

    return False
