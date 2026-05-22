from brain.c2.executor.base import ExecutorBase
from brain.c4.tools.registry import ToolRegistry
from brain.c3.memory.store import MemoryStore
from brain.c1.state import BrainState

class Executor(ExecutorBase):
    def __init__(self, tool_registry: ToolRegistry, memory_store: MemoryStore, llm):
        self.tools = tool_registry
        self.memory = memory_store
        self.llm = llm

    def execute(self, step: dict, state: BrainState):
        action = step["action"]

        if action == "think":
            return {"thought": self.llm(state.user_input)}

        if action == "use_tool":
            tool = self.tools.get(step["tool"])
            return tool.run(**step.get("args", {}))

        if action == "query_memory":
            return self.memory.query(step["query"])

        raise ValueError(f"Unknown action: {action}")
