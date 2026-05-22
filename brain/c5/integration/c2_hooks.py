# brain/c5/integration/c2_hooks.py

"""
C5 → C2 integration hooks.
These functions apply reflection directives to the planner subsystem.
"""

from typing import List
from brain.c5.reflection_types import ReflectionDirective


def apply_directives_to_planner(planner, directives: List[ReflectionDirective]):
    """
    Applies high-level behavioral adjustments to the planner.

    Expected planner interface:
        planner.set_flag(key: str, value: bool)
        planner.set_preference(key: str, weight: float)

    This hook is intentionally conservative.
    """

    for d in directives:
        text = d.directive.lower()

        # Precondition enforcement
        if "precondition" in text:
            planner.set_flag("enforce_preconditions", True)

        # Tool argument validation
        if "validate tool arguments" in text:
            planner.set_flag("validate_tool_args", True)

        # Avoid long chains
        if "avoid long reasoning chains" in text:
            planner.set_preference("max_chain_length", 3.0)

        # Avoid redundant calls
        if "avoid repeating" in text:
            planner.set_flag("avoid_redundant_calls", True)

    return planner
