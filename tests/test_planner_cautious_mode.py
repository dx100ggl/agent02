# tests/test_planner_cautious_mode.py

def test_cautious_mode_adds_verification_steps():
    from brain.c1.planner.adaptive_planner import AdaptivePlanner
    from brain.c4.tools.registry import ToolRegistry

    planner = AdaptivePlanner(tools=ToolRegistry())
    planner.set_cautious(True)

    plan = planner.create_plan(
        user_input="hello",
        directive=None,
        memory_results=None
    )

    # At least one verification step should exist
    assert any(
        "verify" in step.description.lower()
        or step.tool == "verify_tool"
        for step in plan.steps
    )
