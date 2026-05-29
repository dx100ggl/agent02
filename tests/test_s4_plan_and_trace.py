# tests/test_s4_plan_and_trace.py

from __future__ import annotations

from brain.c1.planner.plan import Plan


def test_s4_planstep_canonical_fields():
    plan = Plan(user_input="test")
    plan.add_step(
        description="Call tool search_memory",
        tool="use_tool",
        args={"tool": "search_memory", "args": {"query": "hello"}},
    )

    assert len(plan.steps) == 1
    step = plan.steps[0]

    # Backward-compatible fields
    assert step.description == "Call tool search_memory"
    assert step.tool == "use_tool"
    assert step.args == {"tool": "search_memory", "args": {"query": "hello"}}

    # S4 fields
    assert step.index == 0
    assert isinstance(step.timestamp, str)

    # Canonicalization
    assert step.canonical_action() in ("use_tool", "call tool search_memory")
    assert step.canonical_params() == {"tool": "search_memory", "args": {"query": "hello"}}


def test_s4_plan_trace_events():
    plan = Plan(user_input="trace test")
    plan.add_step(description="LLM reasoning", tool="llm", args={"prompt": "hi"})
    plan.set_result(0, {"text": "hello"})

    events = [e["event"] for e in plan.trace]
    assert "step_added" in events
    assert "step_result" in events

    # Ensure step_result event has index and result
    step_result_events = [e for e in plan.trace if e["event"] == "step_result"]
    assert step_result_events
    data = step_result_events[0]["data"]
    assert data["index"] == 0
    assert data["result"] == {"text": "hello"}
