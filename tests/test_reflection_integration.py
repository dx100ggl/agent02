# tests/test_reflection_integration.py

def test_reflection_does_not_affect_default_cycle():
    from brain.c2.orchestrator import Orchestrator
    from brain.c1.state import State

    orch = Orchestrator()
    state = State(task_id="t1", user_input="hello world")

    output = orch.run(state)

    # Output should be a string (your synthesizer returns strings)
    assert isinstance(output, str)
    assert "hello" in output.lower()

    # Reflection metadata should exist
    assert "reflection" in state.meta
    assert "findings" in state.meta["reflection"]
    assert "directives" in state.meta["reflection"]
