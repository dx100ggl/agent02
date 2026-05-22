# brain/c5/heuristics/planning_rules.py

"""
Planning heuristics for C5 Reflection Engine v1.
These rules are intentionally conservative and only fire on strong signals.
"""

def detect_missing_preconditions(planner_trace):
    """
    Detects when the planner executes a tool call without satisfying
    its declared preconditions.

    Expected trace format (example):
    {
        "step": 3,
        "action": "tool_call",
        "tool": "search",
        "args": {"query": "x"},
        "preconditions": ["memory_retrieved"],
        "preconditions_satisfied": False
    }

    Returns:
        bool
    """

    for step in planner_trace:
        if step.get("action") == "tool_call":
            # If the trace explicitly marks preconditions as unsatisfied
            if step.get("preconditions") and not step.get("preconditions_satisfied", True):
                return True

            # If the planner declares preconditions but does not check them
            if step.get("preconditions") and "preconditions_satisfied" not in step:
                return True

    return False
