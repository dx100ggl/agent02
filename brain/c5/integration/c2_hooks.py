# brain/c5/integration/c2_hooks.py

from typing import List, Dict, Any
from brain.c5.reflection_types import ReflectionDirective
from brain.c3.memory.memory_service import MemoryService


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


# ----------------------------------------------------------------------
# NEW: Inject C5 beliefs into planner context
# ----------------------------------------------------------------------

def inject_beliefs_into_planner_context(
    memory: MemoryService,
    planner_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Enrich planner context with stable beliefs from C5.
    This is safe, optional, and does not modify planner behavior directly.
    """

    beliefs = memory.get_beliefs()

    # Expose beliefs as simple strings for now
    planner_context["stable_beliefs"] = [
        b.content for b in beliefs
    ]

    return planner_context
