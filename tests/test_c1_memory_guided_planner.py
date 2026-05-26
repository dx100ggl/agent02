from brain.c1.planner.adaptive_planner import AdaptivePlanner
from brain.c4.tools.registry import ToolRegistry
from brain.c3.memory.store import MemoryItem

def test_memory_guided_planning():
    planner = AdaptivePlanner(tools=ToolRegistry())
    directive = type("D", (), {"mode": type("M", (), {"value": "normal"}), "schema": "llm"})

    memory_results = [
        MemoryItem(text="instruction: always be polite"),
        MemoryItem(text="past conversation about cats"),
    ]

    plan = planner.create_plan("hello", directive, memory_results=memory_results)
    assert "memory_context" in plan.meta
    assert any("instruction" in s.lower() for s in plan.meta["memory_context"])
