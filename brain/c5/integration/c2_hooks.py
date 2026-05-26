from typing import List
from brain.c5.reflection_types import ReflectionDirective


def apply_directives_to_planner(planner, directives: List[ReflectionDirective]):
    """
    Applies high-level behavioral adjustments to the planner.
    """

    for d in directives:
        text = d.directive.lower()

        if "precondition" in text:
            planner.set_flag("enforce_preconditions", True)

        if "validate tool arguments" in text:
            planner.set_flag("validate_tool_args", True)

        if "avoid long reasoning chains" in text:
            planner.set_preference("max_chain_length", 3.0)

        if "avoid repeating" in text:
            planner.set_flag("avoid_redundant_calls", True)

        if "adjust_mode:more_cautious" in text:
            planner.meta_mode = "more_cautious"

    return planner
