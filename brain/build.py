# brain/build.py

from brain.c1.state import State
from brain.c2.orchestrator import Orchestrator
from brain.c2.planner.adaptive_planner import AdaptivePlanner
from brain.c2.router.dynamic_router import DynamicRouter
from brain.c2.executor.executor import Executor

from brain.c3.memory.store import MemoryStore
from brain.c4.tools.registry import ToolRegistry


# ---------------------------------------------------------
# Component builders
# ---------------------------------------------------------
def build_router():
    return DynamicRouter()


def build_planner():
    return AdaptivePlanner()


def build_memory_store():
    return MemoryStore()


def build_tool_registry():
    return ToolRegistry()


def build_executor(tools, memory):
    return Executor(tools=tools, memory=memory)


# ---------------------------------------------------------
# Main brain builder
# ---------------------------------------------------------
def build_brain(use_lmstudio: bool = False):
    """
    Build a complete Brain-24 instance.
    LM Studio is opt-in (REPL mode), tests remain unchanged.
    """

    router = build_router()
    planner = build_planner()
    tools = build_tool_registry()
    memory = build_memory_store()
    executor = build_executor(tools, memory)

    # Switch LLM backend if requested
    if use_lmstudio:
        tools.default_llm = "lmstudio_llm"

    return Orchestrator(
        router=router,
        planner=planner,
        executor=executor,
        tools=tools,
        memory=memory,
    )


# ---------------------------------------------------------
# Legacy API for test suite compatibility
# ---------------------------------------------------------
def run_brain(user_input: str):
    """
    Legacy wrapper expected by test_c4_smoke.py.
    Build a default brain and run a single turn.
    """
    brain = build_brain(use_lmstudio=False)
    state = State(user_input)
    return brain.run(state)
