# brain/build.py

from __future__ import annotations

from typing import Optional

from brain.c1.state import State
from brain.c1.planner.adaptive_planner import AdaptivePlanner

from brain.c2.orchestrator import Orchestrator
from brain.c2.router.dynamic_router import DynamicRouter
from brain.c2.executor.executor import Executor
from brain.c2.meta_controller import MetaController
from brain.c2.meta_types import MetaConfig

from brain.c3.memory.retriever import SimpleMemoryProvider

from brain.c4.tools.registry import ToolRegistry
from brain.c4.tools.builtin.search_memory_tool import SearchMemoryTool
from brain.c4.tools.builtin.write_memory_tool import WriteMemoryTool

from brain.llm.lmstudio_llm import LMStudioLLM

from brain.c5.reflection_engine import ReflectionEngine
from brain.c5.trace_logger import TraceLogger
from brain.c5.integration.c3_hooks import C3MemoryHooks

from brain.c2.skill_learning.skill_store import SkillStore
from brain.c2.skill_learning.skill_learner import SkillLearner
from brain.c2.skill_learning.skill_router import SkillRouter


# ---------------------------------------------------------
# Component builders
# ---------------------------------------------------------

def build_memory():
    """
    S4: C3 memory is now a SimpleMemoryProvider façade
    (store + embeddings + retriever).
    """
    return SimpleMemoryProvider()


def build_tools(memory):
    """
    S4: ToolRegistry now receives a list of Tool instances.
    Memory tools are constructed here.
    """
    search_tool = SearchMemoryTool(memory=memory)
    write_tool = WriteMemoryTool(memory=memory)

    # LM Studio LLM tool (for planner + general use)
    lmstudio_llm = LMStudioLLM()

    return ToolRegistry([
        search_tool,
        write_tool,
        lmstudio_llm,
    ])


def build_router():
    return DynamicRouter()


def build_executor(tools, memory):
    """
    Executor now receives:
    - tool registry
    - memory provider
    """
    return Executor(tools=tools, memory=memory)


def build_planner(llm_callable):
    """
    AdaptivePlanner requires an llm_callable(prompt) -> str
    for intent classification.
    """
    return AdaptivePlanner(llm_callable=llm_callable)


def build_meta_controller(
    trace_logger: TraceLogger,
    reflection_engine: Optional[ReflectionEngine] = None,
    config: Optional[MetaConfig] = None,
) -> MetaController:
    return MetaController(
        trace_logger=trace_logger,
        reflection_engine=reflection_engine,
        config=config,
    )


def build_skill_store(memory) -> SkillStore:
    """
    C7 SkillStore: thin adapter over C3 memory provider.
    """
    return SkillStore(memory)


def build_skill_learner(memory) -> SkillLearner:
    """
    C7 SkillLearner: detect + generalize + persist skills from traces.
    """
    return SkillLearner(memory)


def build_skill_router(memory, planner) -> SkillRouter:
    """
    C7 SkillRouter: routes tasks via learned skills before falling back to planner.
    """
    store = build_skill_store(memory)
    return SkillRouter(store=store, planner=planner)


# ---------------------------------------------------------
# Main brain builder
# ---------------------------------------------------------

def build_brain(use_lmstudio: bool = False):
    """
    Build a complete Brain-24 instance.
    """

    # --- C3 Memory ---
    memory = build_memory()

    # --- C4 Tools ---
    tools = build_tools(memory)

    # --- LLM callable for planner intent classification ---
    lm = tools.get("lmstudio_llm")

    def llm_callable(prompt: str) -> str:
        """
        Planner uses this to classify intent.
        """
        result = lm.run(prompt)
        return result.get("answer", "")

    # --- C2 Planner / Router / Executor ---
    planner = build_planner(llm_callable if use_lmstudio else None)
    router = build_router()
    executor = build_executor(tools, memory)

    # --- C5 Reflection Hooks ---
    c3_hooks = C3MemoryHooks(memory)

    # --- C7 Skill Learning ---
    skill_learner = build_skill_learner(memory)
    skill_router = build_skill_router(memory, planner)

    # --- C2.5 Orchestrator ---
    orchestrator = Orchestrator(
        router=router,
        planner=planner,
        executor=executor,
        tools=tools,
        memory=memory,
        c3_hooks=c3_hooks,
    )

    # Attach Ch7 components
    orchestrator.skill_learner = skill_learner
    orchestrator.skill_router = skill_router

    return orchestrator


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
