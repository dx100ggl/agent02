from brain.c5.reflection_engine import ReflectionEngineV1
from brain.c5.reflection_types import ReflectionInput

def test_reflection_basic():
    r = ReflectionEngineV1()
    inp = ReflectionInput(
        task_id="1",
        planner_trace=[],
        executor_trace=[],
        final_output="ok",
        error=None,
        plan_trace=[],
    )
    out = r.reflect(inp)
    assert hasattr(out, "directives")
    assert hasattr(out, "findings")
    assert hasattr(out, "memory_updates")
