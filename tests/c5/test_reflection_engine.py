import pytest
from brain.c5.reflection_engine import ReflectionEngineV1
from brain.c5.reflection_types import ReflectionInput


def test_reflection_engine_basic_no_errors():
    engine = ReflectionEngineV1()

    r = ReflectionInput(
        task_id="t1",
        planner_trace=[],
        executor_trace=[],
        final_output={"result": "ok"},
        error=None,
    )

    out = engine.reflect(r)

    assert out.findings == []
    assert out.directives == []
    assert out.memory_updates == {}


def test_reflection_engine_detects_precondition_issue(monkeypatch):
    engine = ReflectionEngineV1()

    # Force heuristic to fire
    monkeypatch.setattr(
        engine, "_detect_missing_preconditions", lambda r: True
    )

    r = ReflectionInput(
        task_id="t2",
        planner_trace=[{"action": "tool_call"}],
        executor_trace=[],
        final_output=None,
        error=None,
    )

    out = engine.reflect(r)

    assert any(f.category == "planning_error" for f in out.findings)
    assert any("precondition" in d.directive.lower() for d in out.directives)
