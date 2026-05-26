from brain.c4.tools.registry import ToolRegistry
from brain.c1.planner.tool_schema import ToolSchema

def test_tool_registry_schema():
    r = ToolRegistry()
    schema = ToolSchema(name="t", description="test", args={"x": "int"})
    r.register("t", tool=lambda **k: None, schema=schema)

    assert r.get_schema("t").args["x"] == "int"
    assert "t" in r.list_schemas()
