from brain.c2.executor.executor import Executor
from brain.c1.planner.plan import Plan
from brain.c4.tools.registry import ToolRegistry
from brain.c3.memory.store import MemoryStore

def test_executor_llm_step():
    class FakeLLM:
        def run(self, payload):
            return {"text": "hello world"}

    tools = ToolRegistry()
    tools.tools["llm"] = FakeLLM()
    tools.default_llm = "llm"

    executor = Executor(tools, MemoryStore())

    plan = Plan("hi")
    plan.add_step("LLM reasoning", tool="llm", args={"prompt": "hi"})

    out = executor.execute_plan(plan, state=type("S", (), {})())
    assert out == "hello world"
