# brain/c5/integration/c4_hooks.py

"""
C5 → C4 integration hooks.
Updates skill/tool metadata based on reflection directives.
"""

from typing import List
from brain.c5.reflection_types import ReflectionDirective


def apply_skill_metadata_updates(skill_registry, directives: List[ReflectionDirective]):
    """
    Updates tool metadata in the skill registry.

    Expected skill_registry interface:
        skill_registry.set_tool_metadata(tool_name: str, key: str, value: Any)
    """

    for d in directives:
        text = d.directive.lower()

        # Tool argument validation
        if "validate tool arguments" in text:
            for tool_name in skill_registry.list_tools():
                skill_registry.set_tool_metadata(tool_name, "requires_validation", True)

        # Precondition enforcement
        if "precondition" in text:
            for tool_name in skill_registry.list_tools():
                skill_registry.set_tool_metadata(tool_name, "requires_preconditions", True)

    return skill_registry
