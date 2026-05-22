from brain.c5.integration.c2_hooks import apply_directives_to_planner
from brain.c5.integration.c3_hooks import apply_memory_updates
from brain.c5.integration.c4_hooks import apply_skill_metadata_updates
from brain.c5.reflection_types import ReflectionDirective


class DummyPlanner:
    def __init__(self):
        self.flags = {}
        self.prefs = {}

    def set_flag(self, key, value):
        self.flags[key] = value

    def set_preference(self, key, value):
        self.prefs[key] = value


class DummyMemory:
    def __init__(self):
        self.data = {}

    def write(self, key, value):
        self.data[key] = value

    def update_namespace(self, ns, data):
        self.data.setdefault(ns, {}).update(data)


class DummyTools:
    def __init__(self):
        self.meta = {}
        self.tools = ["search", "calc"]

    def list_tools(self):
        return self.tools

    def set_tool_metadata(self, tool, key, value):
        self.meta.setdefault(tool, {})[key] = value


def test_c2_hook_sets_planner_flags():
    planner = DummyPlanner()
    directives = [ReflectionDirective("Ensure precondition checks before tool calls.", 5)]

    apply_directives_to_planner(planner, directives)

    assert planner.flags.get("enforce_preconditions") is True


def test_c3_hook_updates_memory():
    memory = DummyMemory()
    updates = {"tools": {"search": {"requires_validation": True}}}

    apply_memory_updates(memory, updates)

    assert memory.data["tools"]["search"]["requires_validation"] is True


def test_c4_hook_updates_tool_metadata():
    registry = DummyTools()
    directives = [ReflectionDirective("Validate tool arguments before execution.", 4)]

    apply_skill_metadata_updates(registry, directives)

    assert registry.meta["search"]["requires_validation"] is True
    assert registry.meta["calc"]["requires_validation"] is True
