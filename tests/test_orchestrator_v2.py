from brain.build import build_brain
from brain.c1.state import BrainState


def test_orchestrator_runs_multi_step_plan():
    """
    Orchestrator should execute multi-step plans produced by the planner.
    For input containing 'search', planner returns:
        [use_tool, think]
    So orchestrator should execute exactly one step and stop (single-step termination rule).
    """
    brain = build_brain()
    state = BrainState("please search for apples")

    result = brain.run(state)

    # Should be a dict result
    assert isinstance(result, dict)

    # Should have executed at least one step
    assert len(state.history) >= 1

    # First step should be a tool step
    first_step = state.history[0]["step"]
    assert first_step["action"] == "use_tool"


def test_orchestrator_stops_on_final_signal():
    """
    If a tool or LLM returns {"final": True}, orchestrator should stop immediately.
    We simulate this by monkeypatching executor to return final=True.
    """
    brain = build_brain()

    # Monkeypatch executor
    def final_executor(step, state):
        return {"final": True, "answer": "done"}

    brain.executor.execute = final_executor

    state = BrainState("hello")
    result = brain.run(state)

    assert result.get("final") is True
    assert result.get("answer") == "done"
    assert state.done is True
    assert len(state.history) == 1


def test_orchestrator_max_depth():
    """
    If orchestrator exceeds MAX_STEPS, it should terminate with an error.
    We simulate this by forcing planner to always return a think step.
    """
    brain = build_brain()

    # Monkeypatch planner to produce infinite think steps
    def infinite_plan(state):
        return [{"action": "think"}, {"action": "think"}]


    brain.planner.plan = infinite_plan

    state = BrainState("loop forever")
    result = brain.run(state)

    assert result.get("error") is True
    assert "Max cognitive depth" in result.get("message", "")
    assert state.done is True


def test_orchestrator_propagates_errors():
    """
    If executor returns {"error": True}, orchestrator should record it in history.
    """
    brain = build_brain()

    # Monkeypatch executor to always error
    def failing_executor(step, state):
        return {"error": True, "message": "fail"}

    brain.executor.execute = failing_executor

    state = BrainState("hello")
    result = brain.run(state)

    # Should record error in history
    assert state.history[-1]["error"] is True
    assert result.get("error") is True


def test_orchestrator_single_step_plan_terminates():
    """
    If planner returns a single-step plan, orchestrator should treat the result as final.
    """
    brain = build_brain()

    # Monkeypatch planner to return a single think step
    def single_step_plan(state):
        return [{"action": "think"}]

    brain.planner.plan = single_step_plan

    # Monkeypatch executor to return a predictable result
    def think_executor(step, state):
        return {"thought": "ok"}

    brain.executor.execute = think_executor

    state = BrainState("hello")
    result = brain.run(state)

    assert result == {"thought": "ok"}
    assert state.done is True
    assert len(state.history) == 1
