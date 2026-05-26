from brain.c1.planner.adaptive_planner import AdaptivePlanner
from brain.c4.tools.registry import ToolRegistry
from brain.c1.planner.tool_schema import ToolSchema

def test_tool_aware_planning():
    tools = ToolRegistry()
    tools.register(
        "search",
        tool=lambda **k: None,
        schema=ToolSchema(
            name="search",
            description="search query",
            args={"query": "str"},
        )
    )

    planner = AdaptivePlanner(tools=tools)
    directive = type("D", (), {"mode": type("M", (), {"value": "normal"}), "schema": "tool_call"})

    plan = planner.create_plan("please search cats", directive)
    assert plan.steps[0].tool == "use_tool"
    assert plan.steps[0].args["tool"] == "search"
