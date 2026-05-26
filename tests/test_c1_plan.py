from brain.c1.planner.plan import Plan

def test_plan_basic():
    p = Plan("hello")
    p.add_step("do something", tool="llm", args={"prompt": "hi"})
    assert len(p.steps) == 1
    assert p.steps[0].tool == "llm"

def test_plan_trace_logging():
    p = Plan("hello")
    p.log("event_x", {"a": 1})
    assert p.trace[0]["event"] == "event_x"
    assert p.trace[0]["data"]["a"] == 1
