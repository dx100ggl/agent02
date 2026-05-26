from brain.c5.integration.c2_hooks import apply_directives_to_planner
from brain.c5.reflection_types import ReflectionDirective

def test_directive_adjusts_planner_mode():
    class P:
        def __init__(self):
            self.meta_mode = "default"
            self.flags = {}
            self.preferences = {}

        def set_flag(self, k, v):
            self.flags[k] = v

        def set_preference(self, k, v):
            self.preferences[k] = v

    p = P()
    directives = [
        ReflectionDirective("adjust_mode:more_cautious", 5),
        ReflectionDirective("Validate tool arguments against schema.", 4),
    ]
    apply_directives_to_planner(p, directives)
    assert p.meta_mode == "more_cautious"
    assert p.flags.get("validate_tool_args") is True
