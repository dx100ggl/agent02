# brain/build.py

from brain.c1.state import State
from brain.c2.orchestrator import Orchestrator
from brain.c2.planner.adaptive_planner import AdaptivePlanner
from brain.c2.router.dynamic_router import DynamicRouter
from brain.c2.executor.executor import Executor

from brain.c3.memory.store import MemoryStore
from brain.c4.tools.registry import ToolRegistry
from brain.c4.tools.builtin.lmstudio_llm import LMStudioLLM


# ---------------------------------------------------------
# Component builders
# ---------------------------------------------------------

def build_memory_store():
    return MemoryStore()


def build_tool_registry(memory):
    """
    ToolRegistry now requires memory so it can register:
    - write_memory
    - search_memory
    """
    return ToolRegistry(memory=memory)


def build_router():
    return DynamicRouter()


def build_executor(tools, memory):
    return Executor(tools=tools, memory=memory)


def build_planner(llm_callable):
    """
    AdaptivePlanner now requires an llm_callable(prompt) -> str
    for intent classification.
    """
    return AdaptivePlanner(llm_callable=llm_callable)


# ---------------------------------------------------------
# Main brain builder
# ---------------------------------------------------------

def build_brain(use_lmstudio: bool = False):
    """
    Build a complete Brain-24 instance.
    LM Studio is opt-in (REPL mode), tests remain unchanged.
    """

    # --- C3 Memory ---
    memory = build_memory_store()

    # --- C4 Tools (memory-aware) ---
    tools = build_tool_registry(memory)

    # --- LLM callable for planner intent classification ---
    lm_tool = tools.get("lmstudio_llm")

    def llm_callable(prompt: str) -> str:
        """
        Planner uses this to classify intent.
        We call the LMStudioLLM tool directly.
        """
        result = lm_tool.run(prompt)
        return result.get("answer", "")

    # --- C2 Planner / Router / Executor ---

    planner = AdaptivePlanner(llm_callable if use_lmstudio else None)

    router = build_router()
    executor = build_executor(tools, memory)

    # Switch LLM backend if requested
    if use_lmstudio:
        tools.default_llm = "lmstudio_llm"

    # --- C2.5 Orchestrator ---
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
