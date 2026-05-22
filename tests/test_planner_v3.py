from brain.planner.adaptive_planner import AdaptivePlanner
from brain.state import BrainState


def test_planner_thinks_after_successful_tool():
    """
    After a successful tool step, planner v3 should follow up with a think step.
    """
    planner = AdaptivePlanner()
    state = BrainState("please search for apples")

    # Simulate a successful tool call in history
    state.history.append({
        "step": {"action": "use_tool", "tool": "search", "args": {"query": "please search for apples"}},
        "result": {"results": ["apple 1", "apple 2"]},
        "error": False,
        "retries": 0,
    })

    plan = planner.plan(state)
    assert isinstance(plan, list)
    assert plan[0]["action"] == "think"
