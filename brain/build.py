from brain.router.dynamic_router import DynamicRouter
from brain.planner.adaptive_planner import AdaptivePlanner
from brain.executor.executor import Executor
from brain.tools.registry import ToolRegistry
from brain.tools.builtin.tool_x import SearchTool
from brain.tools.builtin.tool_y import EchoTool
from brain.memory.store import LocalMemoryStore
from brain.orchestrator import Orchestrator
from brain.state import BrainState


# ---------------------------------------------------------
# 1. Register tools
# ---------------------------------------------------------
def build_tool_registry() -> ToolRegistry:
    registry = ToolRegistry
    registry.register(SearchTool())
    registry.register(EchoTool())
    return registry


# ---------------------------------------------------------
# 2. Build memory store
# ---------------------------------------------------------
def build_memory_store() -> LocalMemoryStore:
    return LocalMemoryStore()


# ---------------------------------------------------------
# 3. Dummy LLM backend (replace with your real LLM)
# ---------------------------------------------------------
def llm_backend(prompt: str) -> str:
    return f"[LLM response to: {prompt}]"


# ---------------------------------------------------------
# 4. Build the executor
# ---------------------------------------------------------
def build_executor(tool_registry, memory_store) -> Executor:
    return Executor(
        tool_registry=tool_registry,
        memory_store=memory_store,
        llm=llm_backend,
    )


# ---------------------------------------------------------
# 5. Build router + planner
# ---------------------------------------------------------
def build_router() -> DynamicRouter:
    return DynamicRouter()


def build_planner() -> AdaptivePlanner:
    return AdaptivePlanner()


# ---------------------------------------------------------
# 6. Build orchestrator
# ---------------------------------------------------------
def build_orchestrator() -> Orchestrator:
    router = build_router()
    planner = build_planner()
    tools = build_tool_registry()
    memory = build_memory_store()
    executor = build_executor(tools, memory)

    return Orchestrator(
        router=router,
        planner=planner,
        executor=executor,
    )


# ---------------------------------------------------------
# 7. Public entrypoint: build a full C4 brain
# ---------------------------------------------------------
def build_brain():
    orchestrator = build_orchestrator()
    return orchestrator


# ---------------------------------------------------------
# 8. Convenience function: run the brain on input
# ---------------------------------------------------------
def run_brain(user_input: str):
    orchestrator = build_brain()
    state = BrainState(user_input)
    result = orchestrator.run(state)
    return result
