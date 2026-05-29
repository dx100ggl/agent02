from brain.c2.orchestrator import Orchestrator
from brain.c1.state import State

def test_orchestrator_runs_end_to_end():
    o = Orchestrator()
    s = State(user_input="hello")
    out = o.run(s)
    assert isinstance(out, str)
    assert s.done is True
    assert len(s.history) >= 1
