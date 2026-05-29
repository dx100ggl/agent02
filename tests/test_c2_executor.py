# tests/test_c2_executor.py

from brain.c1.planner.plan import Plan
from brain.c2.executor.executor import Executor
from brain.c3.memory.retriever import SimpleMemoryProvider
from brain.c4.tools.registry import ToolRegistry

def test_executor_llm_step():
    class FakeLLM:
        def run(self, payload):
            return {"text": "hello world"}

    tools = ToolRegistry()
    tools.tools["llm"] = FakeLLM()
    tools.default_llm = "llm"

    executor = Executor(tools, SimpleMemoryProvider())

    plan = Plan("hi")
    plan.add_step("LLM reasoning", tool="llm", args={"prompt": "hi"})

    out = executor.execute_plan(plan, state=type("S", (), {})())
    assert out == "hello world"
