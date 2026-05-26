from brain.c2.orchestrator import Orchestrator
from brain.c1.state import State

def test_full_c6_cycle():
    o = Orchestrator()
    s = State(user_input="hello world")
    s.debug_visualize_plan = True

    out = o.run(s)

    assert isinstance(out, str)
    assert s.done is True
    assert len(s.history) >= 1
    assert hasattr(s, "plan_visualization")
    assert "=== PLAN ===" in s.plan_visualization
