# brain/build.py

from __future__ import annotations
from typing import Optional

from brain.c1.state import State
from brain.c1.planner.adaptive_planner import AdaptivePlanner

from brain.c2.orchestrator import Orchestrator
from brain.c2.router.dynamic_router import DynamicRouter
from brain.c2.executor.executor import Executor

from brain.c3.memory.retriever import SimpleMemoryProvider

from brain.c4.tools.registry import ToolRegistry
from brain.c4.tools.builtin.search_memory_tool import SearchMemoryTool
from brain.c4.tools.builtin.write_memory_tool import WriteMemoryTool
from brain.c4.tools.dummy_llm import DummyLLMTool

from brain.c5.integration.c3_hooks import C3MemoryHooks

from brain.c2.skill_learning.skill_store import SkillStore
from brain.c2.skill_learning.skill_learner import SkillLearner
from brain.c2.skill_learning.skill_router import SkillRouter


# ---------------------------------------------------------
# Component builders
# ---------------------------------------------------------

def build_memory():
    """C3 memory provider façade."""
    return SimpleMemoryProvider()


def build_tools(memory):
    """
    Build the ToolRegistry with:
    - memory search tool
    - memory write tool
    - dummy LLM
    - lmstudio_llm (required by tests)
    """
    search_tool = SearchMemoryTool(memory=memory)
    write_tool = WriteMemoryTool(memory=memory)

    from brain.c4.tools.dummy_llm import DummyLLMTool
    from brain.llm.lmstudio_llm import LMStudioLLM

    dummy_llm = DummyLLMTool()
    lmstudio_llm = LMStudioLLM()

    tools = ToolRegistry()
    tools.register("search_memory", search_tool)
    tools.register("write_memory", write_tool)
    tools.register("dummy_llm", dummy_llm)
    tools.register("lmstudio_llm", lmstudio_llm)

    # 🔥 Required by test_s4_tool_registry_llm_defaults
    tools.default_llm = "lmstudio_llm"

    return tools


def build_router():
    return DynamicRouter()


def build_executor(tools, memory):
    return Executor(tools=tools, memory=memory)


def build_planner(llm_callable):
    return AdaptivePlanner(llm_callable=llm_callable)


def build_skill_store(memory) -> SkillStore:
    return SkillStore(memory)


def build_skill_learner(memory) -> SkillLearner:
    return SkillLearner(memory)


def build_skill_router(memory, planner) -> SkillRouter:
    store = build_skill_store(memory)
    return SkillRouter(store=store, planner=planner)


# ---------------------------------------------------------
# Main brain builder
# ---------------------------------------------------------

def build_brain(use_lmstudio: bool = False):
    """
    Build a complete Brain‑24 orchestrator instance.
    """

    # --- C3 Memory ---
    memory = build_memory()

    # --- C4 Tools ---
    tools = build_tools(memory)

    # # --- LLM callable for planner intent classification ---
    # llm_tool = tools.get(tools.default_llm)
    # Planner should use dummy_llm unless LM Studio is explicitly requested
    llm_tool = tools.get("dummy_llm") if not use_lmstudio else tools.get("lmstudio_llm")

    def llm_callable(prompt: str) -> str:
        raw = llm_tool.run({"text": prompt})
        if isinstance(raw, dict):
            return str(raw.get("text") or raw.get("output") or raw.get("response") or "")
        return str(raw)

    # --- C2 Planner / Router / Executor ---
    planner = build_planner(llm_callable)
    router = build_router()
    executor = build_executor(tools, memory)

    # --- C5 Reflection Hooks ---
    c3_hooks = C3MemoryHooks(memory)

    # --- C7 Skill Learning ---
    skill_learner = build_skill_learner(memory)
    skill_router = build_skill_router(memory, planner)

    # --- Orchestrator ---
    orchestrator = Orchestrator(
        router=router,
        planner=planner,
        executor=executor,
        tools=tools,
        memory=memory,
        c3_hooks=c3_hooks,
    )

    orchestrator.skill_learner = skill_learner
    orchestrator.skill_router = skill_router

    return orchestrator


# ---------------------------------------------------------
# Legacy API for test suite compatibility
# ---------------------------------------------------------

def run_brain(user_input: str):
    brain = build_brain()
    state = State(user_input)
    return brain.run(state)
